from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


for parent in Path(__file__).resolve().parents:
    if (parent / "iot_core").is_dir():
        sys.path.insert(0, str(parent))
        break

from iot_core.dashboard_queries import load_config_devices, load_dashboard_data, recent_table, table_for_display


st.set_page_config(page_title="OBJ Conect Dashboard", layout="wide")

st.title("OBJ Conect Dashboard")
st.caption("Dados locais do collector MQTT salvos em TinyDB.")

data = load_dashboard_data()
devices = load_config_devices()

if data.settings is not None:
    st.write(
        f"Broker MQTT: `{data.settings.mqtt.host}:{data.settings.mqtt.port}` | "
        f"Topico collector: `{data.settings.mqtt.subscribe_topic}`"
    )

for warning in data.warnings:
    st.warning(warning)

count_columns = st.columns(5)
for index, table_name in enumerate(("telemetry", "events", "status", "commands", "raw_messages")):
    with count_columns[index]:
        st.metric(table_name, data.counts.get(table_name, 0))

if not data.has_data:
    st.info(
        "Ainda nao ha dados no TinyDB. Rode o collector, inicie o Wokwi, publique comandos MQTT "
        "e aguarde mensagens de telemetry/status/events."
    )

st.subheader("Devices configurados")
if devices.empty:
    st.info("Nenhum device encontrado em configs/devices.yaml.")
else:
    st.dataframe(devices, use_container_width=True, hide_index=True)

st.subheader("Mensagens recentes")
raw = recent_table(data, "raw_messages", limit=10)
if raw.empty:
    st.info("Nenhuma raw message coletada ainda.")
else:
    st.dataframe(
        table_for_display(
            raw,
            ["received_at", "topic", "channel", "payload_valid", "payload_format", "payload_raw"],
        ),
        use_container_width=True,
        hide_index=True,
    )
