# Dashboard Streamlit

Este documento explica como rodar e usar o dashboard Streamlit do projeto.

O dashboard foi criado para visualizar os dados coletados pelo collector MQTT e também para publicar comandos MQTT pela interface. Ele é uma camada local de operação e demonstração.

## 1. Fluxo esperado

```text
Streamlit
  -> publica comandos MQTT
MQTT broker
  -> entrega mensagens
Collector Python
  -> salva histórico
TinyDB
  ->
Dashboard lê e exibe
```

O Streamlit não grava comandos diretamente no TinyDB. Quando você clica em `Light on`, por exemplo, o dashboard publica `light:on` no broker MQTT. O histórico só aparece no TinyDB quando o collector está rodando e recebe essa mensagem.

## 2. Preparar ambiente

Na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 3. Rodar collector

Em um terminal:

```powershell
.\.venv\Scripts\python.exe -m tools.collector.mqtt_collector
```

O collector assina:

```text
mackenzie/iot/v1/campus01/lab01/lighting/+/+
```

E grava em:

```text
data/local/iot_data.json
data/local/iot_config.json
```

## 4. Rodar dashboard

Em outro terminal, sempre a partir da raiz do projeto:

```powershell
.\.venv\Scripts\python.exe -m streamlit run apps\dashboard\app.py
```

O navegador abrirá o dashboard Streamlit.

## 5. Página Home

A página inicial mostra:

- broker configurado;
- contagens por tabela;
- devices configurados;
- mensagens recentes;
- orientação caso ainda não existam dados.

Use essa página para confirmar se o TinyDB está sendo encontrado e se há registros coletados.

## 6. Página Live Monitor

A página Live Monitor mostra o estado mais recente do dispositivo:

- lux;
- presença;
- condição de luz;
- modo de controle;
- estado da lâmpada;
- eventos recentes;
- status recentes.

Também mostra gráficos quando houver dados suficientes.

## 7. Atualização “viva” do Live Monitor

O Live Monitor usa polling leve a cada 2 segundos apenas na área dinâmica.

A cada ciclo, ele verifica se `data/local/iot_data.json` mudou. Para isso, compara:

- tamanho do arquivo;
- `mtime_ns`, que representa a última modificação do arquivo.

Se o arquivo mudou, o dashboard recarrega os dados do TinyDB e atualiza o snapshot em memória.

Se não mudou, reaproveita o último snapshot salvo em `st.session_state`.

Isso evita recarregar o TinyDB sem necessidade e dá a sensação de monitoramento ao vivo.

## 8. Página Devices

A página Devices lista os dispositivos configurados e mostra, quando disponível:

- última telemetria;
- último status;
- área;
- domínio;
- device ID.

Ela é útil para confirmar se a configuração de `configs/devices.yaml` está coerente com os dados recebidos.

## 9. Página Commands

A página Commands permite publicar comandos MQTT:

```text
status
light:on
light:off
mode:auto
```

Comportamento esperado:

| Botão | Efeito |
|---|---|
| Status | Pede status atualizado do ESP32. |
| Light on | Liga a lâmpada e muda para modo manual. |
| Light off | Desliga a lâmpada e muda para modo manual. |
| Mode auto | Retorna para a lógica automática. |

Lembre-se: se o collector não estiver rodando, o comando pode ser publicado com sucesso no broker, mas não aparecerá no histórico local do TinyDB.

## 10. Página Data Explorer

A página Data Explorer permite inspecionar as tabelas TinyDB:

```text
telemetry
events
status
commands
raw_messages
```

Ela é útil para debug, validação e demonstração.

## 11. Quando o dashboard estiver vazio

Se a tela estiver vazia ou sem dados recentes:

1. confirme que o collector está rodando;
2. confirme que o Wokwi está rodando;
3. publique comandos MQTT;
4. aguarde mensagens de `telemetry`, `status` ou `events`;
5. volte ao Live Monitor.

## 12. Teste mínimo

Terminal 1:

```powershell
.\.venv\Scripts\python.exe -m tools.collector.mqtt_collector
```

Terminal 2:

```powershell
.\.venv\Scripts\python.exe -m streamlit run apps\dashboard\app.py
```

VS Code:

```text
Wokwi: Start Simulator
```

No dashboard:

1. abra Commands;
2. clique em `Light on`;
3. confirme o LED ligado no Wokwi;
4. clique em `Light off`;
5. clique em `Mode auto`;
6. manipule lux e presença no Wokwi;
7. veja o Live Monitor atualizar.

## 13. Limitações desta etapa

Esta versão é intencionalmente simples:

- sem autenticação;
- sem controle de usuários;
- sem dashboard de produção;
- sem escrita direta no TinyDB pelo Streamlit;
- polling leve apenas no Live Monitor;
- TinyDB adequado para protótipo local e baixo volume.

Para produção, seria melhor usar um banco com concorrência e consulta mais robustas.
