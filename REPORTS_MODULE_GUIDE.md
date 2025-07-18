# 📊 Reports & Analytics Module

## Overview

The Reports module provides comprehensive reporting and analytics capabilities for the FroidPredict refrigeration maintenance system. Users can generate, download, and schedule various types of reports with customizable date ranges and format options.

## 🎯 Features

### Report Types

1. **Alerts Report**
   - Comprehensive alerts analysis with severity breakdown
   - Trend analysis over time
   - Available formats: PDF, Excel
   - Includes high/medium/low severity categorization

2. **Predictions Report**
   - Machine learning predictions analysis
   - Accuracy metrics and confidence levels
   - Normal vs failure prediction breakdown
   - Available formats: PDF, Excel

3. **Thermodynamic Diagrams Report**
   - Complete Mollier diagrams package
   - Pedagogical diagrams for training
   - System performance analysis
   - Available formats: ZIP (multiple diagrams), PDF (analysis)

4. **System Performance Report**
   - Comprehensive system health analysis
   - Uptime statistics and KPIs
   - COP (Coefficient of Performance) analysis
   - Available formats: PDF

5. **Custom Reports**
   - User-configurable report sections
   - Mix and match different data types
   - Flexible content selection
   - Available formats: PDF

6. **Scheduled Reports**
   - Automated report generation
   - Daily, weekly, monthly frequencies
   - Configurable report types
   - Background processing

### Date Range Filtering

- **Custom Date Range**: Select specific start and end dates
- **Quick Presets**: 
  - Last 24 Hours
  - Last 3 Days
  - Last Week
  - Last Month
  - Last 3 Months

### Download Formats

- **PDF**: Professional reports with analysis
- **Excel**: Data-rich spreadsheets for further analysis
- **ZIP**: Complete diagram packages
- **Text**: Raw data exports

## 🚀 Getting Started

### Prerequisites

1. **Backend Dependencies**:
   ```bash
   pip install pandas openpyxl xlsxwriter
   ```

2. **Frontend Dependencies**:
   ```bash
   npm install @heroicons/vue
   ```

### Setup

1. **Start the Backend Server**:
   ```bash
   python app.py
   ```

2. **Start the Frontend Development Server**:
   ```bash
   npm run dev
   ```

3. **Access the Reports Page**:
   ```
   http://localhost:3000/reports
   ```

## 🛠️ API Endpoints

### Generate Alerts Report
```http
POST /api/reports/alerts
Content-Type: application/json

{
  "format": "pdf|excel",
  "dateRange": {
    "start": "2025-01-01T00:00:00",
    "end": "2025-01-31T23:59:59"
  },
  "includeBreakdown": true,
  "includeTrends": true
}
```

### Generate Predictions Report
```http
POST /api/reports/predictions
Content-Type: application/json

{
  "format": "pdf|excel",
  "dateRange": {
    "start": "2025-01-01T00:00:00",
    "end": "2025-01-31T23:59:59"
  },
  "includeAccuracy": true,
  "includeTrends": true
}
```

### Generate Diagrams Report
```http
POST /api/reports/diagrams
Content-Type: application/json

{
  "type": "complete|analysis",
  "dateRange": {
    "start": "2025-01-01T00:00:00",
    "end": "2025-01-31T23:59:59"
  },
  "includeAnalysis": true
}
```

### Generate System Report
```http
POST /api/reports/system
Content-Type: application/json

{
  "type": "comprehensive|summary",
  "dateRange": {
    "start": "2025-01-01T00:00:00",
    "end": "2025-01-31T23:59:59"
  },
  "includePerformance": true,
  "includeHealth": true
}
```

### Generate Custom Report
```http
POST /api/reports/custom
Content-Type: application/json

{
  "dateRange": {
    "start": "2025-01-01T00:00:00",
    "end": "2025-01-31T23:59:59"
  },
  "sections": {
    "includeAlerts": true,
    "includePredictions": true,
    "includeDiagrams": false,
    "includePerformance": true
  }
}
```

### Create Scheduled Report
```http
POST /api/reports/schedule
Content-Type: application/json

{
  "frequency": "daily|weekly|monthly",
  "reportType": "alerts|predictions|system|comprehensive",
  "dateRange": {
    "start": "2025-01-01T00:00:00",
    "end": "2025-01-31T23:59:59"
  }
}
```

