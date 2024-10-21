from tools.config_browser import ConfigBrowser
from scraper.webscraper import WebRadioScraper
import socket
import vlc
from threading import Event, Thread
from time import sleep
from enum import Enum


class RadioPlayer:

    class RadioPlayerError(Enum):
        ERROR = "error"
        ENDED = "ended"

    def __init__(self, data_port) -> None:
        self.__config = ConfigBrowser.getConfig()

        self.__vlc_instance = vlc.Instance()
        self.__vlc_player = self.__vlc_instance.media_player_new()
        self.__vlc_player.event_manager().event_attach(
            vlc.EventType.MediaPlayerEncounteredError,
            self.__on_error,
            RadioPlayer.RadioPlayerError.ERROR,
        )
        self.__vlc_player.event_manager().event_attach(
            vlc.EventType.MediaPlayerEndReached,
            self.__on_error,
            RadioPlayer.RadioPlayerError.ENDED,
        )

        self.__current_channel = self.__config["default channel"]

        self.__data_port = data_port
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind(("localhost", self.__data_port))
        self.__server.listen()

        self.__close_main_loop = False
        self.__end_event = Event()
        self.__switch_event = Event()

        self.__error_count = 0

    def start(self) -> None:
        media = self.__vlc_instance.media_new(
            self.__config["m3u8Urls"][self.__current_channel]
        )
        self.__vlc_player.set_media(media)
        self.__close_main_loop = False
        self.__end_event.clear()
        restart = False

        self.__vlc_player.play()

        while not self.__close_main_loop:
            connection, address = self.__server.accept()
            if address[0] != "127.0.0.1":
                continue
            with connection:
                data = connection.recv(1024).decode().strip().split(" ")
                match data[0]:
                    case "stop":
                        self.__stop()

                    case "restart":
                        restart = True
                        break

                    case "switch":
                        thread = Thread(
                            target=self.__switch_channel, args=[" ".join(data[1:])]
                        )
                        thread.daemon = False
                        thread.start()
                        self.__switch_event.wait()
                        self.__switch_event.clear()

                    case "exit":
                        self.__exit()

        self.__end_event.set()

        if restart:
            self.start()

    def __stop(self) -> None:
        self.__vlc_player.stop()
        self.__close_main_loop = True

    def __on_error(self, event, error: RadioPlayerError):
        if error == RadioPlayer.RadioPlayerError.ERROR and self.__error_count != 5:
            sleep(2)
            self.__error_count += 1
            self.__send_command("restart")
            return

        if error == RadioPlayer.RadioPlayerError.ERROR:
            self.__error_count = 0

        WebRadioScraper.refreshM3U8Urls()
        self.__config = ConfigBrowser.getConfig()

        self.__send_command("restart")

    def __exit(self) -> None:
        self.__stop()
        self.__server.close()

    def __send_command(self, command: str) -> None:
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temp_socket.connect(("localhost", self.__data_port))
        temp_socket.send(command.encode())
        temp_socket.close()

    def __switch_channel(self, channel: str) -> None:
        if channel not in self.__config["channels"]:
            self.__switch_event.set()
            return

        self.__stop()
        self.__switch_event.set()

        self.__end_event.wait()
        self.__end_event.clear()

        self.__current_channel = channel

        self.start()
    
    def set_default_channel(self, channel: str) -> None:
        if channel in self.__config["channels"]:
            self.__config["default channel"] = channel
            ConfigBrowser.updateConfig(self.__config)
