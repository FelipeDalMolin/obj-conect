# Dashboard Streamlit

A v0.3 adiciona um dashboard Streamlit minimo para visualizar os dados salvos pelo collector MQTT em TinyDB e publicar comandos MQTT para o ESP32 simulado.

## Fluxo esperado

```text
Streamlit -> MQTT broker -> collector -> TinyDB -> dashboard
```

O Streamlit nao grava comandos diretamente no TinyDB. Ele publica no broker MQTT. O historico local so aparece quando o collector esta rodando e recebe a mensagem.

## Preparar ambiente

Na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Rodar collector

Em um terminal:

```powershell
.\.venv\Scripts\python.exe -m tools.collector.mqtt_collector
```

O collector assina:

`mackenzie/iot/v1/campus01/lab01/lighting/+/+`

Ele grava em:

- `data/local/iot_data.json`
- `data/local/iot_config.json`

## Rodar dashboard

Em outro terminal, sempre a partir da raiz do projeto:

```powershell
.\.venv\Scripts\python.exe -m streamlit run apps\dashboard\app.py
```

## Paginas

Home:

- mostra broker configurado;
- mostra contagens por tabela;
- mostra devices configurados;
- mostra raw messages recentes.

Live Monitor:

- mostra a ultima telemetry por device;
- mostra lux, presence, light_condition, control_mode e lamp_state;
- mostra grafico de lux quando houver dados;
- mostra ultimos events e status.
- usa polling leve de 2 segundos apenas na area dinamica.

Devices:

- lista devices configurados;
- mostra ultima telemetry e ultimo status por device.

Commands:

- publica `status`;
- publica `light:on`;
- publica `light:off`;
- publica `mode:auto`;
- mostra historico local de commands vindo do TinyDB.

Data Explorer:

- permite escolher tabelas do TinyDB;
- mostra registros recentes;
- mostra raw messages para debug.

## Testar botoes de comando

1. Rode o collector.
2. Rode o dashboard.
3. Abra a pagina Commands.
4. Clique em `Light on`, `Light off` ou `Mode auto`.
5. Aguarde o collector receber a mensagem.
6. Atualize a pagina ou navegue novamente para ver o historico local.

Se o collector nao estiver rodando, o comando pode ser publicado com sucesso no broker, mas nao aparecera em `commands` no TinyDB.

## Quando nao houver dados

Se o dashboard estiver vazio:

- rode o collector;
- rode o Wokwi;
- publique comandos MQTT;
- aguarde mensagens de telemetry, status ou events;
- atualize a pagina.

## Polling leve no Live Monitor

A pagina Live Monitor usa `st.fragment(run_every="2s")` apenas na area dinamica.

A cada ciclo, o dashboard verifica um token simples de revisao do arquivo `data/local/iot_data.json`:

- tamanho do arquivo;
- `mtime_ns` do arquivo.

Se o token mudou, o dashboard recarrega os dados do TinyDB e atualiza o snapshot em `st.session_state`.

Se o token nao mudou, o dashboard reaproveita o ultimo snapshot em memoria. Isso evita reler o TinyDB sem necessidade.

Na tela, o Live Monitor mostra:

- ultima atualizacao detectada;
- se esta aguardando novos dados;
- contagem de registros por tabela.

Isso e diferente de um auto-refresh completo: a pagina inteira nao precisa ser reconstruida a cada 2 segundos, e a leitura do banco so acontece quando o arquivo muda.

## Limitacoes desta etapa

- Sem autenticacao.
- Sem dashboard de producao.
- Sem escrita direta no TinyDB pelo Streamlit.
- Polling leve apenas no Live Monitor.
- TinyDB e adequado para prototipo local e baixo volume; para producao, use banco com concorrencia e consultas mais robustas.
