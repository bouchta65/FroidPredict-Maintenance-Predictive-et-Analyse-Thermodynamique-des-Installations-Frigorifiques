# ESP32/ESP8266 Refrigeration Monitoring Web Server

This Arduino sketch provides a complete web server solution for monitoring refrigeration system parameters via a web interface.

## Features

✅ **WiFi-enabled web server** - Access monitoring dashboard from any device on the network  
✅ **Real-time sensor data** - Auto-refreshing sensor readings every 2 seconds  
✅ **RESTful API** - JSON endpoints for sensor data integration  
✅ **Responsive design** - Beautiful, mobile-friendly dashboard  
✅ **Multiple endpoints** - Support for various data access methods  
✅ **Simulated sensor data** - Built-in data generation for testing  

## Hardware Requirements

- ESP32 development board (recommended) **OR**
- ESP8266 development board (NodeMCU, Wemos D1 Mini, etc.)
- USB cable for programming
- WiFi network

## Software Requirements

### Arduino IDE Setup

1. **Install Arduino IDE** (version 1.8.13 or newer)
   - Download from: https://www.arduino.cc/en/software

2. **Add ESP32/ESP8266 Board Support**
   
   For ESP32:
   - File → Preferences → Additional Board Manager URLs
   - Add: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Tools → Board → Boards Manager → Search "ESP32" → Install

   For ESP8266:
   - Add: `http://arduino.esp8266.com/stable/package_esp8266com_index.json`
   - Tools → Board → Boards Manager → Search "ESP8266" → Install

3. **Install Required Libraries**
   
   Go to: Tools → Manage Libraries
   
   Install these libraries:
   - **ESPAsyncWebServer** by me-no-dev
   - **AsyncTCP** (for ESP32) OR **ESPAsyncTCP** (for ESP8266)

   If not available in Library Manager, install manually from:
   - ESPAsyncWebServer: https://github.com/me-no-dev/ESPAsyncWebServer
   - AsyncTCP: https://github.com/me-no-dev/AsyncTCP
   - ESPAsyncTCP: https://github.com/me-no-dev/ESPAsyncTCP

### PlatformIO Setup (Alternative)

Create a `platformio.ini` file:

```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
lib_deps = 
    me-no-dev/ESPAsyncWebServer@^1.2.3
    me-no-dev/AsyncTCP@^1.1.1

[env:nodemcuv2]
platform = espressif8266
board = nodemcuv2
framework = arduino
lib_deps = 
    me-no-dev/ESPAsyncWebServer@^1.2.3
    me-no-dev/ESPAsyncTCP@^1.2.2
```

## Installation & Configuration

### Step 1: Configure WiFi Credentials

Open `arduino_esp32_server.ino` and update these lines:

```cpp
const char* ssid = "YOUR_SSID";          // Replace with your WiFi name
const char* password = "YOUR_PASSWORD";  // Replace with your WiFi password
```

### Step 2: Select Your Board

In Arduino IDE:
- Tools → Board → Select your board:
  - **ESP32**: "ESP32 Dev Module" or your specific ESP32 board
  - **ESP8266**: "NodeMCU 1.0 (ESP-12E Module)" or your specific board

### Step 3: Upload the Sketch

1. Connect your ESP32/ESP8266 board via USB
2. Select the correct Port: Tools → Port → (Select your device)
3. Click Upload button (→) in Arduino IDE
4. Wait for compilation and upload to complete

### Step 4: Monitor Serial Output

1. Open Serial Monitor: Tools → Serial Monitor
2. Set baud rate to **115200**
3. Watch for WiFi connection and IP address

You should see output like:
```
Connecting to WiFi...

✓ WiFi Connected Successfully
IP Address: 192.168.1.100
Open this address in your browser to view the dashboard
✓ Web server started successfully!
Available endpoints:
  - http://192.168.1.100/ (Main dashboard)
  - http://192.168.1.100/api/sensors (JSON sensor data)
  - http://192.168.1.100/api/status (System status)
```

## Usage

### Access the Dashboard

Open your web browser and navigate to the IP address shown in the Serial Monitor:

```
http://192.168.1.100/
```

The dashboard will automatically refresh sensor data every 2 seconds.

### API Endpoints

#### 1. Get Sensor Data (JSON)
```
GET http://192.168.1.100/api/sensors
```

Response:
```json
{
  "temp_evaporator": -10.5,
  "temp_condenser": 40.2,
  "pressure_high": 12.15,
  "pressure_low": 2.45,
  "superheat": 8.3,
  "subcooling": 5.1,
  "compressor_current": 8.7,
  "vibration": 0.025,
  "timestamp": 12345678
}
```

