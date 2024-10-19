import requests
from bs4 import BeautifulSoup
import re
import json
from secret import config_path


class WebRadioScraper:
    @staticmethod
    def fetchMediaIDs() -> dict:
        with open(config_path) as config_file:
            config = json.loads(config_file.read())
            channels = config["channels"]
        
        mediaIds = {}
        
        url = "https://www.supla.fi/radiosuomipop"
        response = requests.get(url)

        soup = BeautifulSoup(response.text, "html.parser")
        scripts = soup.find_all("script")

        pattern = re.compile(r'"title":"(.*?)",*?"mediaId":"(\d+)"')

        for script in scripts:
            if script.string:
                cleaned = script.string.replace("\\", "")
                matches = pattern.findall(cleaned)
                for match in matches:
                    title, mediaId = match
                    if title in channels:
                        mediaIds[title] = mediaId

        return mediaIds
