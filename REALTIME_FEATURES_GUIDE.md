# Real-time Data Updates Guide

This guide explains the new automatic data refresh functionality added to the FroidPredict dashboard.

## 🚀 Features

### Automatic Data Refresh
- **Predictions Count**: Updates every 30 seconds
- **Alerts Count**: Updates every 30 seconds  
- **System Status**: Updates every 10 seconds
- **Database Status**: Real-time monitoring
- **System Uptime**: Live percentage tracking

### Visual Indicators
- 🔴 **Live Status Indicator**: Shows "Live" with pulsing green dot
- 🔄 **Refresh Animation**: Spinning icon during data updates
- ⏰ **Last Update Time**: Displays exact time of last refresh
- 📊 **Real-time Badges**: Animated counters for alerts and predictions

## 🔧 API Endpoints

### New Real-time Endpoints

#### Get Predictions Count
```
GET /api/predictions/count
```
Response:
```json
{
  "status": "success",
  "count": 42,
  "timestamp": "2025-07-14T10:30:45.123456"
}
```

#### Get Alerts Count
```
GET /api/alerts/count
```
Response:
```json
{
  "status": "success", 
  "count": 3,
  "timestamp": "2025-07-14T10:30:45.123456"
}
```

#### Get System Status
```
GET /api/system/status
```
Response:
```json
{
  "status": "success",
  "system_status": "online",
  "db_status": "connected", 
  "uptime": 98.5,
  "timestamp": "2025-07-14T10:30:45.123456",
  "services": {
    "mongodb": true,
    "api": true, 
    "predictions": true,
    "alerts": true
  }
}
```

## 🎛️ Configuration

### Sidebar Component Props
```vue
<Sidebar 
  :initial-prediction-count="0"
  :initial-alert-count="0"
  :refresh-interval="30000"    <!-- 30 seconds -->
  :status-interval="10000"     <!-- 10 seconds -->
/>
```

### Customizing Refresh Intervals
You can adjust the refresh rates by modifying the props:

```vue
<!-- Fast updates (10 seconds) -->
<Sidebar :refresh-interval="10000" :status-interval="5000" />

<!-- Slow updates (2 minutes) -->
<Sidebar :refresh-interval="120000" :status-interval="60000" />
```

## 🔍 How It Works

### 1. Component Initialization
- Sidebar component mounts and sets up reactive data variables
- Initial data fetch occurs immediately
- Two separate intervals are established for different refresh rates

### 2. Data Fetching
```javascript
// Fetch predictions and alerts count
const fetchSystemData = async () => {
  // GET /api/predictions/count
  // GET /api/alerts/count
}

// Fetch system and database status
const fetchSystemStatus = async () => {
  // GET /api/system/status
}
```

### 3. Automatic Updates
- **Data Interval**: Refreshes counts every 30 seconds
- **Status Interval**: Refreshes system status every 10 seconds
- **Manual Refresh**: Click the refresh button for immediate update

### 4. Error Handling
- Failed requests don't break the interface
- Previous values are maintained on error
- Console warnings for debugging

## 🎨 UI Features

### Status Indicators
- **Green Pulsing Dot**: System online and connected
- **Red Solid Dot**: System offline or disconnected
- **Blue Badge**: Live data indicator
- **Spinning Icon**: Data refresh in progress

### Navigation Badges
- **Alert Count**: Red badge with pulse animation when > 0
- **Prediction Count**: Blue badge with smooth transitions
- **Real-time Updates**: Badges update automatically without page refresh

### System Health Cards
- **System Status**: Online/Offline with uptime percentage
- **Database Status**: Connected/Disconnected with visual indicators
- **Last Update**: Timestamp of most recent data refresh

## 🧪 Testing

### Manual Testing
1. Start the Flask backend: `python app.py`
2. Start the Vue frontend: `npm run dev`
3. Open browser and watch the sidebar for live updates
4. Check console for any errors

### Automated Testing
Run the test script:
```bash
python test_realtime_api.py
```

This will verify all API endpoints are working correctly.

### Monitoring Network Requests
1. Open browser developer tools (F12)
2. Go to Network tab
3. Watch for periodic requests to `/api/predictions/count`, `/api/alerts/count`, and `/api/system/status`

## 🛠️ Troubleshooting

### Common Issues

#### No Data Updates
- Check if Flask backend is running on port 5000
- Verify API endpoints are accessible
- Check browser console for CORS errors

#### High Server Load
- Increase refresh intervals in component props
- Consider implementing WebSocket for real-time updates
- Add request caching on backend

#### MongoDB Connection Issues
- API will gracefully fallback to in-memory data
- Database status will show "disconnected"
- System continues to function with reduced features

### Debug Mode
Add this to your browser console to see refresh activity:
```javascript
// Enable debug logging
localStorage.setItem('debug-sidebar', 'true')
```

## 🚀 Future Enhancements

### Planned Features
- **WebSocket Integration**: Real-time push notifications
- **Smart Refresh**: Adaptive intervals based on data change frequency
- **Offline Support**: Cached data when server is unavailable
- **User Preferences**: Customizable refresh rates per user

### Performance Optimizations
- **Request Batching**: Combine multiple API calls
- **Data Compression**: Minimize bandwidth usage
- **Smart Caching**: Reduce redundant requests
- **Background Updates**: Refresh data when tab is inactive

## 📚 Related Files

- `frontend/src/components/Sidebar.vue` - Main sidebar component with real-time features
- `frontend/src/components/Layout.vue` - Layout wrapper component
- `app.py` - Flask backend with new API endpoints
- `test_realtime_api.py` - Testing script for API endpoints

---

**🎯 Result**: Your dashboard now updates automatically without manual page refreshes, providing a real-time monitoring experience for your refrigeration system!
