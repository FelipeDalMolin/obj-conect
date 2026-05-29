# Obj Conect — IoT simulado com ESP32, Wokwi, MQTT, TinyDB e Streamlit

Este projeto demonstra uma solução de **iluminação inteligente simulada** usando ESP32 no Wokwi, sensores de luminosidade e presença, comunicação MQTT, coleta local em Python com TinyDB e visualização em Streamlit.

A proposta é transformar uma simulação simples do Wokwi em um projeto mais organizado e próximo de uma solução IoT real: com firmware versionado, build pelo PlatformIO, tópicos MQTT padronizados, comandos remotos, coleta de dados, armazenamento local e dashboard.

O projeto não exige hardware físico. Toda a demonstração pode ser feita no VS Code com Wokwi, MQTT, Python e Streamlit.

---

## 1. O que o projeto faz

O ESP32 simulado lê dois sensores:

* **LDR**, usado para estimar a luminosidade do ambiente.
* **PIR**, usado para detectar presença ou movimento.

Com essas informações, o firmware controla uma lâmpada simulada por um LED.

No modo automático, a lâmpada liga somente quando duas condições são verdadeiras:

```text
há presença detectada
+
o ambiente está escuro
```

Também é possível controlar a lâmpada remotamente por MQTT usando comandos como:

```text
status
light:on
light:off
mode:auto
```

Além da simulação, o projeto possui:

* firmware ESP32 em Arduino/C++ com PlatformIO;
* simulação Wokwi dentro do VS Code;
* comunicação MQTT com broker público;
* collector Python para salvar mensagens em TinyDB;
* dashboard Streamlit para visualizar dados e enviar comandos.

---

## 2. Arquitetura geral

```text
Wokwi / ESP32 simulado
  ├── LDR no GPIO 34
  ├── PIR no GPIO 26
  └── LED no GPIO 12
        ↓
Firmware Arduino/C++ com PlatformIO
        ↓ MQTT
Broker público MQTT
        ↓
Collector Python
        ↓
TinyDB local
        ↓
Dashboard Streamlit
```

O broker MQTT padrão usado pelo projeto é:

```text
broker.hivemq.com:1883
```

O broker alternativo configurável no firmware é:

```text
test.mosquitto.org:1883
```

---

## 3. Estrutura do projeto

A estrutura principal do projeto é:

```text
obj-conect/
├── README.md
├── platformio.ini
├── wokwi.toml
├── diagram.json
├── package.json
├── package-lock.json
├── requirements.txt
├── .gitignore
│
├── src/
│   └── main.cpp
│
├── include/
├── lib/
├── test/
│
├── apps/
│   └── dashboard/
│       ├── app.py
│       └── pages/
│           ├── 1_live_monitor.py
│           ├── 2_devices.py
│           ├── 3_commands.py
│           └── 4_data_explorer.py
│
├── iot_core/
│   ├── settings.py
│   ├── topics.py
│   ├── storage_tinydb.py
│   ├── mqtt_client.py
│   ├── models.py
│   ├── dashboard_queries.py
│   └── command_publisher.py
│
├── tools/
│   └── collector/
│       └── mqtt_collector.py
│
├── configs/
│   ├── mqtt.yaml
│   ├── devices.yaml
│   └── environments.yaml
│
├── data/
│   ├── local/
│   ├── raw/
│   └── exports/
│
└── docs/
    ├── contexto-extraido.md
    ├── mqtt.md
    ├── data-collection.md
    ├── dashboard.md
    ├── troubleshooting.md
    └── roteiro-video.md
```

Os arquivos abaixo são gerados localmente durante a execução e não devem ser versionados no Git:

```text
.pio/
.venv/
node_modules/
data/local/iot_data.json
data/local/iot_config.json
```

---

## 4. Pré-requisitos em uma máquina nova

Para rodar o projeto em outra máquina, instale:

```text
Git
VS Code
Node.js com npm
Python 3.11 ou superior
Extensão PlatformIO IDE no VS Code
Extensão Wokwi Simulator no VS Code
```

