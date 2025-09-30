import requests

from utils.logger import logger


class APIClient:
    def get(self, url, params=None, headers=None):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API error: {e}")
            return None
        cookbook_panel = getattr(self.app, "cookbook_panel", None)
        if cookbook_panel and hasattr(cookbook_panel, "print_recipe"):
            cookbook_panel.print_recipe(rid)
        else:
            self.show_error("Error", "Cookbook panel not found or does not support printing.")
