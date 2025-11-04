// ESP32/ESP8266 Web Server for Refrigeration Data Monitoring
// Serves static HTML page and provides real-time sensor data via API

#include <Arduino.h>
#ifdef ESP32
#include <WiFi.h>
#include <AsyncTCP.h>
#elif defined(ESP8266)
#include <ESP8266WiFi.h>
#include <ESPAsyncTCP.h>
#endif
#include <ESPAsyncWebServer.h>

AsyncWebServer server(80);

// WiFi credentials - Update these with your network details
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

const char* PARAM_MESSAGE = "message";

// Simulated sensor data structure
struct SensorData {
    float temp_evaporator;
    float temp_condenser;
    float pressure_high;
    float pressure_low;
    float superheat;
    float subcooling;
    float compressor_current;
    float vibration;
    unsigned long timestamp;
};

SensorData currentData;

// HTML page content
const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Refrigeration Monitoring System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .sensor-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .sensor-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .sensor-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }
        .sensor-label {
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .sensor-value {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        .sensor-unit {
            font-size: 18px;
            color: #999;
        }
        .status-bar {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        .status-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        .status-online {
            background-color: #4CAF50;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .timestamp {
            color: #666;
            font-size: 14px;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: background 0.3s ease;
        }
        .refresh-btn:hover {
            background: #5568d3;
        }
        @media (max-width: 768px) {
            .sensor-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧊 Refrigeration Monitoring System</h1>
        
        <div class="status-bar">
            <div class="status-item">
                <div class="status-indicator status-online"></div>
                <span>System Online</span>
            </div>
            <div class="timestamp" id="lastUpdate">Last update: --</div>
            <button class="refresh-btn" onclick="fetchData()">Refresh Data</button>
        </div>

        <br>

        <div class="sensor-grid">
            <div class="sensor-card">
                <div class="sensor-label">Evaporator Temperature</div>
                <div class="sensor-value" id="temp_evaporator">--</div>
                <div class="sensor-unit">°C</div>
            </div>

            <div class="sensor-card">
                <div class="sensor-label">Condenser Temperature</div>
                <div class="sensor-value" id="temp_condenser">--</div>
                <div class="sensor-unit">°C</div>
            </div>

            <div class="sensor-card">
                <div class="sensor-label">High Pressure</div>
                <div class="sensor-value" id="pressure_high">--</div>
                <div class="sensor-unit">bar</div>
            </div>

            <div class="sensor-card">
                <div class="sensor-label">Low Pressure</div>
                <div class="sensor-value" id="pressure_low">--</div>
                <div class="sensor-unit">bar</div>
            </div>

            <div class="sensor-card">
                <div class="sensor-label">Superheat</div>
                <div class="sensor-value" id="superheat">--</div>
                <div class="sensor-unit">°C</div>
            </div>

            <div class="sensor-card">
                <div class="sensor-label">Subcooling</div>
                <div class="sensor-value" id="subcooling">--</div>
                <div class="sensor-unit">°C</div>
            </div>

            <div class="sensor-card">
                <div class="sensor-label">Compressor Current</div>
                <div class="sensor-value" id="compressor_current">--</div>
                <div class="sensor-unit">A</div>
            </div>

            <div class="sensor-card">
                <div class="sensor-label">Vibration Level</div>
                <div class="sensor-value" id="vibration">--</div>
                <div class="sensor-unit">g</div>
            </div>
        </div>
    </div>

    <script>
        // Fetch sensor data from the server
        async function fetchData() {
            try {
                const response = await fetch('/api/sensors');
                const data = await response.json();
                
                // Update all sensor values
                document.getElementById('temp_evaporator').textContent = data.temp_evaporator.toFixed(1);
                document.getElementById('temp_condenser').textContent = data.temp_condenser.toFixed(1);
                document.getElementById('pressure_high').textContent = data.pressure_high.toFixed(2);
                document.getElementById('pressure_low').textContent = data.pressure_low.toFixed(2);
                document.getElementById('superheat').textContent = data.superheat.toFixed(1);
                document.getElementById('subcooling').textContent = data.subcooling.toFixed(1);
                document.getElementById('compressor_current').textContent = data.compressor_current.toFixed(1);
                document.getElementById('vibration').textContent = data.vibration.toFixed(3);
                
                // Update timestamp
                const now = new Date();
                document.getElementById('lastUpdate').textContent = 
                    'Last update: ' + now.toLocaleTimeString();
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }

        // Auto-refresh every 2 seconds
        setInterval(fetchData, 2000);
        
        // Initial fetch
        fetchData();
    </script>
</body>
</html>
)rawliteral";

// Function to handle 404 errors
void notFound(AsyncWebServerRequest *request) {
    request->send(404, "text/plain", "Not found");
}

// Function to generate simulated sensor data
void updateSensorData() {
    // Simulate sensor readings with realistic values
    currentData.temp_evaporator = -10.0 + random(-20, 20) / 10.0;
    currentData.temp_condenser = 40.0 + random(-30, 30) / 10.0;
    currentData.pressure_high = 12.0 + random(-20, 20) / 10.0;
    currentData.pressure_low = 2.5 + random(-10, 10) / 10.0;
    currentData.superheat = 8.0 + random(-20, 20) / 10.0;
    currentData.subcooling = 5.0 + random(-15, 15) / 10.0;
    currentData.compressor_current = 8.5 + random(-15, 15) / 10.0;
    currentData.vibration = 0.025 + random(-10, 10) / 1000.0;
    currentData.timestamp = millis();
}

void setup() {
    Serial.begin(115200);
    
    // Initialize random seed
    randomSeed(analogRead(0));
    
    // Connect to WiFi
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    
    Serial.println("Connecting to WiFi...");
    
    if (WiFi.waitForConnectResult() != WL_CONNECTED) {
        Serial.printf("WiFi Failed!\n");
        return;
    }

    Serial.println("\n✓ WiFi Connected Successfully");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.println("Open this address in your browser to view the dashboard");

    // Initialize sensor data
    updateSensorData();

    // Serve the main HTML page
    server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
        request->send_P(200, "text/html", index_html);
    });

    // API endpoint to get sensor data as JSON
    server.on("/api/sensors", HTTP_GET, [](AsyncWebServerRequest *request){
        // Update sensor data before sending
        updateSensorData();
        
        // Create JSON response
        String json = "{";
        json += "\"temp_evaporator\":" + String(currentData.temp_evaporator, 1) + ",";
        json += "\"temp_condenser\":" + String(currentData.temp_condenser, 1) + ",";
        json += "\"pressure_high\":" + String(currentData.pressure_high, 2) + ",";
        json += "\"pressure_low\":" + String(currentData.pressure_low, 2) + ",";
        json += "\"superheat\":" + String(currentData.superheat, 1) + ",";
        json += "\"subcooling\":" + String(currentData.subcooling, 1) + ",";
        json += "\"compressor_current\":" + String(currentData.compressor_current, 1) + ",";
        json += "\"vibration\":" + String(currentData.vibration, 3) + ",";
        json += "\"timestamp\":" + String(currentData.timestamp);
        json += "}";
        
        request->send(200, "application/json", json);
    });

    // Legacy GET endpoint with parameter
    server.on("/get", HTTP_GET, [](AsyncWebServerRequest *request) {
        String message;
        if (request->hasParam(PARAM_MESSAGE)) {
            message = request->getParam(PARAM_MESSAGE)->value();
        } else {
            message = "No message sent";
        }
        request->send(200, "text/plain", "Hello, GET: " + message);
    });

    // Legacy POST endpoint
    server.on("/post", HTTP_POST, [](AsyncWebServerRequest *request){
        String message;
        if (request->hasParam(PARAM_MESSAGE, true)) {
            message = request->getParam(PARAM_MESSAGE, true)->value();
        } else {
            message = "No message sent";
        }
        request->send(200, "text/plain", "Hello, POST: " + message);
    });

    // API endpoint for system status
    server.on("/api/status", HTTP_GET, [](AsyncWebServerRequest *request){
        String json = "{";
        json += "\"status\":\"online\",";
        json += "\"uptime\":" + String(millis()) + ",";
        json += "\"rssi\":" + String(WiFi.RSSI()) + ",";
        json += "\"free_heap\":" + String(ESP.getFreeHeap());
        json += "}";
        
        request->send(200, "application/json", json);
    });

    // Handle 404
    server.onNotFound(notFound);

    // Start server
    server.begin();
    Serial.println("✓ Web server started successfully!");
    Serial.println("Available endpoints:");
    Serial.println("  - http://" + WiFi.localIP().toString() + "/ (Main dashboard)");
    Serial.println("  - http://" + WiFi.localIP().toString() + "/api/sensors (JSON sensor data)");
    Serial.println("  - http://" + WiFi.localIP().toString() + "/api/status (System status)");
}

void loop() {
    // Main loop can be used for additional tasks
    // The async server handles requests independently
}
