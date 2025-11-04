# ESP32/ESP8266 Integration Guide

This guide explains how to integrate the ESP32/ESP8266 web server with the main FroidPredict system.

## Architecture Overview

```
┌─────────────────────┐
│  Real Sensors       │
│  (Temperature,      │
│   Pressure, etc.)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐      WiFi       ┌─────────────────────┐
│  ESP32/ESP8266      │◀────────────────▶│  Web Browser        │
│  - Read Sensors     │                  │  - View Dashboard   │
│  - Host Web Server  │                  │  - Monitor Data     │
│  - Expose API       │                  └─────────────────────┘
└──────────┬──────────┘
           │ HTTP/MQTT
           ▼
┌─────────────────────┐
│  Python Backend     │
│  - Kafka Producer   │
│  - MongoDB Storage  │
│  - ML Predictions   │
└─────────────────────┘
```

## Integration Methods

### Method 1: Direct HTTP Integration

Send sensor data directly to the Python Flask backend:

#### Step 1: Add HTTPClient Library

Add to your Arduino sketch:

```cpp
#ifdef ESP32
#include <HTTPClient.h>
#elif defined(ESP8266)
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#endif
```

#### Step 2: Implement Data Sending Function

```cpp
void sendDataToBackend() {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        WiFiClient client;
        
        // Prepare JSON payload
        String jsonPayload = "{";
        jsonPayload += "\"machine_id\":1,";
        jsonPayload += "\"timestamp\":\"" + getISO8601Time() + "\",";
        jsonPayload += "\"temp_evaporator\":" + String(currentData.temp_evaporator, 1) + ",";
        jsonPayload += "\"temp_condenser\":" + String(currentData.temp_condenser, 1) + ",";
        jsonPayload += "\"pressure_high\":" + String(currentData.pressure_high, 2) + ",";
        jsonPayload += "\"pressure_low\":" + String(currentData.pressure_low, 2) + ",";
        jsonPayload += "\"superheat\":" + String(currentData.superheat, 1) + ",";
        jsonPayload += "\"subcooling\":" + String(currentData.subcooling, 1) + ",";
        jsonPayload += "\"compressor_current\":" + String(currentData.compressor_current, 1) + ",";
        jsonPayload += "\"vibration\":" + String(currentData.vibration, 3);
        jsonPayload += "}";
        
        // Send POST request
        http.begin(client, "http://YOUR_BACKEND_IP:5002/api/sensor_data");
        http.addHeader("Content-Type", "application/json");
        
        int httpResponseCode = http.POST(jsonPayload);
        
        if (httpResponseCode > 0) {
            Serial.printf("Data sent successfully. Response code: %d\n", httpResponseCode);
        } else {
            Serial.printf("Error sending data: %s\n", http.errorToString(httpResponseCode).c_str());
        }
        
        http.end();
    }
}

// Helper function to get ISO 8601 timestamp
String getISO8601Time() {
    // You'll need to implement NTP time sync for accurate timestamps
    // For now, using millis() as placeholder
    return String(millis());
}
```

#### Step 3: Call in Loop

```cpp
void loop() {
    static unsigned long lastSend = 0;
    unsigned long now = millis();
    
    // Send data every 5 seconds
    if (now - lastSend >= 5000) {
        updateSensorData();
        sendDataToBackend();
        lastSend = now;
    }
}
```

### Method 2: MQTT Integration

Use MQTT broker for more reliable, decoupled communication:

#### Step 1: Install PubSubClient Library

In Arduino IDE: Tools → Manage Libraries → Search "PubSubClient" → Install

#### Step 2: Add MQTT Configuration

```cpp
#include <PubSubClient.h>

const char* MQTT_SERVER = "192.168.1.100";
const int MQTT_PORT = 1883;
const char* MQTT_TOPIC = "sensors/refrigeration";

WiFiClient espClient;
PubSubClient mqttClient(espClient);
```

#### Step 3: Implement MQTT Functions

