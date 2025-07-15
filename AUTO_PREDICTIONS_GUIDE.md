# Automatic Prediction Generation System

## 🤖 Real-time Automatic Predictions

Your dashboard now generates predictions automatically every 15-45 seconds without any manual intervention!

## ✨ Features Added

### 🔄 **Automatic Generation**
- **Smart Intervals**: Random 15-45 second intervals to simulate real equipment
- **Realistic Data**: Generated sensor data mimics actual refrigeration systems
- **ML Predictions**: Each data point automatically runs through your trained model
- **Alert Generation**: Automatic alerts when conditions exceed thresholds

### 📡 **Real-time Updates**
- **WebSocket Connection**: Instant updates via Socket.IO
- **Live Badges**: Prediction and alert counters update immediately
- **Visual Feedback**: Bouncing animations when new data arrives
- **Connection Status**: Shows "Live" or "Polling" based on connection

### 🎯 **Generated Data Types**
- **Machine IDs**: AUTO_GEN_1 through AUTO_GEN_5
- **Sensor Data**: Temperature, pressure, current, vibration
- **Predictions**: Maintenance needed vs normal operation
- **Alerts**: Automatic alerts for critical conditions

## 🚀 How It Works

### 1. **Background Thread**
```python
# Runs continuously in Flask backend
def automatic_prediction_generator():
    while True:
        # Generate realistic sensor data
        # Make ML prediction
        # Store in database
        # Emit WebSocket events
        # Wait 15-45 seconds
```

### 2. **Real-time Frontend**
```javascript
// WebSocket connection in Sidebar.vue
socket.on('new_prediction', (data) => {
    predictionCount.value += 1
    // Visual feedback with bounce animation
})

socket.on('new_alert', (data) => {
    alertCount.value += 1
    // Alert badge pulses
})
```

### 3. **Generated Scenarios**
- **80% Normal Operations**: Typical sensor readings
- **20% Alert Conditions**: High temperatures, pressures, currents, vibrations

## 🎮 Controls

### API Endpoints
```bash
# Toggle automatic generation on/off
POST /api/auto-prediction/toggle
{"enabled": true}

# Check status
GET /api/auto-prediction/status
```

### Visual Indicators
- 🟢 **Green "Live"**: WebSocket connected, real-time updates
- 🟡 **Yellow "Polling"**: Fallback to HTTP polling
- 🔵 **Prediction Badge**: Bounces when new prediction arrives
- 🔴 **Alert Badge**: Pulses when new alert generated

## 📊 What You'll See

### Automatic Predictions Every 15-45 Seconds:
```
🤖 Auto-generated prediction for AUTO_GEN_3: ✅ Normal (confidence: 85.2%)
🤖 Auto-generated prediction for AUTO_GEN_1: ⚠️ Maintenance (confidence: 78.9%)
🚨 Generated 2 automatic alerts for AUTO_GEN_1
```

### Real-time Sidebar Updates:
- **Prediction Count**: Increments automatically
- **Alert Count**: Increases when critical conditions detected
- **Last Update Time**: Shows exact time of latest data
- **System Status**: Live monitoring of all components

## 🔧 Monitoring

### Console Logs
- Check browser console for WebSocket connection status
- Flask console shows generation activity
- Real-time feedback on predictions and alerts

### Database Storage
- All predictions stored in MongoDB (if available)
- Fallback to in-memory storage
- Sensor data and alerts also stored

## 🎯 Testing

1. **Start the System**:
   ```bash
   python app.py
   npm run dev
   ```

2. **Watch the Magic**:
   - Sidebar badges increment automatically
   - Console shows generation activity
   - Database grows with new predictions

3. **WebSocket Status**:
   - Look for "Live" indicator in sidebar
   - Green dot = WebSocket connected
   - Yellow dot = HTTP polling fallback

## 🚀 Result

Your dashboard now provides a **true real-time monitoring experience** with:
- ✅ Automatic prediction generation every 15-45 seconds
- ✅ Instant WebSocket updates to the UI
- ✅ Visual feedback with animations
- ✅ Realistic sensor data simulation
- ✅ Automatic alert generation
- ✅ No manual refresh needed!

The predictions are now being added automatically in real-time! 🎉
