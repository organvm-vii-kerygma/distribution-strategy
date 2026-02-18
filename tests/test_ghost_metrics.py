"""Tests for Ghost CMS engagement metrics pull-back."""
from kerygma_strategy.ghost_metrics import GhostMetricsClient, GhostMetricsConfig


class TestGhostMetrics:
    def _client(self):
        return GhostMetricsClient(
            GhostMetricsConfig(
                api_url="https://ghost.example.com",
                admin_api_key="abc123:deadbeef0102030405060708090a0b0c0d0e0f101112131415161718191a1b",  # allow-secret — test fixture
            )
        )

    def test_mock_site_metrics(self):
        client = self._client()
        metrics = client.get_site_metrics()
        assert "total_posts" in metrics
        assert "total_members" in metrics
        assert "email_open_rate" in metrics

    def test_mock_metrics_are_zero(self):
        client = self._client()
        metrics = client.get_site_metrics()
        assert metrics["total_posts"] == 0
        assert metrics["total_members"] == 0
        assert metrics["email_open_rate"] == 0.0

    def test_mock_post_count(self):
        client = self._client()
        assert client.get_post_count() == 0

    def test_config_defaults(self):
        config = GhostMetricsConfig(
            api_url="https://x.com",
            admin_api_key="a:b",
        )
        assert config.content_api_key == ""