Também é recomendado instalar:

```text
Extensão C/C++ Extension Pack no VS Code
GitHub CLI, se quiser criar/publicar repositório pelo terminal
Docker Desktop, opcional, para testar MQTT com Mosquitto client via container
MQTTX, opcional, para depuração visual de mensagens MQTT
```

---

## 5. Clonar o projeto

Escolha uma pasta para seus projetos. No Windows, uma sugestão é:

```powershell
mkdir "$env:USERPROFILE\projetos"
cd "$env:USERPROFILE\projetos"
```

Clone o repositório:

```powershell
git clone https://github.com/SEU_USUARIO/obj-conect.git obj-conect
cd obj-conect
```

O comando será parecido com:

```powershell
git clone https://github.com/FelipeDalMolin/obj-conect.git obj-conect
cd obj-conect
```

Abra o projeto no VS Code:

```powershell
code .
```

Importante: abra a pasta `obj-conect`, não a pasta `.git`.

---

## 6. Conferir se as ferramentas estão disponíveis

No terminal do VS Code, rode:

```powershell
git --version
node --version
npm --version
python --version
code --version
```

Se algum comando não for reconhecido, instale a ferramenta correspondente ou corrija o `PATH` do Windows.

---

## 7. Instalar extensões no VS Code

No VS Code, abra a aba de extensões e instale:

```text
PlatformIO IDE
Wokwi Simulator
C/C++ Extension Pack ou C/C++
```

Depois de instalar o **PlatformIO IDE**, aguarde alguns minutos. Na primeira execução, ele pode baixar componentes internos, preparar o PlatformIO Core e configurar o ambiente do VS Code.

Se o PlatformIO pedir reinício do VS Code, reinicie.

### 7.1 Validar o PlatformIO

Depois da instalação, abra o PlatformIO pela barra lateral do VS Code.

Você deve conseguir acessar:

```text
PlatformIO Home
```

ou, pelo menu da extensão:

```text
PlatformIO → Project Tasks
```

Se o projeto já tiver sido clonado corretamente, o PlatformIO deve reconhecer o arquivo:

```text
platformio.ini
```

na raiz do projeto.

### 7.2 Solicitar licença do Wokwi no VS Code

Depois de instalar a extensão **Wokwi Simulator**, será necessário solicitar/ativar a licença da extensão no VS Code.

No VS Code:

```text
1. Pressione Ctrl + Shift + P.
2. Pesquise por Wokwi: Request a new License.
3. Selecione o comando.
4. Siga o fluxo de autenticação indicado pelo navegador.
5. Volte para o VS Code após concluir o login/autorização.
```

Se a licença já estiver ativa nessa máquina, essa etapa pode não ser necessária.

### 7.3 Validar se o Wokwi está disponível

Com o projeto aberto no VS Code, pressione:

```text
Ctrl + Shift + P
```

Depois pesquise por:

```text
Wokwi: Start Simulator
```

Não inicie a simulação ainda se o firmware não tiver sido compilado. Primeiro será necessário fazer o build pelo PlatformIO, porque o Wokwi usa os arquivos gerados em:

```text
.pio/build/esp32dev/firmware.bin
.pio/build/esp32dev/firmware.elf
```

Esses arquivos são gerados na etapa de build do PlatformIO.


## 8. Preparar dependências Node/npm

O projeto usa Node/npm para scripts de teste MQTT no terminal.

Na raiz do projeto:

```powershell
npm install
```

Esse comando cria a pasta `node_modules/`, que não deve ir para o Git.

Para verificar os scripts disponíveis:

```powershell
npm run
```

Você deve ver scripts como:

```text
mqtt:sub:device
mqtt:pub:status
mqtt:pub:light:on
mqtt:pub:light:off
mqtt:pub:mode:auto
```

---

## 9. Preparar ambiente Python

O collector MQTT e o dashboard Streamlit usam Python.

Na raiz do projeto, crie o ambiente virtual:

```powershell
python -m venv .venv
```

