# MQTT pelo VS Code

Este projeto usa MQTT para trocar mensagens entre o ESP32 simulado no Wokwi e clientes executados no terminal do VS Code.

Referencia Wokwi para rede WiFi no ESP32:

`https://docs.wokwi.com/guides/esp32-wifi`

## Conceitos rapidos

- Broker: servidor MQTT que recebe mensagens publicadas e entrega aos assinantes. O padrao do projeto e `broker.hivemq.com:1883`.
- Dispositivo: o ESP32 simulado no Wokwi. Ele tambem e um cliente MQTT.
- Publisher: qualquer cliente que publica mensagens em um topico. O ESP32 publica `telemetry`, `events` e `status`.
- Subscriber: qualquer cliente que assina topicos. O ESP32 assina `commands`.
- Cliente MQTT: programa que conecta no broker, como o ESP32, a CLI `mqtt`, Mosquitto client via Docker ou MQTTX.

## Broker configurado

Broker padrao:

`broker.hivemq.com:1883`

Broker alternativo no firmware:

`test.mosquitto.org:1883`

A troca e feita no codigo, alterando a constante `MQTT_BROKER_ATIVO`.

## Estrutura de topicos

Padrao:

`mackenzie/iot/v1/{site}/{area}/{domain}/{device_id}/{channel}`

Configuracao deste projeto:

- Root: `mackenzie/iot/v1`
- Site: `campus01`
- Area: `lab01`
- Domain: `lighting`
- Device ID: `esp32_01`
- Base topic: `mackenzie/iot/v1/campus01/lab01/lighting/esp32_01`

Topicos finais:

- `mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/telemetry`
- `mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/events`
- `mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/status`
- `mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/commands`

## Payloads

Telemetry:

```json
{
  "site": "campus01",
  "area": "lab01",
  "domain": "lighting",
  "device_id": "esp32_01",
  "lux": 123.45,
  "presence": true,
  "light_condition": "dark",
  "control_mode": "auto",
  "lamp_state": "on",
  "uptime_ms": 123456,
  "source": "wokwi"
}
```

Events:

```json
{
  "site": "campus01",
  "area": "lab01",
  "domain": "lighting",
  "device_id": "esp32_01",
  "event": "motion_detected_in_dark_environment",
  "lux": 123.45,
  "control_mode": "auto",
  "lamp_state": "on",
  "uptime_ms": 123456,
  "source": "wokwi"
}
```

Status:

```json
{
  "site": "campus01",
  "area": "lab01",
  "domain": "lighting",
  "device_id": "esp32_01",
  "status": "online",
  "ip": "x.x.x.x",
  "firmware": "0.1.0",
  "control_mode": "auto",
  "lamp_state": "off",
  "uptime_ms": 123456,
  "source": "wokwi"
}
```

Erro de comando:

```json
{
  "site": "campus01",
  "area": "lab01",
  "domain": "lighting",
  "device_id": "esp32_01",
  "status": "error",
  "error": "invalid_command",
  "received": "comando_invalido",
  "uptime_ms": 123456,
  "source": "wokwi"
}
```

## Modo automatico e modo manual

No modo `auto`, a lampada liga quando ha presenca e o ambiente esta escuro.

No modo `manual`, a lampada segue o ultimo comando remoto. A regra automatica nao altera o LED ate que o comando `mode:auto` seja recebido.

## Forma recomendada: npm scripts

Instale as dependencias uma vez:

```powershell
npm install
```

Assinar tudo do dispositivo:

```powershell
npm run mqtt:sub:device
```

Publicar comando de status:

```powershell
npm run mqtt:pub:status
```

Ligar a lampada em modo manual:

```powershell
npm run mqtt:pub:light:on
```

Desligar a lampada em modo manual:

```powershell
npm run mqtt:pub:light:off
```

Voltar para o modo automatico:

```powershell
npm run mqtt:pub:mode:auto
```

Assinar todos os dispositivos de `lighting` do `lab01`:

```powershell
npm run mqtt:sub:lab-lighting
```

Assinar tudo do `lab01`:

```powershell
npm run mqtt:sub:lab
```

## Teste rapido com npx

O `npx` executa a CLI do pacote `mqtt` sem instalacao global.

Assinar tudo do dispositivo:

```powershell
npx.cmd --yes mqtt sub -h broker.hivemq.com -p 1883 -t "mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/#" -v
```

Publicar comando de status:

```powershell
npx.cmd --yes mqtt pub -h broker.hivemq.com -p 1883 -t "mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/commands" -m "status"
```

Ligar a lampada:

```powershell
npx.cmd --yes mqtt pub -h broker.hivemq.com -p 1883 -t "mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/commands" -m "light:on"
```

Desligar a lampada:

```powershell
npx.cmd --yes mqtt pub -h broker.hivemq.com -p 1883 -t "mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/commands" -m "light:off"
```

Voltar para o modo automatico:

```powershell
npx.cmd --yes mqtt pub -h broker.hivemq.com -p 1883 -t "mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/commands" -m "mode:auto"
```

Assinar todos os dispositivos de `lighting` do `lab01`:

```powershell
npx.cmd --yes mqtt sub -h broker.hivemq.com -p 1883 -t "mackenzie/iot/v1/campus01/lab01/lighting/+/#" -v
```

Assinar tudo do `lab01`:

```powershell
npx.cmd --yes mqtt sub -h broker.hivemq.com -p 1883 -t "mackenzie/iot/v1/campus01/lab01/#" -v
```

## Alternativa com Docker e Mosquitto client

Esta alternativa exige Docker instalado.

Assinar tudo do dispositivo:

```powershell
docker run --rm -it eclipse-mosquitto:2 mosquitto_sub -h broker.hivemq.com -p 1883 -t "mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/#" -v
```

Publicar comando de status:

```powershell
docker run --rm -it eclipse-mosquitto:2 mosquitto_pub -h broker.hivemq.com -p 1883 -t "mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/commands" -m "status"
```

Ligar a lampada:

```powershell
docker run --rm -it eclipse-mosquitto:2 mosquitto_pub -h broker.hivemq.com -p 1883 -t "mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/commands" -m "light:on"
```

Desligar a lampada:

```powershell
docker run --rm -it eclipse-mosquitto:2 mosquitto_pub -h broker.hivemq.com -p 1883 -t "mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/commands" -m "light:off"
```

Voltar para o modo automatico:

```powershell
docker run --rm -it eclipse-mosquitto:2 mosquitto_pub -h broker.hivemq.com -p 1883 -t "mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/commands" -m "mode:auto"
```

## MQTTX

MQTTX e uma interface grafica para MQTT. Use quando quiser visualizar mensagens sem terminal. Configure host `broker.hivemq.com`, porta `1883`, sem usuario e sem senha, e assine:

`mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/#`
