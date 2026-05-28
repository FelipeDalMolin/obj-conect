from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from iot_core.topics import ParsedTopic, parse_topic


SCHEMA_VERSION = "0.2.0"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def decode_payload(payload_bytes: bytes) -> tuple[Any, bool, str | None, str]:
    payload_raw = payload_bytes.decode("utf-8", errors="replace")

    try:
        payload = json.loads(payload_raw)
    except json.JSONDecodeError as exc:
        return None, False, f"invalid_json: {exc.msg}", payload_raw

    return payload, True, None, payload_raw


def build_message_record(topic: str, payload_bytes: bytes, received_at: str | None = None) -> dict[str, Any]:
    received_at = received_at or utc_now_iso()
    parsed_topic, topic_error = parse_topic(topic)
    payload, payload_valid, payload_error, payload_raw = decode_payload(payload_bytes)

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
