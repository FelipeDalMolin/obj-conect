from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


for parent in Path(__file__).resolve().parents:
    if (parent / "iot_core").is_dir():
        sys.path.insert(0, str(parent))
        break

from iot_core.command_publisher import publish_command
from iot_core.dashboard_queries import load_config_devices, load_dashboard_data, recent_table, table_for_display


st.set_page_config(page_title="Commands", layout="wide")
st.title("Commands")

st.info(
    "O Streamlit publica comandos no broker MQTT. Quem grava no TinyDB e o collector. "
    "Se o collector nao estiver rodando, o comando pode ser publicado, mas nao aparecera no historico local."
)

feedback = st.session_state.pop("command_publish_feedback", None)
if feedback:
    if feedback["ok"]:
        st.success(feedback["message"])
    else:
        st.error(feedback["message"])

data = load_dashboard_data()
devices = load_config_devices()

if devices.empty or "device_id" not in devices.columns:
    device_id = "esp32_01"
    st.warning("Nenhum device configurado encontrado; usando esp32_01.")
else:
    device_options = list(devices["device_id"].astype(str))
    device_id = st.selectbox("Device", device_options)

commands = {
    "Status": "status",
    "Light on": "light:on",
    "Light off": "light:off",
    "Mode auto": "mode:auto",
}

cols = st.columns(len(commands))
for index, (label, command) in enumerate(commands.items()):
    with cols[index]:
        if st.button(label, use_container_width=True):
            result = publish_command(command, device_id=device_id)
            if result.ok:
                st.session_state["command_publish_feedback"] = {
                    "ok": True,
                    "message": f"{result.message} `{result.payload}` -> `{result.topic}`",
                }
            else:
                st.session_state["command_publish_feedback"] = {
                    "ok": False,
                    "message": result.message,
                }
            st.rerun()

st.subheader("Historico local de commands")
history = recent_table(data, "commands", limit=20)
if history.empty:
    st.info("Nenhum command coletado ainda. Rode o collector para preencher este historico.")
else:
    st.dataframe(
        table_for_display(history, ["received_at", "device_id", "payload_raw", "payload_format", "payload_valid", "command", "state", "mode"]),
        use_container_width=True,
        hide_index=True,
    )
