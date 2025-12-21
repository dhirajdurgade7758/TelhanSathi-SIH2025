#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <Preferences.h> // For saving data to flash memory
#include <DHT.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// --- PIN DEFINITIONS ---
#define DHTPIN 4
#define DS18B20_PIN 5
#define SOIL_PIN 34
#define LDR_PIN 35
#define LED_PIN 2
#define RESET_BUTTON_PIN 0 // BOOT button to reset WiFi

// --- OBJECTS ---
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);
OneWire oneWire(DS18B20_PIN);
DallasTemperature sensors(&oneWire);

// Web Server for Provisioning
WebServer server(80);
Preferences preferences; // Non-volatile storage

// Variables to store configuration
String config_ssid = "";
String config_pass = "";
String config_server = ""; 

bool isAPMode = false;

// --- CALIBRATION CONSTANTS ---
const int dryVal = 3000; 
const int wetVal = 1200; 

// Light Sensor Constants
const float MAX_ADC = 4095.0;
const float R_FIXED = 10000.0; // 10k Resistor
const float GAMMA = 0.7;
const float RL10 = 50;

// --- HTML PAGE FOR SETUP ---
const char* setup_html = R"rawliteral(
<!DOCTYPE HTML><html><head>
  <title>Smart Garden Setup</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Arial; text-align: center; background-color: #0f172a; color: white; padding: 20px; }
    input { width: 100%; padding: 12px; margin: 8px 0; box-sizing: border-box; border-radius: 5px; border: none; }
    input[type=submit] { background-color: #22c55e; color: white; font-weight: bold; cursor: pointer; }
    .card { background-color: #1e293b; padding: 20px; border-radius: 10px; max-width: 400px; margin: auto; }
    h2 { color: #22c55e; }
  </style>
</head><body>
  <div class="card">
    <h2>🌱 Garden Setup</h2>
    <p>Configure your device to connect to the internet.</p>
    <form action="/save" method="POST">
      <label>WiFi Name (SSID):</label><br>
      <input type="text" name="ssid" placeholder="Enter WiFi Name" required><br>
      <label>WiFi Password:</label><br>
      <input type="password" name="pass" placeholder="Enter WiFi Password"><br>
      <label>Server IP (e.g., 192.168.1.5):</label><br>
      <input type="text" name="ip" placeholder="Laptop IP Address" required><br>
      <input type="submit" value="Save & Restart">
    </form>
  </div>
</body></html>
)rawliteral";

// --- FUNCTIONS ---

void handleRoot() {
  server.send(200, "text/html", setup_html);
}

void handleSave() {
  if (server.hasArg("ssid") && server.hasArg("ip")) {
    String n_ssid = server.arg("ssid");
    String n_pass = server.arg("pass");
    String n_ip = server.arg("ip");

    // Save to Flash Memory
    preferences.begin("garden-config", false);
    preferences.putString("ssid", n_ssid);
    preferences.putString("pass", n_pass);
    preferences.putString("ip", n_ip);
    preferences.end();

    String response = "<html><body style='background-color:#0f172a; color:white; text-align:center; font-family:Arial;'>";
    response += "<h1>Saved! ✅</h1><p>Device is restarting and connecting to " + n_ssid + "...</p></body></html>";
    server.send(200, "text/html", response);
    
    delay(2000);
    ESP.restart();
  } else {
    server.send(400, "text/plain", "Missing Data");
  }
}

void startAPMode() {
  Serial.println("Starting Access Point Mode...");
  WiFi.mode(WIFI_AP);
  WiFi.softAP("SmartGarden-Setup", "12345678"); 
  
  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);

  server.on("/", handleRoot);
  server.on("/save", handleSave);
  server.begin();
  isAPMode = true;
  
  while(true) {
    server.handleClient();
    digitalWrite(LED_PIN, millis() % 1000 < 500); // Slow Blink
    
    // Check reset button
    if (digitalRead(RESET_BUTTON_PIN) == LOW) {
        delay(2000); 
        if (digitalRead(RESET_BUTTON_PIN) == LOW) {
             preferences.begin("garden-config", false);
             preferences.clear();
             preferences.end();
             ESP.restart();
        }
    }
  }
}

// --- SETUP ---
void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(RESET_BUTTON_PIN, INPUT_PULLUP);
  
  // Init Sensors
  dht.begin();
  sensors.begin();
  analogReadResolution(12);
  pinMode(LDR_PIN, INPUT);
  pinMode(SOIL_PIN, INPUT);

  // Load Config
  preferences.begin("garden-config", true); 
  config_ssid = preferences.getString("ssid", "");
  config_pass = preferences.getString("pass", "");
  config_server = preferences.getString("ip", "");
  preferences.end();

  Serial.println("Loaded Config:");
  Serial.println("SSID: " + config_ssid);
  Serial.println("Server: " + config_server);

  if (config_ssid == "") {
    startAPMode();
  }

  // Try to Connect
  WiFi.begin(config_ssid.c_str(), config_pass.c_str());
  
  int retries = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    digitalWrite(LED_PIN, !digitalRead(LED_PIN)); // Fast blink
    retries++;
    
    if (digitalRead(RESET_BUTTON_PIN) == LOW) {
       Serial.println("Resetting Config...");
       preferences.begin("garden-config", false);
       preferences.clear();
       preferences.end();
       ESP.restart();
    }

    if (retries > 40) {
      Serial.println("\nFailed to connect. Starting Setup Mode.");
      startAPMode();
    }
  }

  Serial.println("\nWiFi Connected!");
  digitalWrite(LED_PIN, LOW);
}