Instale as dependências:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Valide os imports principais:

```powershell
.\.venv\Scripts\python.exe -c "import paho.mqtt.client, tinydb, yaml, dotenv, pandas, streamlit, plotly; print('imports ok')"
```

Valide a sintaxe dos módulos Python:

```powershell
.\.venv\Scripts\python.exe -m compileall iot_core tools apps
```

Se aparecer `imports ok`, o ambiente Python está pronto.

---

## 10. Etapa PlatformIO — compilar o firmware ESP32

O firmware principal está em:

```text
src/main.cpp
```

O ambiente PlatformIO está configurado em:

```text
platformio.ini
```

O conteúdo esperado é semelhante a:

```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino

lib_deps =
    knolleary/PubSubClient
    bblanchon/ArduinoJson
```

### 10.1 Build pelo botão do VS Code

No VS Code:

```text
1. Clique no ícone do PlatformIO na barra lateral.
2. Abra Project Tasks.
3. Selecione esp32dev.
4. Clique em Build.
```

Esse é o caminho mais simples quando a máquina ainda não reconhece `pio` no terminal.

### 10.2 Build pelo terminal

Se o PlatformIO estiver instalado no caminho padrão do usuário Windows, rode:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run
```

O resultado esperado é algo parecido com:

```text
[SUCCESS]
```

### 10.3 Se `pio` não for reconhecido

Em algumas máquinas, este comando pode falhar:

```powershell
pio run
```

Isso não significa que o PlatformIO não funciona. Pode ser apenas que o comando `pio` não esteja no `PATH`.

Teste:

```powershell
Test-Path "$env:USERPROFILE\.platformio\penv\Scripts\pio.exe"
```

Se retornar `True`, rode:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\pio.exe" run
```

Também é possível continuar usando o botão **Build** da extensão PlatformIO.

---

## 11. Etapa Wokwi — rodar a simulação no VS Code

O Wokwi usa dois arquivos principais na raiz do projeto:

```text
diagram.json
wokwi.toml
```

O `diagram.json` descreve o circuito simulado.

O `wokwi.toml` aponta para o firmware gerado pelo PlatformIO:

```toml
[wokwi]
version = 1
firmware = ".pio/build/esp32dev/firmware.bin"
elf = ".pio/build/esp32dev/firmware.elf"
```

Por isso, antes de iniciar a simulação, rode o build do PlatformIO.


### 11.1 Iniciar simulador

Depois do build:

```text
1. Pressione Ctrl + Shift + P.
2. Procure por Wokwi: Start Simulator.
3. Aguarde a simulação iniciar.
```

O ESP32 deve:

```text
conectar no Wi-Fi simulado Wokwi-GUEST
conectar ao broker MQTT
assinar o tópico commands
publicar status/telemetry/events
```

### 11.2 Manipular sensores no Wokwi

No simulador:

```text
LDR:
  altere a luminosidade no componente do fotoresistor.

PIR:
  acione o sensor de movimento/presença.

LED:
  representa a lâmpada simulada.
```

No modo automático, o LED deve acender apenas quando houver presença e o ambiente estiver escuro.

---

## 12. Testar MQTT pelo terminal

O projeto usa tópicos no padrão:

```text
mackenzie/iot/v1/{site}/{area}/{domain}/{device_id}/{channel}
```

Neste projeto:

```text
site = campus01
area = lab01
domain = lighting
device_id = esp32_01
```

Os tópicos principais são:

```text
mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/telemetry
mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/events
mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/status
mackenzie/iot/v1/campus01/lab01/lighting/esp32_01/commands
```

### 12.1 Assinar mensagens do dispositivo

Em um terminal:

```powershell
npm run mqtt:sub:device
```

Esse terminal ficará aguardando mensagens MQTT.

### 12.2 Publicar comandos

Em outro terminal:

```powershell
npm run mqtt:pub:status
npm run mqtt:pub:light:on
npm run mqtt:pub:light:off
npm run mqtt:pub:mode:auto
```

Comportamento esperado:

