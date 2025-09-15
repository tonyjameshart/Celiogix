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