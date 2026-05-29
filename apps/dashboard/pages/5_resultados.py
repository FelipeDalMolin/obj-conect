from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


for parent in Path(__file__).resolve().parents:
    if (parent / "iot_core").is_dir():
        sys.path.insert(0, str(parent))
        break


st.set_page_config(page_title="Resultados", layout="wide")
st.title("Resultados")

st.warning(
    "Os dados preenchidos nesta página são temporários da sessão do Streamlit. "
    "Exporte o CSV antes de fechar, recarregar a página ou reiniciar o dashboard."
)


MEASUREMENT_GROUPS = (
    {
        "name": "Sensor LDR",
        "type": "Sensor",
        "scenario": "Alterar luminosidade no Wokwi e observar telemetry/events.",
        "start": "Alteração manual da luminosidade no Wokwi.",
        "end": "Recebimento de telemetry/events refletindo a nova condição de luz.",
    },
    {
        "name": "Sensor PIR",
        "type": "Sensor",
        "scenario": "Acionar presença no Wokwi e observar telemetry/events.",
        "start": "Acionamento manual do PIR no Wokwi.",
        "end": "Recebimento de events/telemetry com presença detectada.",
    },
    {
        "name": "Atuador LED - ligar",
        "type": "Atuador",
        "scenario": "Enviar light:on pelo Streamlit ou npm e observar LED/status.",
        "start": "Envio do comando light:on.",
        "end": "LED ligado no Wokwi ou status com lamp_state=on.",
    },
    {
        "name": "Atuador LED - desligar",
        "type": "Atuador",
        "scenario": "Enviar light:off pelo Streamlit ou npm e observar LED/status.",
        "start": "Envio do comando light:off.",
        "end": "LED desligado no Wokwi ou status com lamp_state=off.",
    },
)

COLUMNS = [
    "Núm. medida",
    "Sensor/atuador",
    "Tipo",
    "Cenário de teste",
    "Marco inicial",
    "Marco final",
    "Tempo de resposta (ms)",
    "Observação",
]


def default_measurements() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for group in MEASUREMENT_GROUPS:
        for number in range(1, 5):
            rows.append(
                {
                    "Núm. medida": number,
                    "Sensor/atuador": group["name"],
                    "Tipo": group["type"],
                    "Cenário de teste": group["scenario"],
                    "Marco inicial": group["start"],
                    "Marco final": group["end"],
                    "Tempo de resposta (ms)": None,
                    "Observação": "",
                }
            )

    return pd.DataFrame(rows, columns=COLUMNS)


if "resultados_mqtt_measurements" not in st.session_state:
    st.session_state["resultados_mqtt_measurements"] = default_measurements()

if st.button("Restaurar tabela vazia", type="secondary"):
    st.session_state["resultados_mqtt_measurements"] = default_measurements()
    st.rerun()

st.subheader("Tabela de medições")
edited = st.data_editor(
    st.session_state["resultados_mqtt_measurements"],
    use_container_width=True,
    hide_index=True,
    num_rows="fixed",
    column_config={
        "Tempo de resposta (ms)": st.column_config.NumberColumn(
            "Tempo de resposta (ms)",
            min_value=0.0,
            step=1.0,
            format="%.0f",
        ),
        "Observação": st.column_config.TextColumn("Observação", width="medium"),
    },
)
st.session_state["resultados_mqtt_measurements"] = edited

results = edited.copy()
results["Tempo de resposta (ms)"] = pd.to_numeric(results["Tempo de resposta (ms)"], errors="coerce")
valid_results = results.dropna(subset=["Tempo de resposta (ms)"])

st.download_button(
    "Baixar CSV",
    data=results.to_csv(index=False).encode("utf-8-sig"),
    file_name="resultados-mqtt-medicoes.csv",
    mime="text/csv",
)

st.subheader("Média por sensor/atuador")
if valid_results.empty:
    st.info("Preencha ao menos uma medição para calcular médias e gerar gráficos.")
else:
    averages = (
        valid_results.groupby(["Sensor/atuador", "Tipo"], as_index=False)["Tempo de resposta (ms)"]
        .mean()
        .rename(columns={"Tempo de resposta (ms)": "Tempo médio (ms)"})
    )
    averages["Tempo médio (ms)"] = averages["Tempo médio (ms)"].round(2)

    st.dataframe(averages, use_container_width=True, hide_index=True)

    bar_fig = px.bar(
        averages,
        x="Sensor/atuador",
        y="Tempo médio (ms)",
        color="Tipo",
        text="Tempo médio (ms)",
        title="Tempo médio de resposta por sensor/atuador",
    )
    bar_fig.update_layout(xaxis_title="", yaxis_title="Tempo médio (ms)")
    st.plotly_chart(bar_fig, use_container_width=True)

    scatter_fig = px.scatter(
        valid_results,
        x="Núm. medida",
        y="Tempo de resposta (ms)",
        color="Sensor/atuador",
        symbol="Tipo",
        title="Medições individuais de tempo de resposta",
    )
    scatter_fig.update_layout(xaxis_title="Núm. medida", yaxis_title="Tempo de resposta (ms)")
    st.plotly_chart(scatter_fig, use_container_width=True)