```cpp
void reconnectMQTT() {
    while (!mqttClient.connected()) {
        Serial.print("Attempting MQTT connection...");
        
        String clientId = "ESP32Client-";
        clientId += String(random(0xffff), HEX);
        
        if (mqttClient.connect(clientId.c_str())) {
            Serial.println("connected");
        } else {
            Serial.print("failed, rc=");
            Serial.print(mqttClient.state());
            Serial.println(" try again in 5 seconds");
            delay(5000);
        }
    }
}

void publishSensorData() {
    if (!mqttClient.connected()) {
        reconnectMQTT();
    }
    
    String json = "{";
    json += "\"machine_id\":1,";
    json += "\"temp_evaporator\":" + String(currentData.temp_evaporator, 1) + ",";
    // ... add other fields
    json += "}";
    
    mqttClient.publish(MQTT_TOPIC, json.c_str());
    Serial.println("Data published to MQTT");
}
```

#### Step 4: Setup and Loop

```cpp
void setup() {
    // ... existing setup code
    
    mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
}

void loop() {
    if (!mqttClient.connected()) {
        reconnectMQTT();
    }
    mqttClient.loop();
    
    static unsigned long lastPublish = 0;
    if (millis() - lastPublish >= 5000) {
        updateSensorData();
        publishSensorData();
        lastPublish = millis();
    }
}
```

### Method 3: WebSocket Integration

For real-time bidirectional communication:

```cpp
#include <WebSocketsClient.h>

WebSocketsClient webSocket;

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            Serial.println("WebSocket Disconnected");
            break;
        case WStype_CONNECTED:
            Serial.println("WebSocket Connected");
            break;
        case WStype_TEXT:
            Serial.printf("Received: %s\n", payload);
            break;
    }
}

void setup() {
    // ... existing setup
    
    webSocket.begin("192.168.1.100", 5002, "/socket.io/?EIO=4&transport=websocket");
    webSocket.onEvent(webSocketEvent);
}

void loop() {
    webSocket.loop();
    
    // Send data periodically
    if (millis() % 5000 == 0) {
        String json = "{...}";  // Your sensor data
        webSocket.sendTXT(json);
    }
}
```

## Python Backend Modifications

### Add Endpoint for ESP32/ESP8266 Data

Add to your Flask app.py:

```python
@app.route('/api/sensor_data', methods=['POST'])
def receive_esp_sensor_data():
    """Receive sensor data from ESP32/ESP8266"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['machine_id', 'temp_evaporator', 'temp_condenser', 
                          'pressure_high', 'pressure_low']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Add timestamp if not provided
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
        
        # Send to Kafka for processing
        producer.send('sensor_data', data)
        
        # Store in MongoDB
        mongo.db.sensor_readings.insert_one(data)
        
        return jsonify({'status': 'success', 'message': 'Data received'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Configure MQTT Bridge (if using MQTT)

Create a new file `mqtt_to_kafka.py`:

```python
import paho.mqtt.client as mqtt
from kafka import KafkaProducer
import json

# Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe("sensors/refrigeration")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print(f"Received from MQTT: {data}")
        
        # Forward to Kafka
        producer.send('sensor_data', data)
        print("Forwarded to Kafka")
        
    except Exception as e:
        print(f"Error processing message: {e}")

# Setup MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect and start loop
client.connect("localhost", 1883, 60)
client.loop_forever()
```

Run the bridge:
```bash
python mqtt_to_kafka.py
```

## Time Synchronization (NTP)

For accurate timestamps, add NTP time sync to ESP32/ESP8266:

```cpp
#include <time.h>

const char* NTP_SERVER = "pool.ntp.org";
const long GMT_OFFSET_SEC = 0;  // Adjust for your timezone
const int DAYLIGHT_OFFSET_SEC = 3600;

