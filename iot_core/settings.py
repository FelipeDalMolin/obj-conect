from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


@dataclass(frozen=True)
class MqttSettings:
    broker_name: str
    host: str
    port: int
    client_id: str
    keepalive: int
    qos: int
    subscribe_topic: str
    debug_topic: str


@dataclass(frozen=True)
class StorageSettings:
    data_db_path: Path
    config_db_path: Path
    raw_dir: Path
    exports_dir: Path


@dataclass(frozen=True)
class AppSettings:
    project_root: Path
    mqtt: MqttSettings
    storage: StorageSettings
    mqtt_config: dict[str, Any]
    devices_config: dict[str, Any]
    environments_config: dict[str, Any]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Arquivo YAML invalido: {path}")

    return data


def load_settings(root: Path | None = None) -> AppSettings:
    root = root or project_root()
    load_dotenv(root / ".env")

    mqtt_config = load_yaml(root / "configs" / "mqtt.yaml")
    devices_config = load_yaml(root / "configs" / "devices.yaml")
    environments_config = load_yaml(root / "configs" / "environments.yaml")

    mqtt_section = mqtt_config.get("mqtt", {})
    broker = mqtt_section.get("broker", {})
    client = mqtt_section.get("client", {})
    topics = mqtt_section.get("topics", {})

    mqtt_settings = MqttSettings(
        broker_name=str(broker.get("name", "HiveMQ Public Broker")),
        host=os.getenv("MQTT_HOST", str(broker.get("host", "broker.hivemq.com"))),
        port=int(os.getenv("MQTT_PORT", broker.get("port", 1883))),
        client_id=os.getenv("MQTT_CLIENT_ID", str(client.get("client_id", "obj-conect-collector"))),
        keepalive=int(os.getenv("MQTT_KEEPALIVE", client.get("keepalive", 60))),
        qos=int(os.getenv("MQTT_QOS", client.get("qos", 0))),
        subscribe_topic=os.getenv(
            "MQTT_SUBSCRIBE_TOPIC",
            str(topics.get("subscribe", "mackenzie/iot/v1/campus01/lab01/lighting/+/+")),
        ),
        debug_topic=str(topics.get("debug", "mackenzie/iot/v1/campus01/lab01/lighting/+/#")),
    )

    active_environment = environments_config.get("active_environment", "local")
    environments = environments_config.get("environments", [])
    environment = next(
        (item for item in environments if item.get("name") == active_environment),
        environments[0] if environments else {},
    )

    storage_settings = StorageSettings(
        data_db_path=root / str(environment.get("data_db", "data/local/iot_data.json")),
        config_db_path=root / str(environment.get("config_db", "data/local/iot_config.json")),
        raw_dir=root / str(environment.get("raw_dir", "data/raw")),
        exports_dir=root / str(environment.get("exports_dir", "data/exports")),
    )

    return AppSettings(
        project_root=root,
        mqtt=mqtt_settings,
        storage=storage_settings,
        mqtt_config=mqtt_config,
        devices_config=devices_config,
        environments_config=environments_config,
    )
