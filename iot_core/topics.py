from __future__ import annotations

from dataclasses import dataclass


MQTT_PREFIX = ("mackenzie", "iot", "v1")
SUPPORTED_CHANNELS = {"telemetry", "events", "status", "commands"}
CHANNEL_TABLES = {
    "telemetry": "telemetry",
    "events": "events",
    "status": "status",
    "commands": "commands",
}


@dataclass(frozen=True)
class ParsedTopic:
    site: str
    area: str
    domain: str
    device_id: str
    channel: str

    @property
    def channel_supported(self) -> bool:
        return self.channel in SUPPORTED_CHANNELS

    @property
    def table_name(self) -> str | None:
        return CHANNEL_TABLES.get(self.channel)


def parse_topic(topic: str) -> tuple[ParsedTopic | None, str | None]:
    parts = topic.split("/")

    if len(parts) != 8:
        return None, "invalid_topic_segment_count"

    if tuple(parts[:3]) != MQTT_PREFIX:
        return None, "invalid_topic_prefix"

    site, area, domain, device_id, channel = parts[3:]
    if not all((site, area, domain, device_id, channel)):
        return None, "invalid_topic_empty_segment"

    parsed = ParsedTopic(
        site=site,
        area=area,
        domain=domain,
        device_id=device_id,
        channel=channel,
    )

    if not parsed.channel_supported:
        return parsed, "unsupported_channel"

    return parsed, None
