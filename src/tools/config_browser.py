from secret import config_path
import json


class ConfigBrowser:
    @staticmethod
    def updateConfig(config: dict):
        """
        Updates the config-file with the given dict

        Args:
            config (dict): The dict which is saved to the config.json
        """
        try:
            with open(config_path, "w") as config_file:
                json.dump(config, config_file, indent=4, ensure_ascii=False)
        except Exception as e:
            print(e)

    @staticmethod
    def getConfig() -> dict:
        """
        Returns the config.json-file as dict

        Returns:
            dict: config.json converted to dictionary
        """
        try:
            with open(config_path, "r") as config_file:
                return json.loads(config_file.read())
        except Exception as e:
            print(e)
            return {"Error", True}