#### 2. Get System Status
```
GET http://192.168.1.100/api/status
```

Response:
```json
{
  "status": "online",
  "uptime": 123456,
  "rssi": -45,
  "free_heap": 234560
}
```

#### 3. Legacy GET Endpoint
```
GET http://192.168.1.100/get?message=hello
```

Response: `Hello, GET: hello`

#### 4. Legacy POST Endpoint
```
POST http://192.168.1.100/post
Content-Type: application/x-www-form-urlencoded

message=test_data
```

Response: `Hello, POST: test_data`

## Monitored Parameters

| Parameter | Description | Unit | Range |
|-----------|-------------|------|-------|
| Evaporator Temperature | Refrigerant evaporation temperature | °C | -30 to 0 |
| Condenser Temperature | Refrigerant condensation temperature | °C | 30 to 60 |
| High Pressure | Discharge side pressure | bar | 8 to 18 |
| Low Pressure | Suction side pressure | bar | 1 to 4 |
| Superheat | Temperature difference at evaporator | °C | 3 to 15 |
| Subcooling | Temperature difference at condenser | °C | 2 to 8 |
| Compressor Current | Electrical current draw | A | 5 to 12 |
| Vibration | Mechanical vibration level | g | 0 to 0.1 |

## Integration with Main System

### Connect to Python Backend

To send data to the main Python application, you can use HTTP POST requests:

```cpp
// Example: Send data to Python backend
void sendDataToBackend() {
    HTTPClient http;
    http.begin("http://your-python-server:5002/api/sensor_data");
    http.addHeader("Content-Type", "application/json");
    
    String json = "{";
    json += "\"machine_id\":1,";
    json += "\"temp_evaporator\":" + String(currentData.temp_evaporator) + ",";
    // ... add other fields
    json += "}";
    
    int httpCode = http.POST(json);
    http.end();
}
```

### Use with Kafka Producer

For real-time streaming, you can integrate with MQTT or HTTP to Kafka:

```cpp
// Send to MQTT broker (requires PubSubClient library)
client.publish("sensors/refrigeration", jsonString);
```

## Customization

### Modify Sensor Data Simulation

Edit the `updateSensorData()` function to:
- Use real sensor readings (DHT22, DS18B20, pressure sensors, etc.)
- Adjust simulation ranges
- Add more sensor parameters

```cpp
void updateSensorData() {
    // Replace with actual sensor readings
    currentData.temp_evaporator = readTempSensor(EVAPORATOR_PIN);
    currentData.pressure_high = readPressureSensor(HIGH_PRESSURE_PIN);
    // ...
}
```

### Add More Endpoints

```cpp
server.on("/api/custom", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send(200, "application/json", "{\"data\":\"value\"}");
});
```

### Customize Dashboard Appearance

The HTML/CSS is embedded in the sketch. Modify the `index_html` string to:
- Change colors and styling
- Add more sensor cards
- Modify layout and design

## Troubleshooting

### WiFi Connection Failed
- Verify SSID and password are correct
- Check that WiFi network is 2.4GHz (ESP8266 doesn't support 5GHz)
- Move device closer to router
- Check for special characters in password

### Cannot Access Web Page
- Verify IP address from Serial Monitor
- Ensure device and computer are on same network
- Check firewall settings
- Try pinging the IP address

### Library Errors During Compilation
- Install required libraries (ESPAsyncWebServer, AsyncTCP/ESPAsyncTCP)
- Use Library Manager in Arduino IDE
- Check library versions are compatible

### Upload Fails
- Select correct board and port
- Press BOOT button on ESP32 while uploading (if required)
- Try different USB cable
- Install CH340/CP2102 drivers if needed

## Performance Notes

- **Memory**: Uses ~40KB of heap memory for web server
- **Speed**: Async server handles multiple clients efficiently
- **Refresh Rate**: Dashboard updates every 2 seconds (configurable)
- **Concurrent Connections**: Supports multiple simultaneous clients

## Security Considerations

⚠️ **Important**: This is a basic implementation for internal networks. For production:

- Add authentication (username/password)
- Use HTTPS (SSL/TLS)
- Implement CORS policies
- Add input validation
- Use strong WiFi passwords

## License

This code is provided as-is for the FroidPredict project.

## Contributing

To add real sensor support:
1. Add sensor libraries to the sketch
2. Initialize sensors in `setup()`
3. Read sensors in `updateSensorData()`
4. Update the JSON response format if needed

## Support

For issues or questions:
- Check Serial Monitor for error messages
- Verify all libraries are installed
- Ensure board is properly selected
- Review WiFi credentials

---

**Created for FroidPredict - Predictive Maintenance System**  
*Version 1.0.0*
