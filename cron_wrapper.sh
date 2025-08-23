#!/bin/bash

# Weather Monitor Cron Wrapper Script
set -euo pipefail

# Configuration
PROJECT_DIR="/home/mike/Projects/weather-monitor"
PYTHON_PATH="/home/mike/miniconda3/bin/python"
LOG_FILE="$PROJECT_DIR/logs/cron.log"

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_DIR/logs"

# Function to log with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Start logging
log_message "Starting weather monitor cron job"

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    log_message "ERROR: Project directory not found: $PROJECT_DIR"
    exit 1
fi

# Check if Python exists
if [ ! -f "$PYTHON_PATH" ]; then
    log_message "ERROR: Python not found: $PYTHON_PATH"
    exit 1
fi

# Change to project directory
cd "$PROJECT_DIR" || {
    log_message "ERROR: Failed to change to project directory"
    exit 1
}

# Check if main script exists
if [ ! -f "weather_monitor.py" ]; then
    log_message "ERROR: weather_monitor.py not found"
    exit 1
fi

# Run the weather monitor
log_message "Executing weather monitor..."
if "$PYTHON_PATH" weather_monitor.py fetch-weather --hours 6 >> "$LOG_FILE" 2>&1; then
    log_message "Weather monitor completed successfully"
else
    log_message "ERROR: Weather monitor failed"
    exit 1
fi
