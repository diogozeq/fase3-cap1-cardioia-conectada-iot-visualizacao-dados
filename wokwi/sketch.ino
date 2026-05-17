#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// CardioIA Fase 3 - Monitoramento continuo com Edge + MQTT.
// Este sketch foi pensado para Wokwi. Em ESP32 fisico, o buffer em memoria
// pode ser migrado para SPIFFS ou microSD.

#define DHT_PIN 15
#define DHT_TYPE DHT22
#define BPM_BUTTON_PIN 4
#define WIFI_SWITCH_PIN 18
#define MOVEMENT_SWITCH_PIN 19

const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASSWORD = "";

// Broker publico HiveMQ - sem necessidade de cadastro ou credenciais.
const char* MQTT_SERVER = "broker.hivemq.com";
const int MQTT_PORT = 1883;

const char* PATIENT_ID = "cardioia-paciente-001";
const char* TOPIC_VITALS = "cardioia/patients/cardioia-paciente-001/vitals";
const char* TOPIC_ALERTS = "cardioia/patients/cardioia-paciente-001/alerts";
const char* TOPIC_STATUS = "cardioia/system/status";

const unsigned long SAMPLE_INTERVAL_MS = 5000;
const unsigned long BPM_WINDOW_MS = 15000;
const int OFFLINE_BUFFER_LIMIT = 2000;

DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient netClient;
PubSubClient mqtt(netClient);

struct VitalSample {
  unsigned long timestampMs;
  float temperature;
  float humidity;
  int bpm;
  bool movement;
  bool wifiRequested;
  char riskLevel[16];
  char alertReason[96];
};

VitalSample offlineBuffer[OFFLINE_BUFFER_LIMIT];
int bufferStart = 0;
int bufferCount = 0;

unsigned long lastSampleAt = 0;
unsigned long bpmWindowStartedAt = 0;
int pulseCount = 0;
bool previousButtonState = HIGH;

void pushOfflineSample(const VitalSample& sample) {
  int index = (bufferStart + bufferCount) % OFFLINE_BUFFER_LIMIT;
  if (bufferCount == OFFLINE_BUFFER_LIMIT) {
    bufferStart = (bufferStart + 1) % OFFLINE_BUFFER_LIMIT;
    index = (bufferStart + bufferCount - 1) % OFFLINE_BUFFER_LIMIT;
    Serial.println("[EDGE] Buffer cheio: amostra mais antiga descartada.");
  } else {
    bufferCount++;
  }
  offlineBuffer[index] = sample;
}

VitalSample popOfflineSample() {
  VitalSample sample = offlineBuffer[bufferStart];
  bufferStart = (bufferStart + 1) % OFFLINE_BUFFER_LIMIT;
  bufferCount--;
  return sample;
}

void classifyRisk(VitalSample& sample) {
  strcpy(sample.riskLevel, "normal");
  strcpy(sample.alertReason, "sem alerta");

  if (sample.bpm > 120) {
    strcpy(sample.riskLevel, "alto");
    strcpy(sample.alertReason, "possivel taquicardia: bpm acima de 120");
  } else if (sample.temperature > 38.0) {
    strcpy(sample.riskLevel, "alto");
    strcpy(sample.alertReason, "possivel febre: temperatura acima de 38 C");
  } else if (!sample.movement && sample.bpm < 50) {
    strcpy(sample.riskLevel, "moderado");
    strcpy(sample.alertReason, "baixa atividade associada a bradicardia");
  } else if (!sample.movement) {
    strcpy(sample.riskLevel, "atencao");
    strcpy(sample.alertReason, "ausencia de movimento detectada");
  }
}

String sampleToJson(const VitalSample& sample) {
  StaticJsonDocument<384> doc;
  doc["patient_id"] = PATIENT_ID;
  doc["timestamp_ms"] = sample.timestampMs;
  doc["temperature_c"] = sample.temperature;
  doc["humidity_pct"] = sample.humidity;
  doc["bpm"] = sample.bpm;
  doc["movement"] = sample.movement;
  doc["wifi_requested"] = sample.wifiRequested;
  doc["risk_level"] = sample.riskLevel;
  doc["alert_reason"] = sample.alertReason;
  doc["offline_buffer_count"] = bufferCount;

  String payload;
  serializeJson(doc, payload);
  return payload;
}

bool wifiEnabledBySwitch() {
  return digitalRead(WIFI_SWITCH_PIN) == HIGH;
}

