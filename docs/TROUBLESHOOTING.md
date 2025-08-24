# Troubleshooting Guide

This guide helps you resolve common issues with the Weather Monitor system.

## Common Issues

### 1. Database Connection Issues

**Problem:** Database connection errors or missing database file.

**Symptoms:**
- `Error: Database file 'weather_data.db' not found`
- `sqlite3.OperationalError: no such table: weather_data`

**Solutions:**

1. **Create database by running data collection:**
```bash
python weather_monitor.py fetch-weather --verbose
```

2. **Check database file permissions:**
```bash
ls -la weather_data.db
chmod 644 weather_data.db
```

3. **Verify database integrity:**
```bash
sqlite3 weather_data.db "PRAGMA integrity_check;"
```

### 2. Missing Dependencies

**Problem:** Import errors for required libraries.

**Symptoms:**
- `ModuleNotFoundError: No module named 'matplotlib'`
- `ImportError: plotext not available for ASCII plotting`

**Solutions:**

1. **Install all dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install specific missing packages:**
```bash
pip install matplotlib plotext rich flask flask-cors plotly openpyxl reportlab
```

3. **Check Python environment:**
```bash
python --version
pip list | grep -E "(matplotlib|plotext|rich|flask|plotly)"
```

### 3. Web Server Issues

**Problem:** Web server won't start or is inaccessible.

**Symptoms:**
- `Error: Flask not available, web server disabled`
- `Address already in use` error
- Browser shows "Connection refused"

**Solutions:**

1. **Install Flask dependencies:**
```bash
pip install flask flask-cors
```

2. **Check if port is already in use:**
```bash
netstat -tulpn | grep :8080
lsof -i :8080
```

3. **Use different port:**
```bash
python weather_monitor.py serve --port 8001
```

4. **Check firewall settings:**
```bash
sudo ufw status
sudo ufw allow 8080
```

### 4. Data Collection Issues

**Problem:** No weather data is being collected.

**Symptoms:**
- Empty database after running fetch-weather
- `No data found` messages
- Network timeout errors

**Solutions:**

1. **Check internet connection:**
```bash
ping 8.8.8.8
curl -I https://meteostat.net
```

2. **Verify region configuration:**
```bash
python weather_monitor.py fetch-weather --verbose
```

3. **Check region codes:**
```bash
# List available regions
python -c "
from database import WeatherDatabase
db = WeatherDatabase('weather_data.db')
print('Available regions:', db.get_regions())
"
```

4. **Try different time periods:**
```bash
python weather_monitor.py fetch-weather --hours 12
```

### 5. Plotting Issues

**Problem:** Charts and plots not working.

**Symptoms:**
- `plotext not available for ASCII plotting`
- `matplotlib not available for file plotting`
- Empty or corrupted plot files

**Solutions:**

1. **Install plotting dependencies:**
```bash
pip install matplotlib plotext plotly
```

2. **Check terminal support for ASCII plots:**
```bash
python -c "import plotext; print('plotext version:', plotext.__version__)"
```

3. **Use file-based plots instead:**
```bash
python weather_monitor.py plot temperature --regions moscow --save plot.png
```

4. **Check display environment (for matplotlib):**
```bash
echo $DISPLAY
export DISPLAY=:0  # If needed
```

### 6. Export Issues

**Problem:** Data export not working.

**Symptoms:**
- `openpyxl not available for Excel export`
- `reportlab not available for PDF reports`
- Export files are empty or corrupted

**Solutions:**

1. **Install export dependencies:**
```bash
pip install openpyxl reportlab
```

2. **Check file permissions:**
```bash
ls -la /path/to/export/directory
chmod 755 /path/to/export/directory
```

3. **Use different export format:**
```bash
python weather_monitor.py export data.csv --format csv
```

4. **Check available disk space:**
```bash
df -h
```

### 7. Performance Issues

**Problem:** Slow performance or high resource usage.

**Symptoms:**
- Long response times
- High CPU/memory usage
- Timeout errors

**Solutions:**

1. **Limit data range:**
```bash
python weather_monitor.py plot temperature --regions moscow --hours 6
```

2. **Use data limits:**
```bash
python weather_monitor.py export data.csv --limit 1000
```

3. **Optimize database:**
```bash
sqlite3 weather_data.db "VACUUM; ANALYZE;"
```

4. **Check system resources:**
```bash
top
htop
free -h
```

### 8. Web Interface Issues

**Problem:** Web dashboard not working properly.

