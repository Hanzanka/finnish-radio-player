# finnish-radio-player
Used to play finnish radio channels

## Required Software
- pulseaudio
- bluez

## Required Libraries
- pydbus
- GLib
- VLC-python
- BeautifulSoup4

## Installation
For me because theres no change remembering all this
### Clone The Repo:
```bash
git clone https://github.com/Hanzanka/finnish-radio-player.git
```
### Connect Wanted Bluetooth Device:
```bash
bluetoothctl
scan on
pair MAC
connect MAC
trust MAC
```
### Save The MAC-Address To The config.json-File:
```json
"playback device": "XX:XX:XX:XX:XX:XX"
```
### Create A User Service:
Create a .service -file:
```bash
mkdir -p ~/.config/systemd/user
nano ~/.config/systemd/user/radio.service
```
Put these lines into the file:
```
[Unit]
Description=Radio Player Service
After=network.target

[Service]
Environment="PULSE_SERVER=unix:/run/user/1000/pulse/native"
ExecStart=/usr/bin/python [path to the radio.py -file] --monitor
StandardOutput=append:[Path where output is saved]
StandardError=append:[Path where errors are saved]
Restart=always

[Install]
WantedBy=default.target
```
Reload User Systemd Daemon:
```bash
systemctl --user daemon-reload
```
Enable the service:
```bash
systemctl --user enable radio.service
```
Start the service:
```bash
systemctl --user start radio.service
```
Check if the service is running:
```bash
systemctl --user status radio.service
```
Enable user lingering (IDK this didn't work before using this)
```
sudo loginctl enable-linger [username]
```
### There may appear errors when going though the installation steps (And there is maybe other things needed to be configured that i didn't remember here)