```text
status:
  solicita status do ESP32.

light:on:
  liga a lâmpada e muda para modo manual.

light:off:
  desliga a lâmpada e muda para modo manual.

mode:auto:
  retorna para o modo automático.
```

Para mais detalhes, veja:

```text
docs/mqtt.md
```

---

## 13. Rodar o collector Python

O collector escuta mensagens MQTT e salva histórico local em TinyDB.

Em um terminal:

```powershell
.\.venv\Scripts\python.exe -m tools.collector.mqtt_collector
```

Ele assina:

```text
mackenzie/iot/v1/campus01/lab01/lighting/+/+
```

E cria os arquivos locais:

```text
data/local/iot_data.json
data/local/iot_config.json
```

Esses arquivos ficam fora do Git.

Para apenas inicializar os bancos locais:

```powershell
.\.venv\Scripts\python.exe -m tools.collector.mqtt_collector --init-only
```

Para uma demonstração curta com limite de mensagens:

```powershell
.\.venv\Scripts\python.exe -m tools.collector.mqtt_collector --message-limit 4
```

Mais detalhes:

```text
docs/data-collection.md
```

---

## 14. Rodar o dashboard Streamlit

O dashboard lê o TinyDB e permite enviar comandos MQTT pela interface.

Em outro terminal, sempre a partir da raiz do projeto:

```powershell
.\.venv\Scripts\python.exe -m streamlit run apps\dashboard\app.py
```

O Streamlit abrirá no navegador, normalmente em:

```text
http://localhost:8501
```

O dashboard possui páginas para:

```text
Home:
  resumo do projeto, broker, devices e contagens do TinyDB.

Live Monitor:
  visão ao vivo da última telemetria, lux, presença, modo e lâmpada.

Devices:
  lista de dispositivos configurados e último estado conhecido.

Commands:
  botões para status, light:on, light:off e mode:auto.

Data Explorer:
  visualização das tabelas TinyDB e mensagens brutas.
```

O Streamlit não grava comandos diretamente no TinyDB. Ele publica comandos no broker MQTT. O collector, se estiver rodando, recebe a mensagem e registra no TinyDB.

Mais detalhes:

```text
docs/dashboard.md
```

---

## 15. Fluxo completo recomendado

Para demonstrar o projeto funcionando, abra três partes:

### Terminal 1 — collector

```powershell
.\.venv\Scripts\python.exe -m tools.collector.mqtt_collector
```

### Terminal 2 — dashboard

```powershell
.\.venv\Scripts\python.exe -m streamlit run apps\dashboard\app.py
```

### VS Code — Wokwi

```text
Ctrl + Shift + P
Wokwi: Start Simulator
```

Depois:

```text
1. Abra a página Live Monitor no dashboard.
2. Confirme se há dados de telemetry.
3. Abra a página Commands.
4. Clique em Light on.
5. Veja o LED acender no Wokwi.
6. Clique em Light off.
7. Veja o LED apagar.
8. Clique em Mode auto.
9. Manipule LDR e PIR no Wokwi.
10. Veja a lâmpada responder à regra automática.
11. Abra Data Explorer e confira commands, telemetry, events e raw_messages.
```

---

## 16. Tópicos MQTT e payloads

### Telemetry

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

### Events

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

### Status

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

### Commands

O canal `commands` aceita:

```text
status
light:on
light:off
mode:auto
```

---

## 17. Dados locais e Git

Os dados locais ficam em:

```text
data/local/iot_data.json
data/local/iot_config.json
```

Eles são gerados pelo collector e ignorados pelo Git.

O `.gitignore` deve proteger:

```gitignore
.pio/
.venv/
node_modules/
.env
data/local/*.json
data/raw/*.ndjson
data/exports/*.csv
__pycache__/
*.pyc
```

Se quiser conferir o que o Git está ignorando:

```powershell
git status --short --ignored
```

---

## 18. Troubleshooting rápido

### PlatformIO não compila

Tente pelo botão **Build** da extensão PlatformIO.

