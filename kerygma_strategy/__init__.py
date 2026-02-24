"""distribution-strategy: Content scheduling, multi-channel distribution, and analytics.

Part of ORGAN VII (Kerygma) — the marketing and distribution layer
of the eight-organ creative-institutional system.
"""

__version__ = "0.2.0"

from kerygma_strategy.analytics import AnalyticsCollector, EngagementMetric
from kerygma_strategy.channels import ChannelConfig, ChannelRegistry
from kerygma_strategy.scheduler import ContentScheduler, ScheduleEntry, Frequency
from kerygma_strategy.persistence import JsonStore

__all__ = [
    "AnalyticsCollector",
    "EngagementMetric",
    "ChannelConfig",
    "ChannelRegistry",
    "ContentScheduler",
    "ScheduleEntry",
    "Frequency",
    "JsonStore",
]
