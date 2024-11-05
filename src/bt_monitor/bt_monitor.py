from pydbus import SystemBus
from gi.repository import GLib
from tools.config_browser import ConfigBrowser
import subprocess
import os
from threading import Lock


class BtMonitor:
    def __init__(self, main_file_path: str) -> None:
        self.__main_file_path = main_file_path
        self.__connect_lock = Lock()
        self.__disconnect_lock = Lock()
        self.__disconnect_lock.acquire()

    def state_changed(self, iface, changed, invalidated):
        if changed["Connected"]:
            if not self.__connect_lock.acquire(blocking=False):
                return
            try:
                if self.__disconnect_lock.locked():
                    self.__disconnect_lock.release()
            except Exception as e:
                print(e)

        else:
            if not self.__disconnect_lock.acquire(blocking=False):
                return
            try:
                if self.__connect_lock.locked():
                    self.__connect_lock.release()
            except Exception as e:
                print(e)
        
        arg = "--start" if changed["Connected"] else "--exit"

        subprocess.Popen(
            [
                "python",
                self.__main_file_path,
                arg,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            close_fds=True,
            preexec_fn=os.setpgrp,
        )

    def run(self):
        bus = SystemBus()

        device = bus.get(
            "org.bluez",
            f"/org/bluez/hci0/dev_{ConfigBrowser.getConfig()['playback device'].replace(':', '_')}",
        )
        device.onPropertiesChanged = self.state_changed

        GLib.MainLoop().run()
