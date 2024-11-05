from player.radioplayer import RadioPlayer
from tools.config_browser import ConfigBrowser
from bt_monitor.bt_monitor import BtMonitor
import os
from time import sleep
import argparse

parser = argparse.ArgumentParser(
    description="This function is used to interact with the radioplayer"
)

parser.add_argument("--start", action="store_true")
parser.add_argument("--default-channel", type=str)
parser.add_argument("--exit", action="store_true")
parser.add_argument("--switch", type=str)
parser.add_argument("--monitor", action="store_true")

args = parser.parse_args()

if args.start:
    while True:
        try:
            player = RadioPlayer(data_port=ConfigBrowser.getConfig()["default port"])
            break
        except Exception:
            os.system("fuser -k 6996/tcp")
            sleep(5)
    player.start()

if args.default_channel:
    RadioPlayer.set_default_channel(args.default_channel)

if args.exit:
    RadioPlayer.send_command(
        data_port=ConfigBrowser.getConfig()["default port"], command="stop"
    )

if args.switch:
    channel = args.switch
    RadioPlayer.send_command(
        data_port=ConfigBrowser.getConfig()["default port"], command=f"switch {channel}"
    )

if args.monitor:
    monitor = BtMonitor(main_file_path=os.path.abspath(__file__))
    monitor.run()
