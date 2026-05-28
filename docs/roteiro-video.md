# Roteiro de video

## 1. Apresentacao do objetivo

Mostrar um sistema de lighting inteligente simulado no Wokwi, usando ESP32, LDR, PIR, LED, MQTT, payloads JSON e teste pelo terminal integrado do VS Code.

## 2. Ambiente

- VS Code com PlatformIO.
- Wokwi rodando dentro do VS Code.
- Framework Arduino/C++.
- ESP32 Dev Module.
- Sem hardware fisico.

## 3. Circuito no Wokwi

Mostrar o `diagram.json` ativo:

- LDR AO conectado ao `GPIO 34`.
- PIR OUT conectado ao `GPIO 26`.
- LED com resistor conectado ao `GPIO 12`.
- Catodo do LED conectado ao GND.

## 4. Firmware

Abrir `src/main.cpp` e destacar:

- Broker selecionavel entre HiveMQ e Mosquitto.
- Topicos montados por constantes.
- Canais `telemetry`, `events`, `status` e `commands`.
- Payloads JSON com ArduinoJson.
- Modo `auto` e modo `manual`.
- Logs `MQTT CONNECT`, `MQTT SUB`, `MQTT PUB`, `MQTT CMD RECEIVED`, `MQTT MODE` e `MQTT ERROR`.

## 5. Terminal assinando mensagens

No terminal integrado, rodar:

```powershell
npm run mqtt:sub:device
```

Mostrar as mensagens chegando enquanto a simulacao roda.

## 6. Status remoto

Em outro terminal, rodar:

```powershell
npm run mqtt:pub:status
```

Mostrar:

- comando recebido no Serial Monitor;
- resposta do ESP32 no topico `status`;
- log `MQTT CMD RECEIVED`;
- log `MQTT PUB`.

## 7. Controle manual da lampada

Ligar remotamente:

```powershell
npm run mqtt:pub:light:on
```

Mostrar o LED acendendo e o payload de `status` com `control_mode` igual a `manual` e `lamp_state` igual a `on`.

Desligar remotamente:

```powershell
npm run mqtt:pub:light:off
```

Mostrar o LED apagando e o payload de `status` atualizado.

## 8. Volta ao modo automatico

Rodar:

```powershell
npm run mqtt:pub:mode:auto
```

Manipular lux e presenca no simulador:

- com ambiente claro, o LED fica apagado;
- com ambiente escuro e presenca, o LED acende;
- ao entrar nessa condicao, o ESP32 publica no canal `events` apenas na transicao.

## 9. Encerramento

Reforcar que a demonstracao nao depende de app no celular. A forma recomendada e usar os scripts npm do projeto; `npx` e Docker/Mosquitto ficam como alternativas.
