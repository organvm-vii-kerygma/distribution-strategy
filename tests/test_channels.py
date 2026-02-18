"""Tests for the channels module."""
from kerygma_strategy.channels import ChannelRegistry, ChannelConfig

def test_register_and_retrieve_channel():
    reg = ChannelRegistry()
    reg.register(ChannelConfig(channel_id="ch1", name="Mastodon", platform="mastodon", endpoint="https://mastodon.social"))
    ch = reg.get("ch1")
    assert ch.name == "Mastodon"

def test_get_enabled_channels():
    reg = ChannelRegistry()
    reg.register(ChannelConfig(channel_id="ch1", name="A", platform="mastodon", endpoint="url1"))
    reg.register(ChannelConfig(channel_id="ch2", name="B", platform="discord", endpoint="url2", enabled=False))
    enabled = reg.get_enabled()
    assert len(enabled) == 1

def test_format_content_with_limit():
    ch = ChannelConfig(channel_id="ch1", name="Mastodon", platform="mastodon", endpoint="url", max_length=50)
    text = ch.format_content("Title", "This is a long body that should get truncated", "https://example.com")
    assert len(text) <= 50

def test_get_by_platform():
    reg = ChannelRegistry()
    reg.register(ChannelConfig(channel_id="ch1", name="A", platform="mastodon", endpoint="url1"))
    reg.register(ChannelConfig(channel_id="ch2", name="B", platform="discord", endpoint="url2"))
    mastodon_channels = reg.get_by_platform("mastodon")
    assert len(mastodon_channels) == 1
