from __future__ import annotations

from pathlib import Path
from typing import Any

from tinydb import TinyDB

from iot_core.models import utc_now_iso
from iot_core.settings import AppSettings, StorageSettings
from iot_core.topics import CHANNEL_TABLES


DATA_TABLES = ("telemetry", "events", "status", "commands", "raw_messages")
CONFIG_TABLES = ("devices", "environments", "settings")


class TinyDBStorage:
    def __init__(self, settings: StorageSettings) -> None:
        self.settings = settings
        self._prepare_file(settings.data_db_path)
        self._prepare_file(settings.config_db_path)
        settings.raw_dir.mkdir(parents=True, exist_ok=True)
        settings.exports_dir.mkdir(parents=True, exist_ok=True)
        self.data_db = TinyDB(settings.data_db_path)
        self.config_db = TinyDB(settings.config_db_path)

    def close(self) -> None:
        self.data_db.close()
        self.config_db.close()

    def initialize_config(self, app_settings: AppSettings) -> None:
        loaded_at = utc_now_iso()

        devices_table = self.config_db.table("devices")
        devices_table.truncate()
        for device in app_settings.devices_config.get("devices", []):
            devices_table.insert({"loaded_at": loaded_at, **device})

        environments_table = self.config_db.table("environments")
        environments_table.truncate()
        for environment in app_settings.environments_config.get("environments", []):
            environments_table.insert({"loaded_at": loaded_at, **environment})

        settings_table = self.config_db.table("settings")
        settings_table.truncate()
        settings_table.insert(
            {
                "loaded_at": loaded_at,
                "name": "mqtt",
                "config": app_settings.mqtt_config,
            }
        )

        self._ensure_table_keys(self.data_db, DATA_TABLES)
        self._ensure_table_keys(self.config_db, CONFIG_TABLES)

    def store_message(self, record: dict[str, Any]) -> str:
        self.data_db.table("raw_messages").insert(record)

        if not record.get("topic_valid"):
            return "raw_messages"

        table_name = CHANNEL_TABLES.get(str(record.get("channel")))
        if table_name is None:
            return "raw_messages"

        self.data_db.table(table_name).insert(record)
        return table_name

    @staticmethod
    def _prepare_file(path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text("{}", encoding="utf-8")

    @staticmethod
    def _ensure_table_keys(db: TinyDB, table_names: tuple[str, ...]) -> None:
        data = db.storage.read() or {}
        changed = False

        for table_name in table_names:
            if table_name not in data:
                data[table_name] = {}
                changed = True

        if changed:
            db.storage.write(data)
