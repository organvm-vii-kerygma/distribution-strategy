"""Tests for Mastodon engagement metrics pull-back."""
from kerygma_strategy.mastodon_metrics import MastodonMetricsClient, MastodonMetricsConfig


class TestMastodonMetrics:
    def _client(self):
        return MastodonMetricsClient(
            MastodonMetricsConfig(instance_url="https://mastodon.social", access_token="test")
        )

    def test_mock_get_status_metrics(self):
        client = self._client()
        metrics = client.get_status_metrics("12345")
        assert "reblogs_count" in metrics
        assert "favourites_count" in metrics
        assert "replies_count" in metrics

    def test_mock_get_account_stats(self):
        client = self._client()
        stats = client.get_account_stats()
        assert "followers_count" in stats
        assert "statuses_count" in stats

    def test_config_defaults(self):
        config = MastodonMetricsConfig(instance_url="https://x.com", access_token="t")
        assert config.instance_url == "https://x.com"

    def test_mock_metrics_are_zero(self):
        client = self._client()
        metrics = client.get_status_metrics("any-id")
        assert all(v == 0 for v in metrics.values())
