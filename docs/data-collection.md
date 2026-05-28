# Coleta local MQTT com TinyDB

A v0.2 adiciona um coletor Python local para assinar mensagens MQTT do ESP32 simulado no Wokwi e salvar os dados em TinyDB. O objetivo e preparar uma base simples para paginas e graficos futuros em Streamlit, sem alterar o firmware PlatformIO.

## Criar ambiente Python

No PowerShell, na raiz do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Rodar o collector

```powershell
.\.venv\Scripts\python.exe -m tools.collector.mqtt_collector
```

Para apenas inicializar os arquivos TinyDB e validar configs:

```powershell
.\.venv\Scripts\python.exe -m tools.collector.mqtt_collector --init-only
```

Para testes automatizados ou demonstracoes curtas:

```powershell
.\.venv\Scripts\python.exe -m tools.collector.mqtt_collector --message-limit 4
```

## Topicos assinados

Topico padrao:

`mackenzie/iot/v1/campus01/lab01/lighting/+/+`

Esse padrao captura exatamente:

`mackenzie/iot/v1/{site}/{area}/{domain}/{device_id}/{channel}`

Canais esperados:

- `telemetry`
- `events`
- `status`
- `commands`

Alternativa de debug:

`mackenzie/iot/v1/campus01/lab01/lighting/+/#`

Use a alternativa de debug apenas quando precisar investigar topicos fora do formato esperado.

## Validacao de topicos e payloads

O collector valida exatamente 8 segmentos:

`mackenzie/iot/v1/{site}/{area}/{domain}/{device_id}/{channel}`

Se o topico nao bater com esse formato, a mensagem e salva apenas em `raw_messages` e o processo continua.

Se o payload nao for JSON valido, a mensagem tambem e preservada com:

- `payload_valid=false`
- `payload_raw`
- `payload_error`
- `received_at`

O timestamp `received_at` e salvo em ISO-8601 UTC, por exemplo:

`2026-05-28T14:30:00.123456+00:00`

## TinyDB

O collector cria dois arquivos locais:

- `data/local/iot_data.json`
- `data/local/iot_config.json`

Esses arquivos sao ignorados pelo Git.

`iot_data.json` contem:

- `telemetry`
- `events`
- `status`
- `commands`
- `raw_messages`

`iot_config.json` contem:

- `devices`
- `environments`
- `settings`

As tabelas de configuracao sao inicializadas a partir de:

- `configs/devices.yaml`
- `configs/environments.yaml`
- `configs/mqtt.yaml`

## Formato para Streamlit

Cada documento salvo nas tabelas de canal contem:

- `received_at`
- `topic`
- `site`
- `area`
- `domain`
- `device_id`
- `channel`
- `payload`
- `payload_valid`
- `schema_version`

A tabela `telemetry` serve como base para graficos de serie temporal com `lux`, `presence`, `light_condition`, `control_mode` e `lamp_state`.

A tabela `events` serve para linha do tempo de eventos.

A tabela `status` serve para cards de estado atual por dispositivo.

A tabela `commands` serve para auditoria de comandos enviados.

A tabela `raw_messages` serve para debug e reprocessamento.

## Gerar mensagens de teste

Com o collector rodando em um terminal, use outro terminal:

```powershell
npm run mqtt:pub:status
npm run mqtt:pub:light:on
npm run mqtt:pub:light:off
npm run mqtt:pub:mode:auto
```

Tambem e possivel deixar um assinante aberto para comparar:

```powershell
npm run mqtt:sub:device
```

## Configuracao via .env

Opcionalmente, crie um `.env` local para sobrescrever a configuracao MQTT sem alterar YAML:

```env
MQTT_HOST=broker.hivemq.com
MQTT_PORT=1883
MQTT_CLIENT_ID=obj-conect-collector
MQTT_QOS=0
MQTT_SUBSCRIBE_TOPIC=mackenzie/iot/v1/campus01/lab01/lighting/+/+
```

## Limitacoes do TinyDB

TinyDB e adequado para prototipo local, demonstracoes e baixo volume.

Nao e recomendado para producao porque:

- nao oferece concorrencia robusta para varios escritores;
- nao possui indices reais como bancos relacionais ou documentais completos;
- grava em arquivo local;
- pode ficar lento com volume alto;
- exige cuidado para backup e integridade do arquivo.

Para producao, considere PostgreSQL, SQLite com schema bem definido, InfluxDB ou outro banco apropriado ao volume e aos requisitos de consulta.
