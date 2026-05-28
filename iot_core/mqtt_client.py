from __future__ import annotations

import signal
from dataclasses import dataclass

import paho.mqtt.client as mqtt

from iot_core.models import build_message_record
from iot_core.settings import MqttSettings
from iot_core.storage_tinydb import TinyDBStorage


@dataclass
class CollectorRuntime:
    message_limit: int = 0
    messages_seen: int = 0
    stopping: bool = False


class MqttCollectorClient:
    def __init__(
        self,
        mqtt_settings: MqttSettings,
        storage: TinyDBStorage,
        subscribe_topic: str | None = None,
        message_limit: int = 0,
    ) -> None:
        self.settings = mqtt_settings
        self.storage = storage
        self.subscribe_topic = subscribe_topic or mqtt_settings.subscribe_topic
        self.runtime = CollectorRuntime(message_limit=message_limit)
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=mqtt_settings.client_id,
        )
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_subscribe = self._on_subscribe
        self.client.on_message = self._on_message

    def run_forever(self) -> None:
        self._install_signal_handlers()
        print(
            "MQTT COLLECTOR CONNECT "
            f"broker={self.settings.broker_name} "
            f"host={self.settings.host} "
            f"port={self.settings.port} "
            f"client_id={self.settings.client_id}"
        )
        print(f"MQTT COLLECTOR SUBSCRIBE topic={self.subscribe_topic}")
        self.client.connect(self.settings.host, self.settings.port, self.settings.keepalive)
        self.client.loop_forever()

    def stop(self) -> None:
        if self.runtime.stopping:
            return
        self.runtime.stopping = True
        self.client.disconnect()

    def _install_signal_handlers(self) -> None:
        def _handle_stop(_signum: int, _frame: object) -> None:
            print("MQTT COLLECTOR STOP requested")
            self.stop()

        signal.signal(signal.SIGINT, _handle_stop)
        signal.signal(signal.SIGTERM, _handle_stop)

    def _on_connect(self, client: mqtt.Client, _userdata: object, _flags: object, reason_code: object, _properties: object) -> None:
        if getattr(reason_code, "is_failure", False):
            print(f"MQTT COLLECTOR CONNECT FAIL reason={reason_code}")
            return

        print(f"MQTT COLLECTOR CONNECT OK reason={reason_code}")
        client.subscribe(self.subscribe_topic, qos=self.settings.qos)

    def _on_disconnect(
        self,
        _client: mqtt.Client,
        _userdata: object,
        _disconnect_flags: object,
        reason_code: object,
        _properties: object,
    ) -> None:
        print(f"MQTT COLLECTOR DISCONNECT reason={reason_code}")

    def _on_subscribe(
        self,
        _client: mqtt.Client,
        _userdata: object,
        message_id: int,
        reason_code_list: list[object],
        _properties: object,
    ) -> None:
        print(f"MQTT COLLECTOR SUBSCRIBE OK mid={message_id} reason_codes={reason_code_list}")

    def _on_message(self, client: mqtt.Client, _userdata: object, message: mqtt.MQTTMessage) -> None:
        record = build_message_record(message.topic, message.payload)
        stored_table = self.storage.store_message(record)

        print(
            "MQTT COLLECTOR MESSAGE "
            f"topic={message.topic} "
            f"channel={record.get('channel')} "
            f"payload_valid={record.get('payload_valid')} "
            f"topic_valid={record.get('topic_valid')} "
            f"stored={stored_table}"
        )

        self.runtime.messages_seen += 1
        if self.runtime.message_limit > 0 and self.runtime.messages_seen >= self.runtime.message_limit:
            print(f"MQTT COLLECTOR MESSAGE LIMIT reached={self.runtime.messages_seen}")
            client.disconnect()
