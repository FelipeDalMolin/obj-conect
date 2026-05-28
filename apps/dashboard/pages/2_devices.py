from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


for parent in Path(__file__).resolve().parents:
    if (parent / "iot_core").is_dir():
        sys.path.insert(0, str(parent))
        break

from iot_core.dashboard_queries import (
    latest_status_by_device,
    latest_telemetry_by_device,
    load_config_devices,
    load_dashboard_data,
    table_for_display,
)


st.set_page_config(page_title="Devices", layout="wide")
st.title("Devices")

data = load_dashboard_data()
devices = load_config_devices()
telemetry = latest_telemetry_by_device(data)
status = latest_status_by_device(data)

for warning in data.warnings:
    st.warning(warning)

if devices.empty:
    st.info("Nenhum device configurado.")
else:
    st.subheader("Configuracao")
    st.dataframe(devices, use_container_width=True, hide_index=True)

st.subheader("Ultima telemetry por device")
if telemetry.empty:
    st.info("Sem telemetry coletada.")
else:
    st.dataframe(
        table_for_display(
            telemetry,
            ["received_at", "device_id", "lux", "presence", "light_condition", "control_mode", "lamp_state"],
        ),
        use_container_width=True,
        hide_index=True,
    )

st.subheader("Ultimo status por device")
if status.empty:
    st.info("Sem status coletado.")
else:
    st.dataframe(
        table_for_display(status, ["received_at", "device_id", "status", "ip", "firmware", "control_mode", "lamp_state"]),
        use_container_width=True,
        hide_index=True,
    )
