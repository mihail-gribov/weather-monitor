"""Database module for weather monitoring."""

import sqlite3
import logging
import math
from datetime import datetime
from typing import Optional, Dict, Any


class WeatherDatabase:
    """Weather data database manager."""
    
    def __init__(self, db_path: str):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        self._init_database()
    
    def _safe_get_value(self, weather_row: Dict[str, Any], key: str) -> Optional[float]:
        """Safely get value from weather_row, converting NaN to None."""
        value = weather_row.get(key)
        if value is not None and (math.isnan(value) if isinstance(value, (int, float)) else False):
            return None
        return value
    
    def _init_database(self):
        """Create weather data table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weather_data (
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
                )
            ''')
            
            # Migrate existing database to add new columns if they don't exist
            self._migrate_database(cursor)
            
            conn.commit()
            logging.info("Database initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            raise
        finally:
            conn.close()
    
    def _migrate_database(self, cursor):
        """Add new columns to existing database if they don't exist."""
        # Check if new columns exist and add them if they don't
        new_columns = [
            ('cloud_cover', 'REAL'),
            ('snow_depth', 'REAL'),
            ('wind_gust', 'REAL'),
            ('sunshine_duration', 'REAL')
        ]
        
        for column_name, column_type in new_columns:
            try:
                cursor.execute(f'ALTER TABLE weather_data ADD COLUMN {column_name} {column_type}')
                logging.info(f"Added new column: {column_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    # Column already exists, which is fine
                    pass
                else:
                    logging.warning(f"Could not add column {column_name}: {e}")
    
    def record_exists(self, region_code: str, timestamp: datetime) -> bool:
        """Check if weather record already exists for given region and timestamp."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT 1 FROM weather_data WHERE region_code = ? AND timestamp = ?',
                (region_code, timestamp.isoformat())
            )
            return cursor.fetchone() is not None
        finally:
            conn.close()
    
    def save_weather_data(self, region_code: str, region_name: str, 
                         latitude: float, longitude: float,
                         weather_row: Dict[str, Any]) -> bool:
        """Save weather data record to database."""
        if not weather_row or 'time' not in weather_row:
            logging.warning("Invalid weather data - missing time field")
            return False
        
        timestamp = weather_row['time']
        
        # Check if record already exists
        if self.record_exists(region_code, timestamp):
            logging.info(f"Weather data for {region_code} at {timestamp} already exists, skipping")
            return False
        
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO weather_data (
                    region_code, region_name, latitude, longitude, timestamp,
                    temperature, dewpoint, humidity, precipitation, pressure,
                    wind_speed, wind_direction, cloud_cover, snow_depth,
                    wind_gust, sunshine_duration, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                region_code,
                region_name,
                latitude,
                longitude,
                timestamp.isoformat(),
                self._safe_get_value(weather_row, 'temp'),
                self._safe_get_value(weather_row, 'dwpt'),
                self._safe_get_value(weather_row, 'rhum'),
                self._safe_get_value(weather_row, 'prcp'),
                self._safe_get_value(weather_row, 'pres'),
                self._safe_get_value(weather_row, 'wspd'),
                self._safe_get_value(weather_row, 'wdir'),
                self._safe_get_value(weather_row, 'coco'),
                self._safe_get_value(weather_row, 'snow'),
                self._safe_get_value(weather_row, 'wpgt'),
                self._safe_get_value(weather_row, 'tsun'),
                datetime.now().isoformat()
            ))
            conn.commit()
            logging.info(f"Saved weather data for {region_name} at {timestamp}")
            return True
        except sqlite3.IntegrityError:
            logging.warning(f"Weather data for {region_code} at {timestamp} already exists")
            return False
        except Exception as e:
            logging.error(f"Error saving weather data: {e}")
            raise
        finally:
            conn.close()
    
    def get_latest_record(self, region_code: str) -> Optional[Dict[str, Any]]:
        """Get the latest weather record for a region."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM weather_data 
                WHERE region_code = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (region_code,))
            
            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
        finally:
            conn.close()
