from player.radioplayer import RadioPlayer
from tools.config_browser import ConfigBrowser
import argparse

parser = argparse.ArgumentParser(
    description="This function is used to interact with the radioplayer"
)

parser.add_argument("--start", action="store_true")
parser.add_argument("--default-channel", type=str)
parser.add_argument("--exit", action="store_true")
parser.add_argument("--switch", type=str)

args = parser.parse_args()

if args.start:
    player = RadioPlayer(data_port=ConfigBrowser.getConfig()["default port"])
    player.start()

if args.default_channel:
    RadioPlayer.set_default_channel(args.default_channel)

if args.exit:
    RadioPlayer.send_command(data_port=ConfigBrowser.getConfig()["default port"], command="stop")

if args.switch:
    channel = args.switch
    RadioPlayer.send_command(data_port=ConfigBrowser.getConfig()["default port"], command=f"switch {channel}")
