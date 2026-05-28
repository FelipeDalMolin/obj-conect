from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import pandas as pd
from tinydb import TinyDB

from iot_core.settings import AppSettings, load_settings


DATA_TABLES = ("telemetry", "events", "status", "commands", "raw_messages")


@dataclass(frozen=True)
class DashboardData:
    settings: AppSettings | None
    tables: dict[str, pd.DataFrame]
    counts: dict[str, int]
    warnings: list[str]

    @property
    def has_data(self) -> bool:
        return any(self.counts.values())


@dataclass(frozen=True)
class DataRevision:
    path: str
    exists: bool
    size: int | None
    mtime_ns: int | None
    token: str
    observed_at: str
    warning: str | None = None


def get_data_revision() -> DataRevision:
    observed_at = datetime.now(timezone.utc).isoformat()

    try:
        settings = load_settings()
    except Exception as exc:
        return DataRevision(
            path="",
            exists=False,
            size=None,
            mtime_ns=None,
            token=f"settings-error:{type(exc).__name__}:{exc}",
            observed_at=observed_at,
            warning=f"Falha ao carregar configuracoes: {exc}",
        )

    path = settings.storage.data_db_path
    try:
        stat = path.stat()
    except FileNotFoundError:
        return DataRevision(
            path=str(path),
            exists=False,
            size=None,
            mtime_ns=None,
            token=f"missing:{path}",
            observed_at=observed_at,
            warning=f"TinyDB nao encontrado: {path}",
        )
    except OSError as exc:
        return DataRevision(
            path=str(path),
            exists=False,
            size=None,
            mtime_ns=None,
            token=f"unavailable:{path}:{type(exc).__name__}:{exc}",
            observed_at=observed_at,
            warning=f"TinyDB temporariamente indisponivel: {exc}",
        )

    warning = "TinyDB esta vazio." if stat.st_size == 0 else None
    return DataRevision(
        path=str(path),
        exists=True,
        size=stat.st_size,
        mtime_ns=stat.st_mtime_ns,
        token=f"{path}:{stat.st_size}:{stat.st_mtime_ns}",
        observed_at=observed_at,
        warning=warning,
    )


def load_dashboard_data(limit: int | None = None) -> DashboardData:
    warnings: list[str] = []

    try:
        settings = load_settings()
    except Exception as exc:
        return DashboardData(
            settings=None,
            tables=_empty_tables(),
            counts={name: 0 for name in DATA_TABLES},
            warnings=[f"Falha ao carregar configuracoes: {exc}"],
        )

    tables: dict[str, pd.DataFrame] = {}
    counts: dict[str, int] = {}

    if not settings.storage.data_db_path.exists():
        warnings.append(f"TinyDB nao encontrado: {settings.storage.data_db_path}")
        return DashboardData(settings=settings, tables=_empty_tables(), counts={name: 0 for name in DATA_TABLES}, warnings=warnings)

    try:
        db = TinyDB(settings.storage.data_db_path)
    except Exception as exc:
        warnings.append(f"Nao foi possivel abrir o TinyDB: {exc}")
        return DashboardData(settings=settings, tables=_empty_tables(), counts={name: 0 for name in DATA_TABLES}, warnings=warnings)

    try:
        for table_name in DATA_TABLES:
            try:
                rows = list(db.table(table_name).all())
            except Exception as exc:
                warnings.append(f"Falha ao ler tabela {table_name}: {exc}")
                rows = []

            counts[table_name] = len(rows)
            if limit is not None:
                rows = rows[-limit:]

            tables[table_name] = _records_to_dataframe(rows)
    finally:
        db.close()

    return DashboardData(settings=settings, tables=tables, counts=counts, warnings=warnings)


def load_config_devices() -> pd.DataFrame:
    try:
        settings = load_settings()
        rows = settings.devices_config.get("devices", [])
    except Exception:
        rows = []

    return _records_to_dataframe(rows)


def latest_telemetry_by_device(data: DashboardData) -> pd.DataFrame:
    telemetry = data.tables.get("telemetry", pd.DataFrame())
    if telemetry.empty or "device_id" not in telemetry.columns:
        return pd.DataFrame()

    telemetry = _sort_by_received_at(telemetry, ascending=True)
    latest = telemetry.drop_duplicates(subset=["device_id"], keep="last")
    return _sort_by_received_at(latest, ascending=False)


def latest_status_by_device(data: DashboardData) -> pd.DataFrame:
    status = data.tables.get("status", pd.DataFrame())
    if status.empty or "device_id" not in status.columns:
        return pd.DataFrame()

    status = _sort_by_received_at(status, ascending=True)
    latest = status.drop_duplicates(subset=["device_id"], keep="last")
    return _sort_by_received_at(latest, ascending=False)


def recent_table(data: DashboardData, table_name: str, limit: int = 20) -> pd.DataFrame:
    frame = data.tables.get(table_name, pd.DataFrame())
    if frame.empty:
        return frame

    return _sort_by_received_at(frame, ascending=False).head(limit)


def table_for_display(frame: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    if frame.empty:
        return frame

    display = frame.copy()
    if columns is not None:
        existing = [column for column in columns if column in display.columns]
        display = display[existing] if existing else display

    return display


def _empty_tables() -> dict[str, pd.DataFrame]:
    return {name: pd.DataFrame() for name in DATA_TABLES}


def _records_to_dataframe(rows: list[dict[str, Any]]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()

    frame = pd.json_normalize(rows, sep=".")
    if "received_at" in frame.columns:
        frame["received_at"] = pd.to_datetime(frame["received_at"], errors="coerce", utc=True)
    return frame


def _sort_by_received_at(frame: pd.DataFrame, ascending: bool) -> pd.DataFrame:
    if frame.empty or "received_at" not in frame.columns:
        return frame

    return frame.sort_values("received_at", ascending=ascending, na_position="last")
