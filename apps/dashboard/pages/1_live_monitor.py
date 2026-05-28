from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st


for parent in Path(__file__).resolve().parents:
    if (parent / "iot_core").is_dir():
        sys.path.insert(0, str(parent))
        break

from iot_core.dashboard_queries import (
    DashboardData,
    get_data_revision,
    latest_status_by_device,
    latest_telemetry_by_device,
    load_dashboard_data,
    recent_table,
    table_for_display,
)


st.set_page_config(page_title="Live Monitor", layout="wide")
st.title("Live Monitor")
st.caption("Polling leve a cada 2s. O TinyDB so e recarregado quando tamanho ou mtime mudam.")


def _current_snapshot() -> DashboardData:
    snapshot = st.session_state.get("live_monitor_snapshot")
    if snapshot is None:
        snapshot = load_dashboard_data()
        st.session_state["live_monitor_snapshot"] = snapshot
    return snapshot


@st.fragment(run_every="2s")
def live_monitor_fragment() -> None:
    revision = get_data_revision()
    previous_token = st.session_state.get("live_monitor_revision_token")
    changed = previous_token != revision.token

    if changed:
        data = load_dashboard_data()
        st.session_state["live_monitor_snapshot"] = data
        st.session_state["live_monitor_revision_token"] = revision.token
        st.session_state["live_monitor_last_change"] = revision.observed_at
    else:
        data = _current_snapshot()

    last_change = st.session_state.get("live_monitor_last_change", "nenhuma")

    status_cols = st.columns(3)
    status_cols[0].metric("Ultima atualizacao detectada", last_change)
    status_cols[1].metric("Estado", "dados atualizados" if changed else "aguardando novos dados")
    status_cols[2].metric("Arquivo TinyDB", "ok" if revision.exists else "indisponivel")

    if revision.warning:
        st.warning(revision.warning)

    count_cols = st.columns(5)
    for index, table_name in enumerate(("telemetry", "events", "status", "commands", "raw_messages")):
        count_cols[index].metric(table_name, data.counts.get(table_name, 0))

    for warning in data.warnings:
        st.warning(warning)

    latest = latest_telemetry_by_device(data)
    if latest.empty:
        st.info("Sem telemetry ainda. Rode o collector e o Wokwi, depois aguarde a proxima publicacao.")
    else:
        for _, row in latest.iterrows():
            st.subheader(str(row.get("device_id", "device")))
            cols = st.columns(5)
            cols[0].metric("Lux", f"{row.get('lux', '-')}")
            cols[1].metric("Presence", str(row.get("presence", "-")))
            cols[2].metric("Light", str(row.get("light_condition", "-")))
            cols[3].metric("Mode", str(row.get("control_mode", "-")))
            cols[4].metric("Lamp", str(row.get("lamp_state", "-")))

    telemetry = data.tables.get("telemetry")
    if telemetry is not None and not telemetry.empty and {"received_at", "lux"}.issubset(telemetry.columns):
        st.subheader("Lux ao longo do tempo")
        chart_data = telemetry.sort_values("received_at")
        color = "device_id" if "device_id" in chart_data.columns else None
        fig = px.line(chart_data, x="received_at", y="lux", color=color, markers=True)
        st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.subheader("Ultimos events")
        events = recent_table(data, "events", limit=10)
        if events.empty:
            st.info("Nenhum event coletado ainda.")
        else:
            st.dataframe(
                table_for_display(events, ["received_at", "device_id", "event", "lux", "control_mode", "lamp_state"]),
                use_container_width=True,
                hide_index=True,
            )

    with right:
        st.subheader("Ultimos status")
        status = recent_table(data, "status", limit=10)
        latest_status = latest_status_by_device(data)
        if status.empty and latest_status.empty:
            st.info("Nenhum status coletado ainda.")
        else:
            st.dataframe(
                table_for_display(status, ["received_at", "device_id", "status", "ip", "control_mode", "lamp_state"]),
                use_container_width=True,
                hide_index=True,
            )


live_monitor_fragment()
