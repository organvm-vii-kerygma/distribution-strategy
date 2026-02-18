"""Mastodon engagement metrics pull-back.

Reads boost, favorite, and reply counts for distributed statuses.
Follows live/mock pattern from kerygma_social adapters.
"""
from __future__ import annotations

import json
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import Any


@dataclass
class MastodonMetricsConfig:
    instance_url: str
    access_token: str


class MastodonMetricsClient:
    def __init__(self, config: MastodonMetricsConfig, live: bool = False) -> None:
        self.config = config
        self._live = live

    def _get(self, path: str) -> dict[str, Any]:
        url = f"{self.config.instance_url}{path}"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {self.config.access_token}",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())

    def get_status_metrics(self, status_id: str) -> dict[str, int]:
        if not self._live:
            return {"reblogs_count": 0, "favourites_count": 0, "replies_count": 0}
        data = self._get(f"/api/v1/statuses/{status_id}")
        return {
            "reblogs_count": data.get("reblogs_count", 0),
            "favourites_count": data.get("favourites_count", 0),
            "replies_count": data.get("replies_count", 0),
        }

    def get_account_stats(self) -> dict[str, int]:
        if not self._live:
            return {"followers_count": 0, "following_count": 0, "statuses_count": 0}
        data = self._get("/api/v1/accounts/verify_credentials")
        return {
            "followers_count": data.get("followers_count", 0),
            "following_count": data.get("following_count", 0),
            "statuses_count": data.get("statuses_count", 0),
        }
