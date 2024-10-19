import requests
from bs4 import BeautifulSoup
import re
import json
from tools.config_browser import ConfigBrowser
from concurrent.futures import ThreadPoolExecutor


class WebRadioScraper:
    @staticmethod
    def fetchMediaIDs() -> dict:
        """
        Fetch the titles and mediaIds for each channel specified in the config.json-file

        Returns:
            dict: Dictionary where channel titles are keys and mediaIds are values
        """
        channels = ConfigBrowser.getConfig()["channels"]

        mediaIds = {}

        url = "https://www.supla.fi/radiosuomipop"
        try:
            soup = BeautifulSoup(requests.get(url).text, "html.parser")
            scripts = soup.find_all("script")
        except Exception as e:
            print(e)

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

    @staticmethod
    def fetchM3U8url(url: str) -> tuple:
        """
        Fetch .m3u8 -url for specific channel

        Args:
            url (str): Url to the website which contains the .m3u8 -url

        Returns:
            tuple: Channel name and it's .m3u8 -url
        """
        try:
            data = json.loads(requests.get(url).text)
        except Exception as e:
            print(e)
            return "Error", "Error"

        try:
            channel = data["clip"]["metadata"]["channelName"]
            m3u8url = data["clip"]["playback"]["media"]["streamUrls"]["audioHls"]["url"]
        except Exception as e:
            print(e)
            return "Error", "Error"

        return channel, m3u8url

    @staticmethod
    def refreshM3U8Urls():
        """
        Refresh .m3u8 -urls for all channels specified in the config.json -file and update the urls to the config
        """
        m3u8Urls = {}
        mediaIds = WebRadioScraper.fetchMediaIDs()

        base_url = "https://mcc.nm-ovp.nelonenmedia.fi/v2/media/"
        urls = []
        for mediaId in mediaIds.values():
            urls.append(base_url + mediaId)

        with ThreadPoolExecutor(max_workers=len(urls)) as executor:
            tasks = {
                executor.submit(WebRadioScraper.fetchM3U8url, url): url for url in urls
            }
            for task in tasks:
                channel, m3u8url = task.result()
                m3u8Urls[channel] = m3u8url

        config = ConfigBrowser.getConfig()
        config["m3u8Urls"] = m3u8Urls
        ConfigBrowser.updateConfig(config)