Ou rode:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run
```

### `pio` não é reconhecido

Use o caminho completo:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\pio.exe" run
```

### Wokwi não inicia

Confira se o firmware foi gerado:

```text
.pio/build/esp32dev/firmware.bin
.pio/build/esp32dev/firmware.elf
```

Se não existir, rode o build PlatformIO antes.

### MQTT não conecta

Teste primeiro no terminal:

```powershell
npm run mqtt:sub:device
```

Em outro terminal:

```powershell
npm run mqtt:pub:status
```

Se nem o terminal conectar, pode ser instabilidade do broker público ou bloqueio de rede.

### Collector não grava dados

Confira se ele está rodando:

```powershell
.\.venv\Scripts\python.exe -m tools.collector.mqtt_collector
```

Confira se o Wokwi ou os scripts MQTT estão publicando mensagens.

### Dashboard vazio

Rode, nesta ordem:

```text
collector
Wokwi
dashboard
```

Depois envie comandos ou altere sensores no Wokwi.

Mais detalhes:

```text
docs/troubleshooting.md
```

---

## 19. Documentação complementar

```text
docs/contexto-extraido.md
```

Resumo das decisões técnicas, origem do projeto e ajustes feitos na migração para PlatformIO/Wokwi.

```text
docs/mqtt.md
```

Explica broker, tópicos, payloads, comandos e formas de testar MQTT pelo VS Code.

```text
docs/data-collection.md
```

Explica o collector Python, TinyDB, payloads normalizados e armazenamento local.

```text
docs/dashboard.md
```

Explica o dashboard Streamlit, páginas, polling leve e comandos via interface.

```text
docs/testes-resultados-mqtt.md
```

Documenta os testes MQTT, metodologia de medição, tabela de resultados, diagramas e capturas recomendadas.

```text
docs/troubleshooting.md
```

Ajuda com erros comuns de PlatformIO, Wokwi, MQTT, collector e dashboard.

```text
docs/roteiro-video.md
```

Roteiro sugerido para gravar a demonstração do projeto funcionando.

---

## 20. Limitações atuais

Esta versão é uma simulação didática e local.

Ela ainda não possui:

```text
hardware físico
broker MQTT próprio
autenticação
TLS
controle de usuários
banco de produção
alta disponibilidade
pipeline CI/CD
```

O TinyDB é adequado para protótipo, demonstração e baixo volume. Para produção, o ideal é considerar bancos mais robustos como PostgreSQL, TimescaleDB, InfluxDB, SQLite com schema definido ou DuckDB/Parquet para análises locais.

---

## 21. Possíveis evoluções

Próximas etapas sugeridas:

```text
v0.4 — página de configuração de ambientes e dispositivos
v0.5 — relatório de economia estimada e ODS 11
v0.6 — simulador de múltiplos dispositivos
v0.7 — exportação analítica com DuckDB/Parquet
v0.8 — broker Mosquitto próprio com autenticação
v0.9 — InfluxDB ou TimescaleDB para séries temporais
v1.0 — preparação para ambiente mais próximo de produção
```

Uma evolução real também precisaria considerar segurança elétrica, relés ou drivers adequados, autenticação dos dispositivos, criptografia, gerenciamento de falhas e medição real de consumo energético.

---

## 22. Resumo de comandos principais

Instalar Node:

```powershell
npm install
```

Criar ambiente Python:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Build PlatformIO:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run
```

Rodar collector:

```powershell
.\.venv\Scripts\python.exe -m tools.collector.mqtt_collector
```

Rodar dashboard:

```powershell
.\.venv\Scripts\python.exe -m streamlit run apps\dashboard\app.py
```

Assinar MQTT:

```powershell
npm run mqtt:sub:device
```

Enviar comandos:

```powershell
npm run mqtt:pub:status
npm run mqtt:pub:light:on
npm run mqtt:pub:light:off
npm run mqtt:pub:mode:auto
```

Iniciar Wokwi:

```text
Ctrl + Shift + P
Wokwi: Start Simulator
```
