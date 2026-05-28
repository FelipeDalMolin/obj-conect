# Coleta local MQTT com TinyDB

Este documento explica como funciona a camada Python que coleta mensagens MQTT e salva os dados localmente em TinyDB.

A coleta foi adicionada para transformar a simulação em uma base de dados simples, que pode ser lida pelo dashboard Streamlit e usada em análises futuras.

## 1. Papel do collector

O firmware do ESP32 publica mensagens MQTT. O collector Python é outro cliente MQTT, executado no seu computador, que assina os mesmos tópicos e grava as mensagens recebidas.

Fluxo:

```text
ESP32 simulado
  ↓ publica MQTT
Broker MQTT
  ↓ entrega mensagens
Collector Python
  ↓ valida e normaliza
TinyDB
  ↓
Dashboard Streamlit
```

O collector não substitui o MQTT do ESP32. Ele apenas participa da mesma rede MQTT como cliente assinante.

## 2. Criar ambiente Python

Na raiz do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 3. Rodar o collector

Para escutar mensagens continuamente:

```powershell
.\.venv\Scripts\python.exe -m tools.collector.mqtt_collector
```

Para apenas inicializar os bancos TinyDB e validar as configurações:

```powershell
.\.venv\Scripts\python.exe -m tools.collector.mqtt_collector --init-only
```

Para testes rápidos com limite de mensagens:

```powershell
.\.venv\Scripts\python.exe -m tools.collector.mqtt_collector --message-limit 4
```

## 4. Tópico assinado

O tópico padrão é:

```text
mackenzie/iot/v1/campus01/lab01/lighting/+/+
```

Esse padrão captura exatamente mensagens no formato:

```text
mackenzie/iot/v1/{site}/{area}/{domain}/{device_id}/{channel}
```

Canais esperados:

```text
telemetry
events
status
commands
```

Para debug, pode-se usar:

```text
mackenzie/iot/v1/campus01/lab01/lighting/+/# 
```

Use o tópico de debug apenas quando quiser investigar mensagens fora do formato esperado.

## 5. Validação de tópicos

O collector espera exatamente 8 segmentos:

```text
mackenzie / iot / v1 / {site} / {area} / {domain} / {device_id} / {channel}
```

Se o tópico não seguir esse formato, a mensagem não é perdida. Ela é salva em `raw_messages` para debug e reprocessamento.

## 6. Validação de payloads

Para `telemetry`, `events` e `status`, o collector espera JSON válido.

Se o payload não for JSON válido, a mensagem é preservada com:

```text
payload_valid = false
payload_raw
payload_error
received_at
```

Para `commands`, o collector aceita JSON ou texto simples. Isso é útil porque comandos como `light:on` são fáceis de enviar pelo terminal.

Comandos texto reconhecidos:

| Texto recebido | Payload normalizado |
|---|---|
| `status` | `{"command": "status"}` |
| `light:on` | `{"command": "set_light", "state": "on"}` |
| `light:off` | `{"command": "set_light", "state": "off"}` |
| `mode:auto` | `{"command": "set_mode", "mode": "auto"}` |

Comandos reconhecidos ficam com:

```text
payload_valid = true
payload_format = text_command
payload_raw = texto original
```

Comandos desconhecidos em `commands` ficam com:

```text
payload_valid = false
payload_error = invalid_command
payload_raw = texto original
```

## 7. Timestamp

O campo `received_at` é salvo em UTC no padrão ISO-8601.

Exemplo:

```text
2026-05-28T14:30:00.123456+00:00
```

Isso facilita gráficos e análises futuras.

## 8. Arquivos TinyDB

O collector cria dois arquivos locais:

```text
data/local/iot_data.json
data/local/iot_config.json
```

Esses arquivos são ignorados pelo Git.

`iot_data.json` contém dados coletados:

```text
telemetry
events
status
commands
raw_messages
```

`iot_config.json` contém configurações locais:

```text
devices
environments
settings
```

As configurações são inicializadas a partir de:

```text
configs/devices.yaml
configs/environments.yaml
configs/mqtt.yaml
```

## 9. Formato dos documentos

Cada documento salvo nas tabelas de canal contém:

```text
received_at
topic
site
area
domain
device_id
channel
payload
payload_valid
payload_format
schema_version
```

A tabela `telemetry` alimenta gráficos temporais de lux, presença e estado da lâmpada.

A tabela `events` alimenta linha do tempo de eventos.

A tabela `status` mostra o estado atual do dispositivo.

A tabela `commands` registra comandos recebidos.

A tabela `raw_messages` serve para debug e reprocessamento.

## 10. Gerar mensagens de teste

Com o collector rodando, em outro terminal:

```powershell
npm run mqtt:pub:status
npm run mqtt:pub:light:on
npm run mqtt:pub:light:off
npm run mqtt:pub:mode:auto
```

Para acompanhar mensagens em paralelo:

```powershell
npm run mqtt:sub:device
```

## 11. Configuração via .env

Opcionalmente, crie um `.env` local para sobrescrever configurações sem alterar os YAMLs:

```env
MQTT_HOST=broker.hivemq.com
MQTT_PORT=1883
MQTT_CLIENT_ID=obj-conect-collector
MQTT_QOS=0
MQTT_SUBSCRIBE_TOPIC=mackenzie/iot/v1/campus01/lab01/lighting/+/+
```

## 12. Limitações do TinyDB

TinyDB é adequado para:

- protótipo local;
- demonstrações;
- baixo volume;
- desenvolvimento rápido em Python;
- integração simples com Streamlit.

TinyDB não é recomendado para produção porque:

- grava em arquivo local;
- não tem concorrência robusta para múltiplos escritores;
- não possui índices como bancos relacionais ou documentais completos;
- pode ficar lento com alto volume;
- exige cuidado com backup e integridade do arquivo.

Para produção, considere PostgreSQL, SQLite com schema definido, InfluxDB, TimescaleDB ou outro banco adequado ao volume e às consultas necessárias.