void setupTime() {
    configTime(GMT_OFFSET_SEC, DAYLIGHT_OFFSET_SEC, NTP_SERVER);
    Serial.println("Waiting for time sync...");
    
    time_t now = time(nullptr);
    while (now < 24 * 3600) {
        delay(500);
        Serial.print(".");
        now = time(nullptr);
    }
    Serial.println("\nTime synchronized!");
}

String getISO8601Time() {
    time_t now = time(nullptr);
    struct tm timeinfo;
    gmtime_r(&now, &timeinfo);
    
    char buffer[30];
    strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
    return String(buffer);
}

void setup() {
    // ... existing setup
    setupTime();
}
```

## Security Considerations

### 1. Authentication

Add API key authentication:

```cpp
const char* API_KEY = "your-secret-api-key";

void sendDataToBackend() {
    // ... existing code
    http.addHeader("X-API-Key", API_KEY);
    // ... rest of code
}
```

Backend validation:

```python
@app.route('/api/sensor_data', methods=['POST'])
def receive_esp_sensor_data():
    api_key = request.headers.get('X-API-Key')
    if api_key != 'your-secret-api-key':
        return jsonify({'error': 'Unauthorized'}), 401
    # ... rest of code
```

### 2. HTTPS (SSL/TLS)

For secure communication over the internet:

```cpp
#include <WiFiClientSecure.h>

WiFiClientSecure client;

void sendSecureData() {
    client.setInsecure();  // For testing; use proper certificates in production
    
    http.begin(client, "https://your-backend.com/api/sensor_data");
    // ... rest of code
}
```

## Testing the Integration

### 1. Test HTTP Endpoint

```bash
# Test with curl
curl -X POST http://YOUR_ESP_IP/api/sensors

# Test backend endpoint
curl -X POST http://localhost:5002/api/sensor_data \
  -H "Content-Type: application/json" \
  -d '{"machine_id":1,"temp_evaporator":-10.5,"temp_condenser":40.2}'
```

### 2. Monitor Logs

```bash
# Monitor Flask backend
python app.py

# Monitor Kafka consumer
python kafka_consumer.py

# Monitor MQTT bridge (if using)
python mqtt_to_kafka.py
```

### 3. Verify Data in MongoDB

```bash
# Check MongoDB for received data
mongo
> use refrigeration_system
> db.sensor_readings.find().sort({_id:-1}).limit(5)
```

## Troubleshooting

### Connection Issues

1. **ESP32 can't reach backend**
   - Check if devices are on same network
   - Verify backend IP address
   - Test with ping: `ping YOUR_BACKEND_IP`
   - Check firewall settings

2. **MQTT connection fails**
   - Verify MQTT broker is running
   - Check MQTT port (default: 1883)
   - Test with MQTT client: `mosquitto_sub -t sensors/#`

3. **Data not appearing in dashboard**
   - Check Kafka consumer is running
   - Verify MongoDB connection
   - Check Flask app logs
   - Verify WebSocket connections

### Performance Issues

1. **Slow response times**
   - Reduce update frequency
   - Optimize JSON payload size
   - Use batch sending

2. **Memory issues**
   - Reduce buffer sizes
   - Clear old data periodically
   - Monitor heap usage: `ESP.getFreeHeap()`

## Best Practices

1. **Error Handling**: Always implement retry logic
2. **Connection Pooling**: Reuse HTTP connections
3. **Data Validation**: Validate sensor readings before sending
4. **Buffering**: Store data locally if network is unavailable
5. **Monitoring**: Log all errors and connection status
6. **Updates**: Implement OTA (Over-The-Air) updates for remote maintenance

## Example Complete Integration

See `arduino_esp32_server_with_backend.ino` (to be created) for a complete example with:
- Real sensor reading
- HTTP backend integration
- MQTT support
- Error handling
- Local data buffering
- OTA updates

---

**Next Steps**:
1. Choose integration method (HTTP, MQTT, or WebSocket)
2. Configure backend endpoints
3. Test with simulated data
4. Connect real sensors
5. Deploy and monitor

For more information, see the main project README.md
