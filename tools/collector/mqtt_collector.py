from __future__ import annotations

import argparse

from iot_core.mqtt_client import MqttCollectorClient
from iot_core.settings import load_settings
from iot_core.storage_tinydb import TinyDBStorage


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect MQTT messages and store them in TinyDB.")
    parser.add_argument("--topic", help="Override the configured MQTT subscription topic.")
    parser.add_argument(
        "--message-limit",
        type=int,
        default=0,
        help="Stop after N messages. Use 0 to run until Ctrl+C.",
    )
    parser.add_argument(
        "--init-only",
        action="store_true",
        help="Initialize TinyDB files and config tables, then exit.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = load_settings()
    storage = TinyDBStorage(settings.storage)

    try:
        storage.initialize_config(settings)
        if args.init_only:
            print("MQTT COLLECTOR INIT OK")
            print(f"data_db={settings.storage.data_db_path}")
            print(f"config_db={settings.storage.config_db_path}")
            return 0

        collector = MqttCollectorClient(
            mqtt_settings=settings.mqtt,
            storage=storage,
            subscribe_topic=args.topic,
            message_limit=args.message_limit,
        )
        collector.run_forever()
        return 0
    finally:
        storage.close()


if __name__ == "__main__":
    raise SystemExit(main())