## 🎨 UI Components

### Main Reports Dashboard

The Reports page (`/reports`) provides:

- **Date Range Selector**: Choose custom dates or quick presets
- **Report Type Cards**: Visual cards for each report type
- **Generation Progress**: Real-time progress indicators
- **Recent Downloads**: History of generated reports
- **Scheduled Reports**: Manage automated reports

### Report Cards

Each report type has a dedicated card showing:
- Report description and capabilities
- Current data metrics (alert counts, prediction counts, etc.)
- Download options (PDF/Excel/ZIP)
- Generation status and progress

### Progress Indicators

- **Modal Progress Dialog**: Shows generation progress
- **Card-level Status**: Individual report generation status
- **Download History**: Track of completed and failed reports

## 📈 Metrics & Analytics

### System Metrics Calculated

1. **Alert Metrics**:
   - Total alert count by date range
   - Severity breakdown (High/Medium/Low)
   - Alert rate trends
   - Machine-specific alert patterns

2. **Prediction Metrics**:
   - Total predictions generated
   - Normal vs failure prediction ratio
   - Prediction accuracy rate
   - Confidence level distribution

3. **System Performance**:
   - System health score
   - Uptime percentage
   - Average COP (Coefficient of Performance)
   - Active machine count

4. **Thermodynamic Analysis**:
   - Mollier diagram parameters
   - Refrigeration cycle efficiency
   - Temperature and pressure trends
   - Energy efficiency metrics

## 🔧 Customization

### Adding New Report Types

1. **Backend**: Add new endpoint in `app.py`
   ```python
   @app.route('/api/reports/new_type', methods=['POST'])
   def generate_new_report():
       # Implementation
       pass
   ```

2. **Frontend**: Add new card in `Reports.vue`
   ```vue
   <!-- New Report Card -->
   <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
     <!-- Card content -->
   </div>
   ```

### Custom Date Presets

Add new presets in `Reports.vue`:
```javascript
const datePresets = [
  { label: 'Last 6 Months', days: 180 },
  { label: 'Last Year', days: 365 },
  // Add more presets
]
```

### Custom Report Sections

Extend the custom report configuration:
```javascript
const customReport = ref({
  includeAlerts: true,
  includePredictions: true,
  includeDiagrams: false,
  includePerformance: true,
  includeNewSection: false  // Add new section
})
```

## 🧪 Testing

### Manual Testing

1. **Run Test Script**:
   ```bash
   python test_reports.py
   ```

2. **Test Individual Reports**:
   - Navigate to `/reports`
   - Select date range
   - Generate each report type
   - Verify downloads

### Automated Testing

The test script covers:
- All API endpoints
- Response validation
- Error handling
- Frontend integration

## 🚨 Troubleshooting

### Common Issues

1. **"Reports page not found"**
   - Ensure router has reports route
   - Check frontend server is running
   - Verify navigation links

2. **"API endpoint not found"**
   - Confirm Flask server is running on port 5002
   - Check CORS configuration
   - Verify endpoint paths

3. **"Report generation failed"**
   - Check server logs for errors
   - Verify database connectivity
   - Ensure required packages installed

4. **"Download not working"**
   - Check browser download settings
   - Verify file permissions
   - Clear browser cache

### Debug Mode

Enable debug logging in `app.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Dependencies

### Backend
- `flask`: Web framework
- `pandas`: Data processing
- `openpyxl`: Excel file generation
- `matplotlib`: Chart generation
- `pymongo`: Database operations

### Frontend
- `vue`: Frontend framework
- `@heroicons/vue`: Icon library
- `moment`: Date manipulation
- `axios`: HTTP client

## 🔄 Updates & Maintenance

### Version History

- **v1.0.0**: Initial reports module
  - Basic PDF/Excel generation
  - Date range filtering
  - Custom report sections

### Planned Features

- **v1.1.0**: Enhanced visualizations
  - Chart integration in reports
  - Interactive diagrams
  - Advanced analytics

- **v1.2.0**: Email delivery
  - Automated email reports
  - Report sharing
  - Notification system

## 📞 Support

For issues or questions regarding the Reports module:

1. Check the troubleshooting section
2. Review the test script output
3. Examine server logs
4. Verify all dependencies are installed

The Reports module provides a comprehensive solution for generating, downloading, and scheduling reports across all aspects of the refrigeration maintenance system.
