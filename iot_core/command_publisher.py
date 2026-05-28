from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

import paho.mqtt.client as mqtt

from iot_core.settings import load_settings


ALLOWED_COMMANDS = {
    "status": "status",
    "light:on": "light:on",
    "light:off": "light:off",
    "mode:auto": "mode:auto",
}


@dataclass(frozen=True)
class PublishResult:
    ok: bool
    topic: str
    payload: str
    message: str


def command_topic_for_device(device_id: str = "esp32_01") -> str:
    settings = load_settings()
    devices = settings.devices_config.get("devices", [])
    device = next((item for item in devices if item.get("device_id") == device_id), None)

    if device is None:
        raise ValueError(f"Device nao encontrado em configs/devices.yaml: {device_id}")

    return (
        f"mackenzie/iot/v1/{device['site']}/{device['area']}/"
        f"{device['domain']}/{device['device_id']}/commands"
    )


def publish_command(command: str, device_id: str = "esp32_01", timeout: float = 5.0) -> PublishResult:
    payload = ALLOWED_COMMANDS.get(command)
    if payload is None:
        return PublishResult(False, "", command, f"Comando nao suportado: {command}")

    try:
        settings = load_settings()
        topic = command_topic_for_device(device_id)
    except Exception as exc:
        return PublishResult(False, "", payload, f"Falha ao carregar configuracao MQTT: {exc}")

    client_id = f"obj-conect-dashboard-{uuid4().hex[:8]}"
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    connected = False
    loop_started = False

    try:
        rc = client.connect(settings.mqtt.host, settings.mqtt.port, settings.mqtt.keepalive)
        if rc != mqtt.MQTT_ERR_SUCCESS:
            return PublishResult(False, topic, payload, f"Falha ao conectar no broker MQTT. rc={rc}")

        connected = True
        client.loop_start()
        loop_started = True
        info = client.publish(topic, payload=payload, qos=settings.mqtt.qos)
        info.wait_for_publish(timeout=timeout)

        if not info.is_published():
            return PublishResult(
                False,
                topic,
                payload,
                f"Timeout ao publicar comando MQTT em {timeout:.0f}s.",
            )

        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            return PublishResult(False, topic, payload, f"Falha MQTT ao publicar. rc={info.rc}")

        return PublishResult(True, topic, payload, "Comando publicado no broker MQTT.")
    except Exception as exc:
        return PublishResult(False, topic if "topic" in locals() else "", payload, f"Erro ao publicar MQTT: {exc}")
    finally:
        if loop_started:
            client.loop_stop()
        if connected:
            client.disconnect()
