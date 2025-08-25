# Weather Monitor

A modern weather monitoring system that collects weather data from Serbian meteorological stations and provides both CLI and web-based interfaces for data visualization and analysis.

## 🌟 Features

- **Real-time weather data collection** from 22 Serbian meteorological stations
- **Modern web dashboard** with interactive charts and real-time updates
- **CLI interface** for data collection, plotting, and export
- **Multiple data formats** support (CSV, JSON, PNG charts)
- **Automated data collection** via cron scheduling
- **Responsive web design** with modern UI/UX
- **Interactive charts** using Plotly.js
- **RESTful API** for programmatic access
- **Session state persistence** - dashboard settings are automatically saved and restored

![Weather Monitor Dashboard](docs/dashboard-screenshot.png)

## 📊 Supported Regions

The system currently monitors **22 Serbian weather stations**:

### Major Cities
- **Belgrade** (Београд) - Capital city
- **Novi Sad** (Нови Сад) - Second largest city
- **Niš** (Ниш) - Third largest city
- **Kragujevac** (Крагујевац) - Industrial center

### Regional Centers
- **Subotica** (Суботица) - Northern Serbia
- **Zrenjanin** (Зрењанин) - Vojvodina region
- **Pančevo** (Панчево) - Industrial city
- **Čačak** (Чачак) - Central Serbia
- **Kraljevo** (Краљево) - Central Serbia
- **Novi Pazar** (Нови Пазар) - Southwest Serbia

### Additional Stations
- **Leskovac, Vranje, Požarevac, Smederevo, Šabac, Valjevo, Kikinda, Sremska Mitrovica, Bečej, Vrbas, Sremski Karlovci, Inđija**

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd weather-monitor
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
./setup_dependencies.sh
```

3. **Initialize the database:**
```bash
python weather_monitor.py fetch-weather
```

4. **Start the web dashboard:**
```bash
python weather_monitor.py serve --host 0.0.0.0 --port 8080
```

5. **Open your browser:**
Navigate to `http://localhost:8080/dashboard`

## 📈 Usage

### Web Dashboard

The modern web interface provides:
- **Interactive region selection** with checkboxes
- **Real-time parameter selection** (temperature, humidity, pressure, wind speed, precipitation)
- **Dynamic time range selection** (6, 12, 24, 48 hours)
- **Interactive charts** with zoom, pan, and hover details
- **Responsive design** that works on desktop and mobile
- **Modern UI** with gradient accents and smooth animations
- **Session state persistence** - your settings are automatically saved and restored

```bash
# Start web server
python weather_monitor.py serve --host 0.0.0.0 --port 8080

# Access dashboard
# http://localhost:8080/dashboard
```

### CLI Commands

#### Data Collection
```bash
# Collect weather data for all Serbian stations
python weather_monitor.py fetch-weather

# Collect data for specific time period
python weather_monitor.py fetch-weather --hours 24

# Verbose output
python weather_monitor.py fetch-weather --verbose
```

#### Data Visualization
```bash
# Create ASCII plot for temperature in Belgrade
python weather_monitor.py plot temperature --regions belgrade --ascii

# Save plot as PNG file
python weather_monitor.py plot temperature --regions belgrade,novi_sad --save weather_plot.png

# Create plot for multiple metrics
python weather_monitor.py plot humidity --regions belgrade,nis,kragujevac --ascii

# Custom time range
python weather_monitor.py plot pressure --regions belgrade --hours 48 --ascii
```

#### Data Export
```bash
# Export data to CSV format
python weather_monitor.py export weather_data.csv --format csv

# Export data to JSON with pretty formatting
python weather_monitor.py export weather_data.json --format json --pretty

# Export data for specific region
python weather_monitor.py export belgrade_data.csv --format csv --region belgrade

# Export data with date range
python weather_monitor.py export data.csv --format csv --start-date 2024-01-01 --end-date 2024-01-31
```

#### System Information
```bash
# View latest data for a specific region
python weather_monitor.py latest belgrade

# Show all available commands
python weather_monitor.py --help

# Get help for specific command
python weather_monitor.py fetch-weather --help
```

## ⚙️ Configuration

### Database Settings
The system uses SQLite database (`weather_data.db`) for data storage.

### Region Configuration
Regions are configured in `config.yaml`:

```yaml
# Weather monitoring configuration
regions:
  belgrade:
    name: "Belgrade"
    latitude: 44.79
    longitude: 20.45
  novi_sad:
    name: "Novi Sad"
    latitude: 45.25
    longitude: 19.85
  # ... more Serbian stations

# Database settings
database:
  path: "weather_data.db"

# Plotting configuration
plotting:
  default_colors: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
  ascii_symbols: ['─', '┄', '┅', '┈', '┉']


```

### Adding New Regions

To add a new region, add an entry to the `regions` section:

