# Weather Monitor

A weather monitoring system that periodically collects weather data from various regions and stores it in a SQLite database.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Data Export](#data-export)
- [Cron Setup](#cron-setup)
- [Database Structure](#database-structure)
- [Supported Export Formats](#supported-export-formats)
- [Troubleshooting](#troubleshooting)
- [Monitoring](#monitoring)
- [Features](#features)

## Installation

### Prerequisites

- Python 3.7+ (recommended Python 3.8+)
- pip for installing dependencies
- Internet access for weather data retrieval

### Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure regions in `config.yaml`**

3. **Test the installation:**
```bash
python weather_monitor.py fetch-weather --verbose
```

## Usage

### Basic Data Collection Commands

```bash
# Collect data for the last 6 hours (recommended period)
python weather_monitor.py fetch-weather

# Collect data for the last 3 hours (for frequent runs)
python weather_monitor.py fetch-weather --hours 3

# Collect data for the last 12 hours (for infrequent runs)
python weather_monitor.py fetch-weather --hours 12
```

### Additional Options

```bash
# Specify custom configuration file path
python weather_monitor.py fetch-weather --config my_config.yaml

# Enable verbose logging
python weather_monitor.py fetch-weather --verbose

# View latest data for a specific region
python weather_monitor.py latest moscow
```

### Available Commands

```bash
# Show all available commands
python weather_monitor.py --help

# Get help for specific command
python weather_monitor.py fetch-weather --help
python weather_monitor.py export --help
```

## Configuration

The `config.yaml` file contains region and database settings:

```yaml
# Weather monitoring configuration
regions:
  # Active weather stations in Moscow region (with current data)
  moskva_station:
    name: "Moskva Station"
    latitude: 55.833
    longitude: 37.617
  ostafyevo:
    name: "Ostafyevo / Yazovo"
    latitude: 55.512
    longitude: 37.507
  # ... more regions
  
  # International stations
  belgrade:
    name: "Belgrade"
    latitude: 44.79
    longitude: 20.45

# Database settings
database:
  path: "weather_data.db"
```

### Adding New Regions

To add a new region, add an entry to the `regions` section:

```yaml
your_city:
  name: "Your City Name"
  latitude: XX.XX
  longitude: YY.YY
```

## Data Export

The system supports exporting data to multiple formats with flexible filtering options.

### Export Formats

```bash
# Export all data to CSV (default)
python weather_monitor.py export weather_data.csv

# Export to JSON with pretty formatting
python weather_monitor.py export weather_data.json --format json --pretty

# Export to XML
python weather_monitor.py export weather_data.xml --format xml

# Export to TSV (tab-separated values)
python weather_monitor.py export weather_data.tsv --format tsv

# Export to plain text format
python weather_monitor.py export weather_data.txt --format txt

# Export to SQL INSERT statements
python weather_monitor.py export weather_data.sql --format sql
```

### Data Filtering

```bash
# Export data for specific region only
python weather_monitor.py export moscow_data.csv --region moscow

# Export last 10 records
python weather_monitor.py export recent_data.json --format json --limit 10

# Export data for specific date range
python weather_monitor.py export period_data.csv --start-date "2025-08-23" --end-date "2025-08-24"

# Combine multiple filters
python weather_monitor.py export filtered_data.json --format json --region spb --limit 5 --pretty
```

## Cron Setup

### 🚀 Quick Setup

For automated data collection, use the provided setup script:

```bash
# Run the automatic setup script
./setup_cron.sh
```

This script will:
- Auto-detect your Python environment
- Create a wrapper script with correct paths
- Test the configuration
- Offer interactive cron setup

### Manual Cron Configuration

#### 1. Prepare the Wrapper Script

The wrapper script `run_weather_monitor.sh` ensures proper environment setup for cron execution.

**Important:** Check and adjust paths in `run_weather_monitor.sh` if needed:

```bash
# Edit the wrapper script
nano run_weather_monitor.sh

# Verify these lines:
PROJECT_DIR="/path/to/your/weather-monitor"  # Project path
PYTHON_PATH="/path/to/your/python"           # Python path
```

#### 2. Test the Wrapper Script

```bash
# Make script executable
chmod +x run_weather_monitor.sh

# Test execution
./run_weather_monitor.sh 1

# Check logs
cat logs/weather_monitor_cron.log
```

#### 3. Configure Cron

Open crontab editor:
```bash
crontab -e
```

Add one of the recommended schedules:

**🎯 OPTIMAL SETUP (recommended):**
```bash
# Every 30 minutes with 6-hour data window
*/30 * * * * /path/to/weather-monitor/run_weather_monitor.sh 6
```

**⚡ HIGH FREQUENCY:**
```bash
# Every 15 minutes with 3-hour data window
*/15 * * * * /path/to/weather-monitor/run_weather_monitor.sh 3
```

**💾 RESOURCE SAVING:**
```bash
# Every hour with 12-hour data window
0 * * * * /path/to/weather-monitor/run_weather_monitor.sh 12
```

#### 4. Verify Cron Setup

```bash
# Check cron service status
sudo systemctl status cron

# View active cron jobs
crontab -l

# Monitor logs
tail -f logs/weather_monitor_cron.log
```

### Advanced Cron Configuration

#### Email Notifications

```bash
# Add to the beginning of crontab for email notifications
MAILTO=your-email@example.com

# Your cron jobs
*/30 * * * * /path/to/weather-monitor/run_weather_monitor.sh 6
```

#### Log Rotation

Create `/etc/logrotate.d/weather-monitor`:

```bash
sudo nano /etc/logrotate.d/weather-monitor
```

File content:
```
/path/to/weather-monitor/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 user user
}
```

#### Business Hours Only

```bash
# Only run from 8:00 to 22:00 on weekdays
*/30 8-22 * * 1-5 /path/to/weather-monitor/run_weather_monitor.sh 6

# Less frequent on weekends (every 2 hours)
0 */2 * * 6,7 /path/to/weather-monitor/run_weather_monitor.sh 6
```

## Database Structure

Data is stored in the `weather_data` table with the following fields:

### System Fields
- `id` - Primary key (auto-increment)
- `region_code` - Region identifier
- `region_name` - Region display name
- `latitude`, `longitude` - Geographic coordinates
- `timestamp` - Observation time (ISO format)
- `created_at` - Record creation timestamp

### Weather Parameters

#### ✅ Currently Monitored Parameters
- `temperature` - Temperature (°C) ← from `temp`
- `dewpoint` - Dew point (°C) ← from `dwpt`
- `humidity` - Relative humidity (%) ← from `rhum`
- `precipitation` - Precipitation (mm) ← from `prcp`
- `pressure` - Atmospheric pressure (hPa) ← from `pres`
- `wind_speed` - Wind speed (km/h) ← from `wspd`
- `wind_direction` - Wind direction (degrees) ← from `wdir`
- `cloud_cover` - Cloud cover (oktas 0-8) ← from `coco`
- `snow_depth` - Snow depth (mm) ← from `snow`
- `wind_gust` - Wind gusts (km/h) ← from `wpgt`
- `sunshine_duration` - Sunshine duration (minutes) ← from `tsun`

### Parameter Details

| Database Field | Source API | Description | Units | Range/Notes |
|---|---|---|---|---|
| `temperature` | `temp` | Air temperature | °C | Celsius degrees |
| `dewpoint` | `dwpt` | Dew point temperature | °C | Temperature at which air becomes saturated |
| `humidity` | `rhum` | Relative humidity | % | 0-100% |
| `precipitation` | `prcp` | Precipitation amount | mm | Millimeters of water equivalent |
| `pressure` | `pres` | Atmospheric pressure | hPa | Hectopascals (millibars) |
| `wind_speed` | `wspd` | Wind speed | km/h | Kilometers per hour |
| `wind_direction` | `wdir` | Wind direction | degrees | 0-360°, where 0° = North |
| `cloud_cover` | `coco` | Cloud coverage | oktas | 0-8 scale (0=clear, 8=overcast) |
| `snow_depth` | `snow` | Snow depth | mm | Millimeters of snow on ground |
| `wind_gust` | `wpgt` | Wind gust speed | km/h | Maximum wind speed in gusts |
| `sunshine_duration` | `tsun` | Sunshine duration | minutes | Minutes of direct sunlight |

### Database Schema

```sql
CREATE TABLE weather_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    region_code TEXT NOT NULL,
    region_name TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    timestamp TEXT NOT NULL,
    temperature REAL,
    dewpoint REAL,
    humidity REAL,
    precipitation REAL,
    pressure REAL,
    wind_speed REAL,
    wind_direction REAL,
    cloud_cover REAL,
    snow_depth REAL,
    wind_gust REAL,
    sunshine_duration REAL,
    created_at TEXT NOT NULL,
    UNIQUE(region_code, timestamp)
);
```

## Supported Export Formats

- **CSV** - Comma-separated values (default)
- **TSV** - Tab-separated values
- **JSON** - JavaScript Object Notation with pretty formatting option
- **XML** - Structured XML with metadata
- **TXT** - Plain text format with delimiters
- **SQL** - INSERT statements for importing to other databases

## Troubleshooting

### Common Issues

#### Issue: Cron doesn't start

**Check:**
1. Cron service status: `sudo systemctl status cron`
2. Crontab syntax: `crontab -l`
3. Script permissions: `ls -la run_weather_monitor.sh`

**Solution:**
```bash
# Restart cron service
sudo systemctl restart cron

# Check system logs
sudo journalctl -u cron -f
```

#### Issue: Script can't find Python

**Check Python path:**
```bash
which python
# Update PYTHON_PATH in run_weather_monitor.sh
```

#### Issue: No permission to write logs

**Create log directory:**
```bash
mkdir -p /path/to/weather-monitor/logs
chmod 755 /path/to/weather-monitor/logs
```

#### Issue: Environment variables not loaded

**Add to wrapper script:**
```bash
# Load user profile
source ~/.bashrc
source ~/.profile
```

### Debug Commands

```bash
# Test weather data collection
python weather_monitor.py fetch-weather --hours 1 --verbose

# Check database records
python -c "import sqlite3; conn=sqlite3.connect('weather_data.db'); print('Records:', conn.execute('SELECT COUNT(*) FROM weather_data').fetchone()[0])"

# View recent logs
tail -20 logs/weather_monitor_cron.log

# Test export functionality
python weather_monitor.py export test.csv --limit 5
```

## Monitoring

### Status Checking

Create a simple status checker:

```bash
cat > check_status.sh << 'EOF'
#!/bin/bash
echo "=== Weather Monitor Status ==="
echo "Last cron run: $(tail -1 logs/weather_monitor_cron.log | head -c 19 2>/dev/null || echo "No log")"
echo "Database records: $(python -c "import sqlite3; conn=sqlite3.connect('weather_data.db'); print(conn.execute('SELECT COUNT(*) FROM weather_data').fetchone()[0])" 2>/dev/null || echo "Error")"
echo "Log file size: $(du -h logs/weather_monitor_cron.log 2>/dev/null | cut -f1 || echo "No log")"
echo "Active regions: $(python -c "import sqlite3; conn=sqlite3.connect('weather_data.db'); print(conn.execute('SELECT COUNT(DISTINCT region_code) FROM weather_data').fetchone()[0])" 2>/dev/null || echo "Error")"
EOF

chmod +x check_status.sh
./check_status.sh
```

### Log Monitoring

```bash
# Real-time log monitoring
tail -f logs/weather_monitor_cron.log

# System cron logs
sudo tail -f /var/log/syslog | grep CRON

# Check for errors in logs
grep -i error logs/weather_monitor_cron.log
```

### Performance Monitoring

```bash
# Database size
du -h weather_data.db

# Records per region
python -c "
import sqlite3
conn = sqlite3.connect('weather_data.db')
cursor = conn.cursor()
cursor.execute('SELECT region_name, COUNT(*) as count FROM weather_data GROUP BY region_name ORDER BY count DESC')
for row in cursor.fetchall():
    print(f'{row[0]}: {row[1]} records')
"

# Latest data timestamps
python -c "
import sqlite3
conn = sqlite3.connect('weather_data.db')
cursor = conn.cursor()
cursor.execute('SELECT region_name, MAX(timestamp) as latest FROM weather_data GROUP BY region_name ORDER BY latest DESC')
for row in cursor.fetchall():
    print(f'{row[0]}: {row[1]}')
"
```

## Features

### Core Features

- **Automatic duplicate prevention** - Checks existing records before saving
- **Network error resilience** - Handles temporary network issues gracefully
- **Comprehensive logging** - Detailed operation logs for monitoring
- **Flexible region configuration** - Easy to add/remove monitoring locations
- **Multiple export formats** - Export data in 6 different formats
- **Advanced filtering** - Filter exports by region, date range, and record count

### Data Collection Features

- **Configurable time windows** - Collect data for 1-24 hour periods
- **Multiple weather stations** - Support for 19+ weather stations in Moscow region
- **International support** - Monitor weather stations worldwide
- **Hourly data frequency** - Most stations provide hourly updates
- **Complete weather parameters** - Temperature, humidity, pressure, wind, precipitation, cloud cover, snow depth, wind gusts, sunshine duration

### Automation Features

- **Cron integration** - Automated data collection via cron jobs
- **Environment detection** - Automatic Python and path detection
- **Wrapper scripts** - Proper environment setup for cron execution
- **Error handling** - Comprehensive error logging and recovery
- **Status monitoring** - Built-in tools for system health checking

### Export and Analysis Features

- **Six export formats** - CSV, TSV, JSON, XML, TXT, SQL
- **Flexible filtering** - By region, date range, record limit
- **Pretty formatting** - Human-readable JSON and XML output
- **SQL compatibility** - Generate INSERT statements for database migration
- **Batch processing** - Export thousands of records efficiently

## Final Setup Verification

After installation and configuration:

```bash
# 1. Verify crontab
crontab -l

# 2. Test wrapper script
./run_weather_monitor.sh 1

# 3. Check system status
./check_status.sh

# 4. Monitor first automatic run
tail -f logs/weather_monitor_cron.log
```

## Recommended Production Setup

```bash
# Add to crontab (crontab -e):
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
MAILTO=""

# Optimal schedule: every 30 minutes with 6-hour window
*/30 * * * * /path/to/weather-monitor/run_weather_monitor.sh 6

# Weekly cleanup of old exports (optional)
0 2 * * 0 find /path/to/weather-monitor -name "*.csv" -o -name "*.json" -o -name "*.xml" -mtime +7 -delete
```

Your weather monitor is now ready to automatically collect weather data every 30 minutes!