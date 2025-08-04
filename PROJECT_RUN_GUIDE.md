# 🚀 FroidPredict Project - Complete Run Guide

## 📋 Quick Access URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Main Application** | [http://localhost:3000](http://localhost:3000) | Vue.js Frontend Dashboard |
| **Backend API** | [http://localhost:5002](http://localhost:5002) | Flask API Server |
| **MongoDB Express** | [http://localhost:8081](http://localhost:8081) | Database Management Interface |
| **Kafka UI** | [http://localhost:8080](http://localhost:8080) | Kafka Stream Management |

## 🏃‍♂️ How to Run This Project

### Option 1: One-Click Startup (Recommended)
```powershell
# Run all services at once
.\run_all_services.ps1
```

### Option 2: Manual Step-by-Step
```powershell
# 1. Start Docker services
docker-compose up -d

# 2. Activate Python environment
.\.venv\Scripts\Activate.ps1

# 3. Start backend API
python app.py

# 4. In a new terminal, start frontend
npm run dev
```

## 🔧 Prerequisites Check

Before running, verify your system meets the requirements:
```powershell
# Check all prerequisites
.\check_prerequisites.ps1
```

**Required:**
- ✅ Python 3.11.9
- ✅ Node.js & npm
- ✅ Docker Desktop (running)
- ✅ Git

## 🛠️ Services Overview

### 🐳 Docker Infrastructure
```bash
# Status check
docker ps

# Services running:
- MongoDB (Port 27017)
- Kafka (Port 9092)
- Zookeeper (Port 2181)
- Mongo Express (Port 8081)
- Kafka UI (Port 8080)
```

### 🎯 Backend API (Flask)
- **URL**: http://localhost:5002
- **Features**: 
  - Predictive maintenance AI
  - Real-time sensor monitoring
  - Report generation (PDF/Excel)
  - Thermodynamic chart generation
  - WebSocket real-time updates

### 🌐 Frontend Dashboard (Vue.js)
- **URL**: http://localhost:3000
- **Features**:
  - Modern responsive UI
  - Real-time data visualization
  - Interactive reports page
  - Thermodynamic diagrams
  - Alert management system

## 📊 Key Features Available

### 1. Reports Dashboard
- **Location**: Main menu → Reports
- **Features**:
  - Enhanced UI with gradient designs
  - Real-time alert counts
  - PDF/Excel report downloads
  - Data filtering and search
  - Professional thermodynamic charts

### 2. Thermodynamic Charts
- **Types**: Pressure-Enthalpy (p-h), Entropy-Pressure (S-p), Pressure-Volume (p-v)
- **Fluids**: R22, R410A, R134a, R717 (Ammonia)
- **Export**: SVG, PNG, PDF formats
- **Features**: Professional quality diagrams with grid lines and property curves

### 3. Real-time Monitoring
- **Auto-predictions**: Every 30 seconds
- **Live alerts**: Instant notifications
- **System status**: Component health monitoring
- **Data streaming**: Kafka-powered real-time updates

## 🔍 Troubleshooting

### Common Issues & Solutions

#### Port Conflicts
```powershell
# Kill processes on common ports
Stop-Process -Name python -Force -ErrorAction SilentlyContinue
Stop-Process -Name node -Force -ErrorAction SilentlyContinue

# Check what's using a port
netstat -ano | findstr :5002
```

#### Docker Issues
```powershell
# Restart Docker services
docker-compose down
docker-compose up -d

# Check logs
docker logs mongodb
docker logs kafka
```

#### Python Environment
```powershell
# Recreate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### Frontend Issues
```powershell
# Clear cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
npm run dev
```

## 🚦 Service Status Verification

### Check All Services
```powershell
# Backend health check
curl http://localhost:5002/api/system/status

# Frontend access
curl http://localhost:3000

# Database access
curl http://localhost:8081

# Kafka UI access
curl http://localhost:8080
```

### Expected Responses
- ✅ **Backend**: JSON response with system status
- ✅ **Frontend**: HTML page loading
- ✅ **MongoDB Express**: Database interface
- ✅ **Kafka UI**: Stream management interface

## 📈 Data Flow Architecture

```
[Sensors] → [Kafka] → [MongoDB] → [Flask API] → [Vue.js Frontend]
    ↓           ↓         ↓          ↓              ↓
[Real Data] [Streaming] [Storage] [Processing] [Visualization]
```

## 🎨 New UI Features (Recently Added)

### Enhanced Reports Page
- **Modern Design**: Gradient backgrounds and glass-morphism effects
- **Improved UX**: Better spacing, typography, and visual hierarchy
- **Real-time Updates**: Live data refresh with loading animations
- **Professional Charts**: High-quality thermodynamic diagrams
- **Export Options**: Multiple format downloads (PDF, Excel, SVG, PNG)

### Loading Animations
- **Multi-ring Spinners**: Enhanced visual feedback
- **Orbiting Dots**: Professional loading indicators
- **Smooth Transitions**: Improved user experience

## 📞 Support & Development

### Development Scripts
```powershell
# Start with reports module
.\start_with_reports.ps1

# Monitor system status
.\check_services_status.ps1

# Stop all services
.\stop_all_services.bat
```

### Debug Mode
```powershell
# Backend debug mode (auto-reload)
$env:FLASK_DEBUG="1"
python app.py

# Frontend debug mode (with source maps)
npm run dev -- --debug
```

## 🎯 Success Indicators

When everything is running correctly, you should see:

1. **Frontend (localhost:3000)**:
   - Dashboard loads without errors
   - Real-time counters updating
   - Reports page with modern UI
   - Thermodynamic charts generating

2. **Backend (localhost:5002)**:
   - API endpoints responding
   - Auto-predictions generating
   - MongoDB connection established
   - Socket.IO connections active

3. **Docker Services**:
   - All 5 containers running
   - No restart loops
   - Ports accessible

## 🔗 Additional Resources

- **API Documentation**: `API_DOCUMENTATION.md`
- **Thermodynamic Charts Guide**: `DIAGRAMME_ENTHALPIQUE_GUIDE.md`
- **Real-time Features**: `REALTIME_FEATURES_GUIDE.md`
- **Reports Module**: `REPORTS_MODULE_GUIDE.md`

---

**🎉 Your FroidPredict application is now fully operational!**

Access the main dashboard at: **[http://localhost:3000](http://localhost:3000)**