// --- LOOP ---
void loop() {
  delay(3000);

  // 1. Read Sensors
  float airHum = dht.readHumidity();
  float airTemp = dht.readTemperature();
  float heatIndex = dht.computeHeatIndex(airTemp, airHum, false);
  
  sensors.requestTemperatures();
  float soilTemp = sensors.getTempCByIndex(0);
  if (soilTemp == -127.00) soilTemp = 0.0;

  int soilRaw = analogRead(SOIL_PIN);
  int soilPercent = map(soilRaw, dryVal, wetVal, 0, 100);
  soilPercent = constrain(soilPercent, 0, 100);

  // --- LUX CALCULATION (Enhanced) ---
  long analogSum = 0;
  for(int i=0; i<10; i++) { 
      analogSum += analogRead(LDR_PIN); 
      delay(10); 
  }
  int analogValue = analogSum / 10;
  
  float voltage = analogValue / MAX_ADC * 3.3;
  float resistance = 0;
  float lux = 0;

  if (analogValue > 0 && analogValue < 4095) {
      // R_LDR = (R_10k * V_out) / (V_in - V_out)
      resistance = (R_FIXED * voltage) / (3.3 - voltage);
      lux = pow(RL10 * 1e3 * pow(10, GAMMA) / resistance, (1 / GAMMA)); 
  } else {
      lux = 0; 
  }

  // Sanity check
  if (isinf(lux)) lux = 100000;
  if (lux > 100000) lux = 100000;
  if (lux < 0) lux = 0;

  // 2. Send Data
  if(WiFi.status() == WL_CONNECTED) {
    digitalWrite(LED_PIN, HIGH);
    HTTPClient http;
    
    // ⭐ CORRECTED: Include /field-monitoring prefix in URL
    String url = "http://" + config_server + ":3000/field-monitoring/api/update";
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    
    String json = "{";
    json += "\"airTemp\":" + String(airTemp) + ",";
    json += "\"airHum\":" + String(airHum) + ",";
    json += "\"heatIndex\":" + String(heatIndex) + ","; 
    json += "\"soilTemp\":" + String(soilTemp) + ",";
    json += "\"soilMoist\":" + String(soilPercent) + ",";
    json += "\"soilRaw\":" + String(soilRaw) + ",";
    json += "\"light\":" + String(lux) + ","; 
    json += "\"lightRaw\":" + String(analogValue) + ",";
    json += "\"rssi\":" + String(WiFi.RSSI()) + ",";        
    json += "\"uptime\":" + String(millis()/1000);           
    json += "}";
    
    int httpResponseCode = http.POST(json);
    if (httpResponseCode > 0) {
        Serial.print("✓ Data Sent. Temp: "); Serial.print(airTemp);
        Serial.print("°C | Humidity: "); Serial.print(airHum);
        Serial.print("% | Soil: "); Serial.print(soilPercent);
        Serial.print("% | Light: "); Serial.print(lux);
        Serial.print(" lux | Code: "); Serial.println(httpResponseCode);
    } else {
        Serial.print("✗ Error sending to " + url + " | Code: ");
        Serial.println(httpResponseCode);
    }
    http.end();
    digitalWrite(LED_PIN, LOW);
  }
}
