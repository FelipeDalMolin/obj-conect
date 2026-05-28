#include <Arduino.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <math.h>

static const char WIFI_SSID[] = "Wokwi-GUEST";
static const char WIFI_PASSWORD[] = "";
static const int WIFI_CHANNEL = 6;

static const uint8_t LDR_PIN = 34;
static const uint8_t PIR_PIN = 26;
static const uint8_t LED_PIN = 12;

static const float LDR_GAMMA = 0.7f;
static const float LDR_RL10 = 33.0f;
static const float LUX_DARK_THRESHOLD = 400.0f;

enum MqttBrokerId {
  BROKER_HIVEMQ,
  BROKER_MOSQUITTO
};

struct MqttBrokerConfig {
  const char *nome;
  const char *host;
  uint16_t porta;
};

static const MqttBrokerId MQTT_BROKER_ATIVO = BROKER_HIVEMQ;
static const MqttBrokerConfig MQTT_BROKERS[] = {
    {"HiveMQ Public Broker", "broker.hivemq.com", 1883},
    {"Mosquitto Test Broker", "test.mosquitto.org", 1883},
};

static const char MQTT_ROOT[] = "mackenzie/iot/v1";
static const char MQTT_SITE[] = "campus01";
static const char MQTT_AREA[] = "lab01";
static const char MQTT_DOMAIN[] = "lighting";
static const char DEVICE_ID[] = "esp32_01";
static const char FIRMWARE_VERSION[] = "0.1.0";
static const char SOURCE[] = "wokwi";

static const String BASE_TOPIC =
    String(MQTT_ROOT) + "/" + MQTT_SITE + "/" + MQTT_AREA + "/" + MQTT_DOMAIN + "/" + DEVICE_ID;
static const String TOPIC_TELEMETRY = BASE_TOPIC + "/telemetry";
static const String TOPIC_EVENTS = BASE_TOPIC + "/events";
static const String TOPIC_STATUS = BASE_TOPIC + "/status";
static const String TOPIC_COMMANDS = BASE_TOPIC + "/commands";

static const unsigned long TELEMETRY_INTERVAL_MS = 10000;
static const unsigned long MQTT_RETRY_INTERVAL_MS = 5000;

enum ControlMode {
  MODE_AUTO,
  MODE_MANUAL
};

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

ControlMode controlMode = MODE_AUTO;
unsigned long ultimaTelemetriaMs = 0;
unsigned long ultimaTentativaMqttMs = 0;
bool motionDarkEventActive = false;
bool lampadaLigada = false;
bool presencaAtual = false;
bool ambienteEscuroAtual = false;
float luxAtual = 0.0f;

const MqttBrokerConfig &brokerAtivo();
String mqttClientId();
float lerLux();
bool lerPresenca();
void conectarWiFi();
void configurarMQTT();
void manterMQTT();
void mqttCallback(char *topic, byte *payload, unsigned int length);
void processarComando(const String &mensagem);
bool processarComandoTexto(String mensagem);
void processarComandoJson(const String &mensagem);
void aplicarControleLampada();
void publicarTelemetria();
void publicarEvento();
void publicarStatus(const char *status);
void publicarErroComando(const String &mensagemRecebida);
void adicionarIdentificacao(JsonDocument &documento);
void registrarModoAtual();
const char *modoControleTexto();
const char *estadoLampadaTexto();
const char *condicaoLuzTexto();
const char *descricaoEstadoMqtt(int estado);
template <typename TDocument>
bool publicarJson(const String &topic, const TDocument &documento);

