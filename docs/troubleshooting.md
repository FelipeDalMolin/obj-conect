# Troubleshooting

Este documento reúne problemas comuns e formas de diagnóstico.

## 1. PlatformIO não encontra a placa

Confirme se o `platformio.ini` contém:

```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
```

Depois tente compilar novamente:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run
```

Também é possível usar o botão **Build** da extensão PlatformIO no VS Code.

## 2. Build falha por biblioteca ausente

Confirme as dependências em `platformio.ini`:

```ini
lib_deps =
    knolleary/PubSubClient
    bblanchon/ArduinoJson
```

Depois rode o build:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run
```

## 3. O comando `pio` não é reconhecido

Se o PowerShell não reconhecer `pio`, use o caminho completo:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run
```

Outra opção é usar o terminal próprio do PlatformIO no VS Code.

## 4. Wokwi não abre o firmware do PlatformIO

Confirme o `wokwi.toml`:

```toml
[wokwi]
version = 1
firmware = ".pio/build/esp32dev/firmware.bin"
elf = ".pio/build/esp32dev/firmware.elf"
```

Antes de iniciar a simulação, faça o build do PlatformIO para gerar:

```text
.pio/build/esp32dev/firmware.bin
.pio/build/esp32dev/firmware.elf
```

## 5. Como trocar entre HiveMQ e Mosquitto

No arquivo `src/main.cpp`, altere:

```cpp
static const MqttBrokerId MQTT_BROKER_ATIVO = BROKER_HIVEMQ;
```

para:

```cpp
static const MqttBrokerId MQTT_BROKER_ATIVO = BROKER_MOSQUITTO;
```

Depois rode o build e reinicie a simulação.

## 6. MQTT `rc=-2`

No PubSubClient, `rc=-2` indica falha de conexão TCP ou falha ao alcançar o servidor MQTT.

Na prática, o ESP32 simulado não conseguiu abrir conexão com o broker configurado.

Verifique:

- se o Wokwi conectou no Wi-Fi `Wokwi-GUEST`;
- se o broker público está respondendo;
- se host e porta estão corretos;
- se o terminal do VS Code consegue assinar o mesmo broker;
- se existe oscilação do broker público.

## 7. Como isolar problema de MQTT

Primeiro teste pelo PC:

```powershell
npm run mqtt:sub:device
```

Em outro terminal:

```powershell
npm run mqtt:pub:status
```

Se o terminal recebe a mensagem, mas o ESP32 não conecta, o problema provavelmente está no Wokwi, no Wi-Fi simulado ou no firmware.

Se o terminal também não conecta, o problema pode estar no broker, na rede local ou em bloqueio temporário.

## 8. A lâmpada não acende no modo automático

No modo `auto`, a lâmpada só liga quando as duas condições são verdadeiras:

```text
presence = true
light_condition = dark
```

No Wokwi:

1. reduza a luminosidade do LDR;
2. acione o PIR;
3. observe o LED e o Serial Monitor.

## 9. `light:on` liga a lâmpada, mas ela não volta sozinha ao automático

O comando `light:on` muda `control_mode` para `manual`.

Para voltar à automação:

```powershell
npm run mqtt:pub:mode:auto
```

## 10. Collector não recebe mensagens

Confirme que ele está rodando:

```powershell
.\.venv\Scripts\python.exe -m tools.collector.mqtt_collector
```

Confirme o tópico assinado:

```text
mackenzie/iot/v1/campus01/lab01/lighting/+/+
```

Depois publique um comando:

```powershell
npm run mqtt:pub:status
```

Se ainda não gravar, abra um subscriber paralelo:

```powershell
npm run mqtt:sub:device
```

Se o subscriber receber e o collector não, revise o collector, o parser de tópicos e os logs do Python.

## 11. TinyDB não aparece

Rode:

```powershell
.\.venv\Scripts\python.exe -m tools.collector.mqtt_collector --init-only
```

Depois confira:

```powershell
Test-Path .\data\local\iot_data.json
Test-Path .\data\local\iot_config.json
```

Esses arquivos são ignorados pelo Git e gerados localmente.

## 12. Dashboard abre, mas não mostra dados

Verifique:

1. se o collector está rodando;
2. se o Wokwi está publicando;
3. se há mensagens em `data/local/iot_data.json`;
4. se o dashboard foi iniciado a partir da raiz do projeto.

Comando correto:

```powershell
.\.venv\Scripts\python.exe -m streamlit run apps\dashboard\app.py
```

## 13. Dashboard não atualiza no Live Monitor

O Live Monitor verifica alterações em `data/local/iot_data.json`.

Se nada muda:

- o collector pode não estar recebendo mensagens;
- o Wokwi pode não estar publicando;
- o comando pode ter sido publicado em outro tópico;
- o TinyDB pode não ter sido alterado.

Faça um teste:

```powershell
npm run mqtt:pub:light:on
```

Com o collector rodando, isso deve alterar o TinyDB e o Live Monitor deve atualizar em até alguns segundos.

## 14. Erro de importação Python

Sempre rode comandos a partir da raiz do projeto:

```powershell
cd C:\Users\Felipe\projetos\obj-conect
```

E use:

```powershell
.\.venv\Scripts\python.exe -m streamlit run apps\dashboard\app.py
```

Se necessário, reinstale dependências:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 15. Justificativa de não usar broker local nesta etapa

O projeto está focado em Wokwi no VS Code e brokers públicos simples. Broker local exigiria configuração adicional de rede e, em alguns casos, uso de Wokwi IoT Gateway.

A evolução pode e deve ser feita ao aproximar o projeto de um ambiente de produção.
