# MQTT pelo VS Code

Este documento explica como o projeto usa MQTT e como testar as mensagens diretamente pelo VS Code, sem depender do myMQTT aplicativo no celular.

## 1. MQTT

MQTT é um protocolo leve de publish/subscribe muito usado em IoT. Ele permite que dispositivos e aplicações troquem mensagens por meio de um broker.

No projeto:

```text
ESP32 simulado publica telemetry, events e status
ESP32 simulado assina commands
Terminal, collector e dashboard também são clientes MQTT
Broker entrega as mensagens entre todos
```

## 2. Conceitos principais

| Conceito | Explicação no projeto |
|---|---|
| Broker | Servidor MQTT que recebe e distribui mensagens. |
| Publisher | Cliente que publica mensagens em um tópico. |
| Subscriber | Cliente que assina tópicos e recebe mensagens. |
| Dispositivo | ESP32 simulado no Wokwi. |
| Cliente MQTT | Qualquer programa conectado ao broker: ESP32, collector Python, dashboard, npm mqtt, MQTTX etc. |

Broker padrão:

```text
broker.hivemq.com:1883
```

Broker alternativo no firmware:

```text
test.mosquitto.org:1883
```

A troca do broker no firmware é feita alterando a constante `MQTT_BROKER_ATIVO` em `src/main.cpp`.

## 3. Estrutura dos tópicos

O padrão adotado é:

```text
mackenzie/iot/v1/{site}/{area}/{domain}/{device_id}/{channel}
```

Configuração deste projeto:

```text
Root:      mackenzie/iot/v1
Site:      campus01
Area:      lab01
Domain:    lighting
Device ID: esp32_01
```

Tópicos finais:

```text
mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/telemetry
mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/events
mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/status
mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/commands
```

## 4. Canais usados

| Canal | Direção | Uso |
|---|---|---|
| `telemetry` | ESP32 → broker | Leituras periódicas de lux, presença, modo e lâmpada. |
| `events` | ESP32 → broker | Eventos importantes, como presença em ambiente escuro. |
| `status` | ESP32 → broker | Estado atual do dispositivo. |
| `commands` | broker → ESP32 | Comandos remotos enviados por terminal ou dashboard. |

## 5. Payload de telemetry

Exemplo:

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

## 6. Payload de events

Exemplo:

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

## 7. Payload de status

Exemplo:

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

## 8. Comandos aceitos

No tópico `commands`, o ESP32 aceita:

```text
status
light:on
light:off
mode:auto
```

Comportamento esperado:

| Comando | Resultado |
|---|---|
| `status` | ESP32 publica status atualizado. |
| `light:on` | Liga a lâmpada e entra em modo manual. |
| `light:off` | Desliga a lâmpada e entra em modo manual. |
| `mode:auto` | Retorna para a regra automática de presença + luminosidade. |

## 9. Forma recomendada: npm scripts

Instale as dependências uma vez:

```powershell
npm install
```

Assinar tudo do dispositivo:

```powershell
npm run mqtt:sub:device
```

Publicar status:

```powershell
npm run mqtt:pub:status
```

Ligar a lâmpada:

```powershell
npm run mqtt:pub:light:on
```

Desligar a lâmpada:

```powershell
npm run mqtt:pub:light:off
```

Voltar ao modo automático:

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

## 10. Teste rápido com npx

O `npx` executa a CLI do pacote `mqtt` sem instalação global.

Assinar tudo do dispositivo:

```powershell
npx.cmd --yes mqtt sub -h broker.hivemq.com -p 1883 -t "mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/#" -v
```

Publicar comando:

```powershell
npx.cmd --yes mqtt pub -h broker.hivemq.com -p 1883 -t "mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/commands" -m "status"
```

Troque a mensagem para testar outros comandos:

```powershell
-m "light:on"
-m "light:off"
-m "mode:auto"
```

## 11. Alternativa com Docker e Mosquitto client

Esta alternativa exige Docker.

Assinar tudo do dispositivo:

```powershell
docker run --rm -it eclipse-mosquitto:2 mosquitto_sub -h broker.hivemq.com -p 1883 -t "mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/#" -v
```

Publicar comando:

```powershell
docker run --rm -it eclipse-mosquitto:2 mosquitto_pub -h broker.hivemq.com -p 1883 -t "mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/commands" -m "status"
```

## 12. MQTTX

MQTTX é uma interface gráfica para MQTT. Use se quiser visualizar mensagens sem terminal.

Configuração:

```text
Host: broker.hivemq.com
Porta: 1883
Usuário: vazio
Senha: vazio
```

Tópico para assinar:

```text
mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/#
```