```yaml
new_region:
  name: "Region Name"
  latitude: 44.123
  longitude: 20.456
```

## 🔧 Automation

### Cron Setup

For automated data collection, set up a cron job:

```bash
# Run setup script
./setup_cron.sh

# Or manually add to crontab
crontab -e

# Add line for every 6 hours
0 */6 * * * /path/to/weather-monitor/run_weather_monitor.sh
```

### Manual Cron Setup

1. **Edit crontab:**
```bash
crontab -e
```

2. **Add entry:**
```bash
# Collect weather data every 6 hours
0 */6 * * * /path/to/weather-monitor/run_weather_monitor.sh
```

## 📊 Data Structure

### Weather Metrics
- **Temperature** (°C)
- **Humidity** (%)
- **Pressure** (hPa)
- **Wind Speed** (m/s)
- **Precipitation** (mm)

### Database Schema
```sql
CREATE TABLE weather_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    region_code TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    temperature REAL,
    humidity REAL,
    pressure REAL,
    wind_speed REAL,
    precipitation REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    dashboard_state TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);
```

## 🌐 API Endpoints

The web server provides RESTful API endpoints:

- `GET /api/health` - System health status
- `GET /api/regions` - List all available regions

- `GET /api/weather-data` - Get weather data with filters
  - Parameters: `regions`, `metric`, `hours`, `limit`
- `GET /api/session/state` - Get dashboard session state
  - Parameters: `session_id`
- `POST /api/session/state` - Save dashboard session state
  - Parameters: `session_id`, body: JSON state data
- `POST /api/session/cleanup` - Clean up expired sessions

### Example API Usage
```bash
# Get temperature data for Belgrade
curl "http://localhost:8080/api/weather-data?regions=belgrade&metric=temperature&hours=24"

# Get humidity data for multiple regions
curl "http://localhost:8080/api/weather-data?regions=belgrade,novi_sad&metric=humidity&hours=48"

# Session management examples
curl "http://localhost:8080/api/session/state?session_id=my_session"
curl -X POST "http://localhost:8080/api/session/state?session_id=my_session" \
  -H "Content-Type: application/json" \
  -d '{"selected_regions":["belgrade"],"selected_metric":"temperature","selected_hours":24}'


```

## 🎨 Web Interface Features

### Modern Design
- **Light theme** with gradient accents
- **Responsive layout** for all screen sizes
- **Interactive elements** with hover effects
- **Smooth animations** and transitions
- **Professional typography** using Inter font

### Stable Color System
- **Consistent region colors** that remain unchanged regardless of selection order
- **Maximum color separation** using golden angle (137.508°) for distinct visualization
- **Index-based color generation** ensures adjacent regions have maximally different colors
- **Local color generation** without API requests for optimal performance
- **Deterministic colors** - same region index always gets same color

### Interactive Charts
- **Real-time updates** without page refresh
- **Zoom and pan** functionality
- **Hover tooltips** with detailed information
- **Multiple line support** for comparing regions
- **Export capabilities** (PNG, SVG)

### User Experience
- **Intuitive region selection** with checkboxes
- **Quick parameter switching** (temperature, humidity, etc.)
- **Flexible time range selection**
- **Loading indicators** and error handling
- **Mobile-friendly** interface
- **Session persistence** - dashboard settings are automatically saved and restored between visits

## 🔍 Monitoring and Logs

### Log Files
- `logs/weather_monitor.log` - Main application logs
- `logs/cron.log` - Cron job execution logs

### Health Monitoring
```bash
# Check system health via API
curl http://localhost:8080/api/health

# View latest logs
tail -f logs/weather_monitor.log
```

## 🛠️ Troubleshooting

### Common Issues

1. **Database not found:**
```bash
python weather_monitor.py fetch-weather
```

2. **Port already in use:**
```bash
python weather_monitor.py serve --port 8081
```

3. **Permission denied:**
```bash
chmod +x run_weather_monitor.sh
```

### Debug Mode
```bash
# Enable debug logging
python weather_monitor.py fetch-weather --verbose

# Start server in debug mode
python weather_monitor.py serve --debug
```

## 📋 Requirements

### System Requirements
- **Python:** 3.7+ (recommended 3.8+)
- **SQLite:** Built-in with Python
- **Internet:** Required for weather data retrieval

### Python Dependencies
- **matplotlib>=3.5.0** - Data visualization
- **plotext>=5.0.0** - ASCII charts
- **rich>=12.0.0** - Terminal output
- **flask>=2.0.0** - Web server
- **plotly>=5.0.0** - Interactive charts
- **jinja2>=3.0.0** - Templates
- **requests>=2.25.0** - HTTP requests
- **click>=8.0.0** - CLI framework

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in `logs/` directory
3. Create an issue on GitHub

---

**Weather Monitor** - Modern weather monitoring for Serbia 🇷🇸