void ensureWifi() {
  if (!wifiEnabledBySwitch()) {
    if (WiFi.status() == WL_CONNECTED) {
      WiFi.disconnect(true);
      Serial.println("[WIFI] Simulacao offline ativada pelo switch.");
    }
    return;
  }

  if (WiFi.status() == WL_CONNECTED) return;

  Serial.println("[WIFI] Conectando...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  unsigned long startedAt = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startedAt < 8000) {
    delay(250);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("[WIFI] Conectado: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("[WIFI] Falha ou timeout. Coleta continua no Edge.");
  }
}

void ensureMqtt() {
  if (WiFi.status() != WL_CONNECTED || mqtt.connected()) return;

  mqtt.setServer(MQTT_SERVER, MQTT_PORT);

  Serial.println("[MQTT] Conectando ao broker publico HiveMQ...");
  String clientId = String("cardioia-esp32-") + String(random(0xffff), HEX);

  if (mqtt.connect(clientId.c_str())) {
    Serial.println("[MQTT] Conectado.");
    mqtt.publish(TOPIC_STATUS, "{\"device\":\"esp32\",\"status\":\"online\"}", true);
  } else {
    Serial.print("[MQTT] Falha rc=");
    Serial.println(mqtt.state());
  }
}

bool publishSample(const VitalSample& sample) {
  if (WiFi.status() != WL_CONNECTED || !mqtt.connected()) return false;

  String payload = sampleToJson(sample);
  bool ok = mqtt.publish(TOPIC_VITALS, payload.c_str());
  Serial.print("[MQTT] vitals ");
  Serial.println(ok ? payload : "falha ao publicar");

  if (ok && strcmp(sample.riskLevel, "normal") != 0) {
    mqtt.publish(TOPIC_ALERTS, payload.c_str());
    Serial.print("[MQTT] alert ");
    Serial.println(payload);
  }

  return ok;
}

void syncOfflineBuffer() {
  if (WiFi.status() != WL_CONNECTED || !mqtt.connected()) return;

  while (bufferCount > 0) {
    VitalSample sample = popOfflineSample();
    if (!publishSample(sample)) {
      pushOfflineSample(sample);
      break;
    }
    delay(100);
  }
}

void updateBpmCounter() {
  bool buttonState = digitalRead(BPM_BUTTON_PIN);
  if (previousButtonState == HIGH && buttonState == LOW) {
    pulseCount++;
  }
  previousButtonState = buttonState;
}

int currentBpm() {
  unsigned long elapsed = millis() - bpmWindowStartedAt;
  if (elapsed >= BPM_WINDOW_MS) {
    int bpm = (int)((pulseCount * 60000.0) / elapsed);
    pulseCount = 0;
    bpmWindowStartedAt = millis();
    return constrain(bpm, 40, 180);
  }
  return 72 + (pulseCount * 4);
}

VitalSample readSample() {
  VitalSample sample;
  sample.timestampMs = millis();
  sample.temperature = dht.readTemperature();
  sample.humidity = dht.readHumidity();
  sample.bpm = currentBpm();
  sample.movement = digitalRead(MOVEMENT_SWITCH_PIN) == HIGH;
  sample.wifiRequested = wifiEnabledBySwitch();

  if (isnan(sample.temperature)) sample.temperature = 36.5;
  if (isnan(sample.humidity)) sample.humidity = 55.0;

  classifyRisk(sample);
  return sample;
}

void setup() {
  Serial.begin(115200);
  pinMode(BPM_BUTTON_PIN, INPUT_PULLUP);
  pinMode(WIFI_SWITCH_PIN, INPUT);
  pinMode(MOVEMENT_SWITCH_PIN, INPUT);

  dht.begin();
  bpmWindowStartedAt = millis();

  Serial.println("CardioIA Fase 3 - Edge/Fog/Cloud IoT");
  Serial.println("Use o switch WiFi para alternar online/offline e testar resiliencia.");
}

void loop() {
  updateBpmCounter();
  ensureWifi();
  ensureMqtt();
  mqtt.loop();
  syncOfflineBuffer();

  if (millis() - lastSampleAt >= SAMPLE_INTERVAL_MS) {
    lastSampleAt = millis();
    VitalSample sample = readSample();
    String payload = sampleToJson(sample);

    Serial.print("[EDGE] sample ");
    Serial.println(payload);

    if (!publishSample(sample)) {
      pushOfflineSample(sample);
      Serial.print("[EDGE] Offline/broker indisponivel. Buffer=");
      Serial.println(bufferCount);
    }
  }
}