**Symptoms:**
- JavaScript errors in browser console
- Charts not loading
- API requests failing

**Solutions:**

1. **Check browser console for errors:**
   - Open Developer Tools (F12)
   - Check Console tab for JavaScript errors
   - Check Network tab for failed requests

2. **Verify API endpoints:**
```bash
curl http://localhost:8080/api/health
curl http://localhost:8080/api/regions
```

3. **Check CORS settings:**
   - Ensure Flask-CORS is installed
   - Check server logs for CORS errors

4. **Clear browser cache:**
   - Hard refresh (Ctrl+F5)
   - Clear browser cache and cookies

### 9. Cron Job Issues

**Problem:** Automated data collection not working.

**Symptoms:**
- No data collected automatically
- Cron job not running
- Permission errors in logs

**Solutions:**

1. **Check cron service:**
```bash
sudo systemctl status cron
sudo systemctl start cron
```

2. **Verify crontab:**
```bash
crontab -l
crontab -e  # Edit if needed
```

3. **Check cron logs:**
```bash
sudo tail -f /var/log/cron
grep CRON /var/log/syslog
```

4. **Test wrapper script:**
```bash
./run_weather_monitor.sh 6
```

5. **Check file permissions:**
```bash
chmod +x run_weather_monitor.sh
chmod +x check_status.sh
```

### 10. Configuration Issues

**Problem:** Configuration file problems.

**Symptoms:**
- `Configuration file not found`
- Invalid configuration errors
- Wrong region data

**Solutions:**

1. **Check config file syntax:**
```bash
python -c "
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
print('Config loaded successfully')
"
```

2. **Verify YAML syntax:**
```bash
yamllint config.yaml
```

3. **Create backup and regenerate:**
```bash
cp config.yaml config.yaml.backup
# Edit config.yaml as needed
```

## Debugging Commands

### System Information

```bash
# Python version and environment
python --version
which python
pip list

# System information
uname -a
lsb_release -a
free -h
df -h

# Network connectivity
ping 8.8.8.8
curl -I https://meteostat.net
```

### Database Diagnostics

```bash
# Check database structure
sqlite3 weather_data.db ".schema"

# Check data count
sqlite3 weather_data.db "SELECT COUNT(*) FROM weather_data;"

# Check regions
sqlite3 weather_data.db "SELECT DISTINCT region_code FROM weather_data;"

# Check latest data
sqlite3 weather_data.db "SELECT region_code, timestamp, temperature FROM weather_data ORDER BY timestamp DESC LIMIT 5;"
```

### Application Diagnostics

```bash
# Test basic functionality
python weather_monitor.py --help
python weather_monitor.py fetch-weather --verbose

# Test plotting
python weather_monitor.py plot temperature --regions moscow --ascii

# Test web server
python weather_monitor.py serve --debug

# Test export
python weather_monitor.py export test.csv --format csv --limit 10
```

## Log Files

### Application Logs

- **Main logs:** `logs/weather_monitor.log`
- **Cron logs:** `logs/weather_monitor_cron.log`
- **Error logs:** `logs/errors.log`

### System Logs

- **Cron logs:** `/var/log/cron`
- **System logs:** `/var/log/syslog`
- **Apache/Nginx logs:** `/var/log/apache2/` or `/var/log/nginx/`

### Viewing Logs

```bash
# Follow logs in real-time
tail -f logs/weather_monitor.log

# Search for errors
grep -i error logs/weather_monitor.log

# View recent entries
tail -n 50 logs/weather_monitor.log
```

## Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Review the logs** for specific error messages
3. **Test with minimal configuration**
4. **Verify system requirements**

### Information to Provide

When asking for help, include:

1. **Error messages** (exact text)
2. **System information:**
   - OS version
   - Python version
   - Installed packages
3. **Configuration files** (sanitized)
4. **Log files** (relevant sections)
5. **Steps to reproduce** the issue

### Support Channels

- **GitHub Issues:** Create an issue in the project repository
- **Documentation:** Check README.md and API documentation
- **Community:** Check project discussions and forums

## Prevention

### Regular Maintenance

1. **Monitor logs** for errors
2. **Check disk space** regularly
3. **Update dependencies** periodically
4. **Backup database** regularly
5. **Test functionality** after system updates

### Best Practices

1. **Use virtual environments** for Python dependencies
2. **Keep system updated** with security patches
3. **Monitor system resources** (CPU, memory, disk)
4. **Use proper file permissions**
5. **Test changes** in development environment first


