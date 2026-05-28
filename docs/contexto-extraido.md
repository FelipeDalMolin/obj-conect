# Informacoes aproveitadas

- Projeto baseado em ESP32 DevKit no Wokwi.
- Firmware original em Arduino usava WiFi, PubSubClient, LDR, PIR e LED.
- Dependencia MQTT indicada: PubSubClient.
- O projeto PlatformIO atual tambem usa ArduinoJson para montar os payloads JSON.
- LDR conectado pela saida analogica AO.
- PIR conectado pela saida digital OUT.
- LED com resistor em serie como atuador visual da lampada simulada.

## Ajustes aplicados no projeto final

- Codigo principal migrado para `src/main.cpp`.
- PIR ajustado para `GPIO 26`, conforme requisito do projeto.
- LDR AO mantido em `GPIO 34`.
- LED mantido em `GPIO 12`.
- Conexao incorreta anterior do LED removida do `diagram.json`.
- Catodo do LED ligado ao GND.
- Topicos MQTT reorganizados no padrao `mackenzie/iot/v1/{site}/{area}/{domain}/{device_id}/{channel}`.
- Payloads publicados em JSON usando ArduinoJson.

## Escopo de simulacao

Este projeto foi preparado para execucao no Wokwi dentro do VS Code com PlatformIO. Nao ha requisito de upload para hardware fisico.
