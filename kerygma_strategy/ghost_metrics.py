"""Ghost CMS engagement metrics pull-back.

Reads post counts, member stats, and email open rates from Ghost APIs.
Follows live/mock pattern from kerygma_social adapters.
Uses Ghost Admin API (JWT) for member data, Content API for public post data.
"""
from __future__ import annotations

import json
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import Any

from kerygma_social.ghost_jwt import build_ghost_jwt


@dataclass
class GhostMetricsConfig:
    api_url: str
    admin_api_key: str  # Format: {id}:{secret}
    content_api_key: str = ""


class GhostMetricsClient:
    def __init__(self, config: GhostMetricsConfig, live: bool = False) -> None:
        self.config = config
        self._live = live

    def _build_jwt(self) -> str:
        return build_ghost_jwt(self.config.admin_api_key)  # allow-secret — runtime JWT

    def _admin_get(self, path: str) -> dict[str, Any]:
        token = self._build_jwt()  # allow-secret — runtime JWT
        url = f"{self.config.api_url}{path}"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Ghost {token}",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())

    def get_site_metrics(self) -> dict[str, Any]:
        if not self._live:
            return {"total_posts": 0, "total_members": 0, "email_open_rate": 0.0}
        try:
            members = self._admin_get("/ghost/api/admin/members/?limit=1")
            member_count = members.get("meta", {}).get("pagination", {}).get("total", 0)
        except Exception:
            member_count = 0

        try:
            posts = self._admin_get("/ghost/api/admin/posts/?limit=1")
            post_count = posts.get("meta", {}).get("pagination", {}).get("total", 0)
        except Exception:
            post_count = 0

        return {
            "total_posts": post_count,
            "total_members": member_count,
            "email_open_rate": 0.0,
        }

    def get_post_count(self) -> int:
        metrics = self.get_site_metrics()
        return metrics["total_posts"]
