from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


for parent in Path(__file__).resolve().parents:
    if (parent / "iot_core").is_dir():
        sys.path.insert(0, str(parent))
        break

from iot_core.dashboard_queries import DATA_TABLES, load_dashboard_data, recent_table


st.set_page_config(page_title="Data Explorer", layout="wide")
st.title("Data Explorer")

data = load_dashboard_data()
for warning in data.warnings:
    st.warning(warning)

table_name = st.selectbox("Tabela", DATA_TABLES, index=0)
limit = st.slider("Registros recentes", min_value=5, max_value=100, value=25, step=5)
frame = recent_table(data, table_name, limit=limit)

if frame.empty:
    st.info(f"Tabela `{table_name}` sem registros.")
else:
    st.dataframe(frame, use_container_width=True, hide_index=True)

st.subheader("Raw messages para debug")
raw = recent_table(data, "raw_messages", limit=limit)
if raw.empty:
    st.info("Sem raw messages.")
else:
    st.dataframe(raw, use_container_width=True, hide_index=True)
