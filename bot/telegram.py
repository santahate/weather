from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class TelegramClient:
    def __init__(self, token: str, chat_id: str | int) -> None:
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"

    def _request(self, method: str, params: dict, files: Optional[dict] = None):
        url = f"{self.base_url}/{method}"
        logger.debug("Telegram %s: %s", method, params)
        resp = requests.post(url, params=params, files=files, timeout=10) if files else requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def send_message(self, text: str) -> None:
        self._request("sendMessage", {"chat_id": self.chat_id, "text": text})

    def send_photo(self, photo_path: Path, caption: str | None = None) -> None:
        with open(photo_path, "rb") as img:
            self._request(
                "sendPhoto",
                {"chat_id": self.chat_id, "caption": caption} if caption else {"chat_id": self.chat_id},
                files={"photo": img},
            )