void setup() {
  Serial.begin(115200);

  pinMode(LDR_PIN, INPUT);
  pinMode(PIR_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  conectarWiFi();
  configurarMQTT();
}

void loop() {
  manterMQTT();
  mqttClient.loop();

  luxAtual = lerLux();
  presencaAtual = lerPresenca();
  ambienteEscuroAtual = luxAtual < LUX_DARK_THRESHOLD;
  aplicarControleLampada();

  const bool motionInDark = presencaAtual && ambienteEscuroAtual;
  if (motionInDark && !motionDarkEventActive) {
    publicarEvento();
  }
  motionDarkEventActive = motionInDark;

  const unsigned long agora = millis();
  if (agora - ultimaTelemetriaMs >= TELEMETRY_INTERVAL_MS) {
    ultimaTelemetriaMs = agora;
    publicarTelemetria();
  }

  delay(250);
}

const MqttBrokerConfig &brokerAtivo() {
  return MQTT_BROKERS[MQTT_BROKER_ATIVO];
}

String mqttClientId() {
  return String(DEVICE_ID) + "-wokwi";
}

float lerLux() {
  const int valorAdc = analogRead(LDR_PIN);
  const float tensao = valorAdc / 4095.0f * 3.3f;

  if (tensao >= 3.29f) {
    return 0.0f;
  }

  const float resistencia = 2000.0f * tensao / (1.0f - tensao / 3.3f);
  if (resistencia <= 0.0f) {
    return 100000.0f;
  }

  return pow((LDR_RL10 * 1000.0f * pow(10.0f, LDR_GAMMA)) / resistencia,
             1.0f / LDR_GAMMA);
}

bool lerPresenca() {
  return digitalRead(PIR_PIN) == HIGH;
}

void conectarWiFi() {
  Serial.print("Conectando ao WiFi Wokwi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD, WIFI_CHANNEL);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("WiFi conectado. IP: ");
  Serial.println(WiFi.localIP());
}

void configurarMQTT() {
  const MqttBrokerConfig &broker = brokerAtivo();

  mqttClient.setServer(broker.host, broker.porta);
  mqttClient.setCallback(mqttCallback);
  mqttClient.setBufferSize(512);

  Serial.print("MQTT CONNECT config broker=");
  Serial.print(broker.nome);
  Serial.print(" host=");
  Serial.print(broker.host);
  Serial.print(" port=");
  Serial.print(broker.porta);
  Serial.print(" client_id=");
  Serial.println(mqttClientId());
}

void manterMQTT() {
  if (mqttClient.connected()) {
    return;
  }

  const unsigned long agora = millis();
  if (agora - ultimaTentativaMqttMs < MQTT_RETRY_INTERVAL_MS) {
    return;
  }

  ultimaTentativaMqttMs = agora;
  const MqttBrokerConfig &broker = brokerAtivo();
  const String clientId = mqttClientId();

  Serial.print("MQTT CONNECT -> broker=");
  Serial.print(broker.nome);
  Serial.print(" host=");
  Serial.print(broker.host);
  Serial.print(" port=");
  Serial.print(broker.porta);
  Serial.print(" client_id=");
  Serial.println(clientId);

  if (mqttClient.connect(clientId.c_str())) {
    Serial.println("MQTT CONNECT -> [OK]");

    const bool subscribed = mqttClient.subscribe(TOPIC_COMMANDS.c_str());
    Serial.print("MQTT SUB -> [");
    Serial.print(subscribed ? "OK" : "FAIL");
    Serial.print("] ");
    Serial.println(TOPIC_COMMANDS);

    if (!subscribed) {
      Serial.println("MQTT ERROR subscribe_failed");
    }

    publicarStatus("online");
    return;
  }

  const int estado = mqttClient.state();
  Serial.print("MQTT CONNECT -> [FAIL] rc=");
  Serial.print(estado);
  Serial.print(" ");
  Serial.println(descricaoEstadoMqtt(estado));
}

void mqttCallback(char *topic, byte *payload, unsigned int length) {
  const String topicoRecebido(topic);

  String mensagem;
  mensagem.reserve(length);
  for (unsigned int i = 0; i < length; i++) {
    mensagem += static_cast<char>(payload[i]);
  }
  mensagem.trim();

  Serial.print("MQTT CMD RECEIVED <- ");
  Serial.print(topicoRecebido);
  Serial.print(": ");
  Serial.println(mensagem);

  if (topicoRecebido != TOPIC_COMMANDS) {
    Serial.print("MQTT ERROR unexpected_topic ");
    Serial.println(topicoRecebido);
    return;
  }

  processarComando(mensagem);
}

void processarComando(const String &mensagem) {
  if (processarComandoTexto(mensagem)) {
    return;
  }

  if (mensagem.startsWith("{")) {
    processarComandoJson(mensagem);
    return;
  }

  Serial.print("MQTT ERROR invalid_command ");
  Serial.println(mensagem);
  publicarErroComando(mensagem);
}

bool processarComandoTexto(String mensagem) {
  mensagem.trim();
  mensagem.toLowerCase();

  if (mensagem == "status") {
    publicarStatus("online");
    return true;
  }

  if (mensagem == "light:on") {
    controlMode = MODE_MANUAL;
    lampadaLigada = true;
    aplicarControleLampada();
    registrarModoAtual();
    publicarStatus("online");
    return true;
  }

  if (mensagem == "light:off") {
    controlMode = MODE_MANUAL;
    lampadaLigada = false;
    aplicarControleLampada();
    registrarModoAtual();
    publicarStatus("online");
    return true;
  }

  if (mensagem == "mode:auto") {
    controlMode = MODE_AUTO;
    aplicarControleLampada();
    registrarModoAtual();
    publicarStatus("online");
    return true;
  }

  return false;
}

void processarComandoJson(const String &mensagem) {
  JsonDocument documento;
  const DeserializationError erro = deserializeJson(documento, mensagem);
  if (erro) {
    Serial.print("MQTT ERROR invalid_json ");
    Serial.println(erro.c_str());
    publicarErroComando(mensagem);
    return;
  }

  String comando = documento["command"] | "";
  comando.trim();
  comando.toLowerCase();

  if (comando == "status") {
    publicarStatus("online");
    return;
  }

  if (comando == "set_light") {
    String estado = documento["state"] | "";
    estado.trim();
    estado.toLowerCase();

    if (estado == "on" || estado == "off") {
      controlMode = MODE_MANUAL;
      lampadaLigada = estado == "on";
      aplicarControleLampada();
      registrarModoAtual();
      publicarStatus("online");
      return;
    }
  }

  if (comando == "set_mode") {
    String modo = documento["mode"] | "";
    modo.trim();
    modo.toLowerCase();

    if (modo == "auto") {
      controlMode = MODE_AUTO;
      aplicarControleLampada();
      registrarModoAtual();
      publicarStatus("online");
      return;
    }
  }

  Serial.print("MQTT ERROR invalid_command ");
  Serial.println(mensagem);
  publicarErroComando(mensagem);
}

void aplicarControleLampada() {
  if (controlMode == MODE_AUTO) {
    lampadaLigada = presencaAtual && ambienteEscuroAtual;
  }

  digitalWrite(LED_PIN, lampadaLigada ? HIGH : LOW);
}

void publicarTelemetria() {
  JsonDocument documento;
  adicionarIdentificacao(documento);
  documento["lux"] = luxAtual;
  documento["presence"] = presencaAtual;
  documento["light_condition"] = condicaoLuzTexto();
  documento["control_mode"] = modoControleTexto();
  documento["lamp_state"] = estadoLampadaTexto();
  documento["uptime_ms"] = millis();
  documento["source"] = SOURCE;

  publicarJson(TOPIC_TELEMETRY, documento);
}

void publicarEvento() {
  JsonDocument documento;
  adicionarIdentificacao(documento);
  documento["event"] = "motion_detected_in_dark_environment";
  documento["lux"] = luxAtual;
  documento["control_mode"] = modoControleTexto();
  documento["lamp_state"] = estadoLampadaTexto();
  documento["uptime_ms"] = millis();
  documento["source"] = SOURCE;

  publicarJson(TOPIC_EVENTS, documento);
}

void publicarStatus(const char *status) {
  JsonDocument documento;
  adicionarIdentificacao(documento);
  documento["status"] = status;
  documento["ip"] = WiFi.localIP().toString();
  documento["firmware"] = FIRMWARE_VERSION;
  documento["control_mode"] = modoControleTexto();
  documento["lamp_state"] = estadoLampadaTexto();
  documento["uptime_ms"] = millis();
  documento["source"] = SOURCE;

  publicarJson(TOPIC_STATUS, documento);
}

void publicarErroComando(const String &mensagemRecebida) {
  JsonDocument documento;
  adicionarIdentificacao(documento);
  documento["status"] = "error";
  documento["error"] = "invalid_command";
  documento["received"] = mensagemRecebida;
  documento["uptime_ms"] = millis();
  documento["source"] = SOURCE;

  publicarJson(TOPIC_STATUS, documento);
}

void adicionarIdentificacao(JsonDocument &documento) {
  documento["site"] = MQTT_SITE;
  documento["area"] = MQTT_AREA;
  documento["domain"] = MQTT_DOMAIN;
  documento["device_id"] = DEVICE_ID;
}

void registrarModoAtual() {
  Serial.print("MQTT MODE control_mode=");
  Serial.print(modoControleTexto());
  Serial.print(" lamp_state=");
  Serial.println(estadoLampadaTexto());
}

const char *modoControleTexto() {
  return controlMode == MODE_AUTO ? "auto" : "manual";
}

const char *estadoLampadaTexto() {
  return lampadaLigada ? "on" : "off";
}

const char *condicaoLuzTexto() {
  return ambienteEscuroAtual ? "dark" : "bright";
}

const char *descricaoEstadoMqtt(int estado) {
  switch (estado) {
    case -4:
      return "connection_timeout";
    case -3:
      return "connection_lost";
    case -2:
      return "connect_failed_tcp_or_mqtt_server";
    case -1:
      return "disconnected";
    case 0:
      return "connected";
    case 1:
      return "bad_protocol";
    case 2:
      return "bad_client_id";
    case 3:
      return "server_unavailable";
    case 4:
      return "bad_credentials";
    case 5:
      return "not_authorized";
    default:
      return "unknown";
  }
}

template <typename TDocument>
bool publicarJson(const String &topic, const TDocument &documento) {
  char payload[512];
  const size_t tamanho = serializeJson(documento, payload, sizeof(payload));

  if (tamanho == 0 || tamanho >= sizeof(payload)) {
    Serial.println("MQTT ERROR json_serialize_failed");
    return false;
  }

  const bool publicado = mqttClient.publish(topic.c_str(), payload);
  Serial.print("MQTT PUB -> [");
  Serial.print(publicado ? "OK" : "FAIL");
  Serial.print("] ");
  Serial.print(topic);
  Serial.print(": ");
  Serial.println(payload);

  return publicado;
}
