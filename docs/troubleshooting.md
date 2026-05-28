# Troubleshooting

## PlatformIO nao encontra a placa

Confirme que o `platformio.ini` contem:

```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
```

## Build falha por biblioteca ausente

Confirme as dependencias em `platformio.ini`:

```ini
lib_deps =
    knolleary/PubSubClient
    bblanchon/ArduinoJson
```

Depois rode:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run
```

## Wokwi nao abre o firmware do PlatformIO

Confirme o `wokwi.toml`:

```toml
[wokwi]
version = 1
firmware = ".pio/build/esp32dev/firmware.bin"
elf = ".pio/build/esp32dev/firmware.elf"
```

Antes de iniciar a simulacao, rode o build do PlatformIO para gerar os arquivos dentro de `.pio/build/esp32dev/`.

Referencia Wokwi para WiFi no ESP32:

`https://docs.wokwi.com/guides/esp32-wifi`

## Como trocar entre HiveMQ e Mosquitto

No `src/main.cpp`, altere:

```cpp
static const MqttBrokerId MQTT_BROKER_ATIVO = BROKER_HIVEMQ;
```

Para:

```cpp
static const MqttBrokerId MQTT_BROKER_ATIVO = BROKER_MOSQUITTO;
```

Depois rode o build e reinicie a simulacao.

## MQTT rc=-2

No PubSubClient, `rc=-2` significa falha na conexao TCP ou no servidor MQTT. Na pratica, o ESP32 simulado nao conseguiu abrir conexao com o broker configurado.

Verifique:

- se o Wokwi conectou no WiFi `Wokwi-GUEST`;
- se o broker publico esta respondendo;
- se o host e a porta estao corretos;
- se o terminal do VS Code consegue assinar o mesmo broker;
- se ha bloqueio temporario de rede ou oscilacao do broker publico.

## Como isolar o problema

Teste o cliente do PC primeiro:

```powershell
npm run mqtt:sub:device
```

Em outro terminal:

```powershell
npm run mqtt:pub:status
```

Se o terminal recebe a mensagem mas o ESP32 nao conecta, o problema provavelmente esta no Wokwi, no WiFi simulado ou no firmware.

Se o terminal tambem nao conecta, teste o broker alternativo no firmware e nos comandos, ou aguarde alguns minutos. Brokers publicos podem oscilar, reiniciar ou limitar conexoes.

## Por que nao usar broker local nesta etapa

O projeto esta focado em Wokwi no VS Code e em brokers publicos simples. Broker local exige rede local acessivel ao simulador, configuracao adicional e, em alguns casos, Wokwi IoT Gateway. Isso fica fora desta etapa para manter a evolucao pequena.

## A lampada nao acende em modo automatico

No modo `auto`, a lampada liga somente quando as duas condicoes forem verdadeiras:

- PIR detecta presenca no `GPIO 26`;
- LDR indica ambiente escuro pelo `GPIO 34`.

No Wokwi, ajuste a luminosidade do sensor LDR e acione o PIR para testar.

## O comando light:on muda para modo manual

O comando `light:on` liga a lampada e muda `control_mode` para `manual`. Isso impede que a regra automatica desligue o LED imediatamente no proximo loop.

Use:

```powershell
npm run mqtt:pub:mode:auto
```

Para voltar ao modo automatico.

## Como confirmar mensagens MQTT

Assine tudo do dispositivo:

```powershell
npm run mqtt:sub:device
```

Rode a simulacao e observe:

- `status` quando o ESP32 conecta;
- `telemetry` periodicamente;
- `events` quando ha transicao para presenca em ambiente escuro;
- logs `MQTT PUB`, `MQTT SUB`, `MQTT CMD RECEIVED`, `MQTT MODE` e `MQTT ERROR` no Serial Monitor.
