from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from iot_core.topics import ParsedTopic, parse_topic


SCHEMA_VERSION = "0.2.0"
TEXT_COMMANDS = {
    "status": {"command": "status"},
    "light:on": {"command": "set_light", "state": "on"},
    "light:off": {"command": "set_light", "state": "off"},
    "mode:auto": {"command": "set_mode", "mode": "auto"},
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def decode_payload(payload_bytes: bytes, channel: str | None = None) -> tuple[Any, bool, str | None, str, str]:
    payload_raw = payload_bytes.decode("utf-8", errors="replace")

    try:
        payload = json.loads(payload_raw)
    except json.JSONDecodeError as exc:
        if channel == "commands":
            command_payload = TEXT_COMMANDS.get(payload_raw.strip().lower())
            if command_payload is not None:
                return command_payload, True, None, payload_raw, "text_command"

            return None, False, "invalid_command", payload_raw, "text"

        return None, False, f"invalid_json: {exc.msg}", payload_raw, "text"

    return payload, True, None, payload_raw, "json"


def build_message_record(topic: str, payload_bytes: bytes, received_at: str | None = None) -> dict[str, Any]:
    received_at = received_at or utc_now_iso()
    parsed_topic, topic_error = parse_topic(topic)
    channel = parsed_topic.channel if parsed_topic is not None else None
    payload, payload_valid, payload_error, payload_raw, payload_format = decode_payload(payload_bytes, channel)

    record: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "received_at": received_at,
        "topic": topic,
        "topic_valid": topic_error is None,
        "topic_error": topic_error,
        "site": None,
        "area": None,
        "domain": None,
        "device_id": None,
        "channel": None,
        "payload": payload,
        "payload_valid": payload_valid,
        "payload_format": payload_format,
        "payload_error": payload_error,
        "payload_raw": payload_raw,
    }

    if parsed_topic is not None:
        add_topic_fields(record, parsed_topic)

    if isinstance(payload, dict):
        for key, value in payload.items():
            record.setdefault(key, value)

    return record


def add_topic_fields(record: dict[str, Any], parsed_topic: ParsedTopic) -> None:
    record["site"] = parsed_topic.site
    record["area"] = parsed_topic.area
    record["domain"] = parsed_topic.domain
    record["device_id"] = parsed_topic.device_id
    record["channel"] = parsed_topic.channel
