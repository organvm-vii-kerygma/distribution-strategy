"""Tests for channels YAML loading/saving."""

from pathlib import Path

from kerygma_strategy.channels import ChannelRegistry, ChannelConfig

FIXTURES = Path(__file__).parent / "fixtures"


class TestChannelsYaml:
    def test_from_yaml(self):
        reg = ChannelRegistry.from_yaml(FIXTURES / "sample_channels.yaml")
        assert reg.total_channels == 3

    def test_from_yaml_enabled(self):
        reg = ChannelRegistry.from_yaml(FIXTURES / "sample_channels.yaml")
        enabled = reg.get_enabled()
        assert len(enabled) == 2

    def test_to_yaml(self, tmp_path):
        reg = ChannelRegistry()
        reg.register(ChannelConfig(
            channel_id="test", name="Test", platform="mastodon",
            endpoint="https://example.com", max_length=500,
        ))
        out = tmp_path / "channels.yaml"
        reg.to_yaml(out)
        assert out.exists()

        reg2 = ChannelRegistry.from_yaml(out)
        assert reg2.total_channels == 1
        assert reg2.get("test").platform == "mastodon"

    def test_roundtrip(self, tmp_path):
        reg = ChannelRegistry.from_yaml(FIXTURES / "sample_channels.yaml")
        out = tmp_path / "roundtrip.yaml"
        reg.to_yaml(out)
        reg2 = ChannelRegistry.from_yaml(out)
        assert reg2.total_channels == reg.total_channels
