#!/usr/bin/env python3
"""
Web server module.

This module provides Flask-based web server for
interactive weather data viewing and visualization.
"""

import os
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict

try:
    from flask import Flask, request, jsonify, send_from_directory
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logging.warning("Flask not available, web server disabled")


@dataclass
class WeatherDataPoint:
    """Weather data point for API responses."""
    region_code: str
    region_name: str
    timestamp: str
    temperature: Optional[float]
    humidity: Optional[float]
    pressure: Optional[float]
    wind_speed: Optional[float]
    precipitation: Optional[float]


@dataclass
class RegionInfo:
    """Region information for API responses."""
    code: str
    name: str
    latitude: float
    longitude: float
    last_update: Optional[str]
    data_points: int


@dataclass
class HealthStatus:
    """Health status for API responses."""
    status: str
    timestamp: str
    database_connected: bool
    regions_count: int
    total_records: int
    last_update: Optional[str]


class WeatherWebServer:
    """Flask-based web server for weather data API."""
    
    def __init__(self, db_path: str, config: Dict[str, Any]):
        """Initialize web server with database path and configuration."""
        self.db_path = db_path
        self.config = config
        self.web_config = config.get('web_server', {})
        self.app = None
        self.server_thread = None
        
        # Default configuration
        self.default_port = self.web_config.get('default_port', 8080)
        self.default_host = self.web_config.get('default_host', 'localhost')
        self.max_data_points = self.web_config.get('max_data_points', 1000)
        self.enable_cors = self.web_config.get('enable_cors', True)
    
    def create_app(self):
        """Create and configure Flask application."""
        if not FLASK_AVAILABLE:
            raise ImportError("Flask not available for web server")
        
        try:
            from flask import Flask
            app = Flask(__name__, 
                       template_folder=os.path.join(os.path.dirname(__file__), 'web', 'templates'),
                       static_folder=os.path.join(os.path.dirname(__file__), 'web', 'static'))
        except ImportError:
            raise ImportError("Flask not available for web server")
        
        # Configure CORS
        if self.enable_cors:
            CORS(app)
        
        # Configure logging
        app.logger.setLevel(logging.INFO)
        
        # Register API routes
        self._register_routes(app)
        
        # Register static file routes
        self._register_static_routes(app)
        
        self.app = app
        return app
    
    def _register_routes(self, app):
        """Register API routes."""
        
        @app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            try:
                health = self.get_health_status()
                return jsonify(asdict(health))
            except Exception as e:
                app.logger.error(f"Health check error: {e}")
                return jsonify({'error': 'Health check failed'}), 500
        
        @app.route('/api/regions', methods=['GET'])
        def get_regions():
            """Get list of available regions."""
            try:
                regions = self.get_regions_data()
                return jsonify(regions)
            except Exception as e:
                app.logger.error(f"Regions API error: {e}")
                return jsonify({'error': 'Failed to get regions'}), 500
        
        @app.route('/api/weather-data', methods=['GET'])
        def get_weather_data():
            """Get weather data with filtering."""
            try:
                # Get query parameters
                regions = request.args.get('regions', '').split(',') if request.args.get('regions') else []
                metric = request.args.get('metric', 'temperature')
                hours = int(request.args.get('hours', 24))
                limit = int(request.args.get('limit', self.max_data_points))
                
                # Validate parameters
                if hours <= 0 or hours > 168:  # Max 1 week
                    return jsonify({'error': 'Hours must be between 1 and 168'}), 400
                
                if limit <= 0 or limit > self.max_data_points:
                    return jsonify({'error': f'Limit must be between 1 and {self.max_data_points}'}), 400
                
                # Get data
                data = self.get_weather_data_api(regions, metric, hours, limit)
                return jsonify(data)
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            except Exception as e:
                app.logger.error(f"Weather data API error: {e}")
                return jsonify({'error': 'Failed to get weather data'}), 500
        
        @app.route('/api/stats', methods=['GET'])
        def get_stats():
            """Get statistical data."""
            try:
                regions = request.args.get('regions', '').split(',') if request.args.get('regions') else []
                metric = request.args.get('metric', 'temperature')
                hours = int(request.args.get('hours', 24))
                
                stats = self.get_stats_api(regions, metric, hours)
                return jsonify(stats)
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            except Exception as e:
                app.logger.error(f"Stats API error: {e}")
                return jsonify({'error': 'Failed to get statistics'}), 500

        @app.route('/api/export/data', methods=['GET'])
        def export_data():
            """Export data in various formats."""
            try:
                # Get query parameters
                regions = request.args.get('regions', '').split(',') if request.args.get('regions') else []
                metric = request.args.get('metric', 'temperature')
                hours = int(request.args.get('hours', 24))
                format = request.args.get('format', 'csv')
                
                # Validate parameters
                if not regions:
                    return jsonify({'error': 'Regions parameter is required'}), 400
                
                if hours <= 0 or hours > 168:
                    return jsonify({'error': 'Hours must be between 1 and 168'}), 400
                
                # Export data
                result = self.export_data_api(regions, metric, hours, format)
                
                if result['success']:
                    from flask import Response
                    response = Response(result['content'], content_type=result['content_type'])
                    response.headers['Content-Disposition'] = f'attachment; filename="{result["filename"]}"'
                    return response
                else:
                    return jsonify({'error': result['error']}), 500
                    
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            except Exception as e:
                app.logger.error(f"Export data API error: {e}")
                return jsonify({'error': 'Failed to export data'}), 500

        @app.route('/api/export/chart', methods=['GET'])
        def export_chart():
            """Export chart in various formats."""
            try:
                # Get query parameters
                regions = request.args.get('regions', '').split(',') if request.args.get('regions') else []
                metric = request.args.get('metric', 'temperature')
                hours = int(request.args.get('hours', 24))
                format = request.args.get('format', 'png')
                
                # Validate parameters
                if not regions:
                    return jsonify({'error': 'Regions parameter is required'}), 400
                
                if hours <= 0 or hours > 168:
                    return jsonify({'error': 'Hours must be between 1 and 168'}), 400
                
                # Export chart
                result = self.export_chart_api(regions, metric, hours, format)
                
                if result['success']:
                    from flask import Response
                    response = Response(result['content'], content_type=result['content_type'])
                    response.headers['Content-Disposition'] = f'attachment; filename="{result["filename"]}"'
                    return response
                else:
                    return jsonify({'error': result['error']}), 500
                    
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            except Exception as e:
                app.logger.error(f"Export chart API error: {e}")
                return jsonify({'error': 'Failed to export chart'}), 500

        @app.route('/api/export/report', methods=['POST'])
        def generate_report():
            """Generate PDF report."""
            try:
                # Get JSON data
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'JSON data required'}), 400
                
                regions = data.get('regions', [])
                metric = data.get('metric', 'temperature')
                hours = int(data.get('hours', 24))
                
                # Validate parameters
                if not regions:
                    return jsonify({'error': 'Regions parameter is required'}), 400
                
                if hours <= 0 or hours > 168:
                    return jsonify({'error': 'Hours must be between 1 and 168'}), 400
                
                # Generate report
                result = self.generate_report_api(regions, metric, hours)
                
                if result['success']:
                    from flask import Response
                    response = Response(result['content'], content_type=result['content_type'])
                    response.headers['Content-Disposition'] = f'attachment; filename="{result["filename"]}"'
                    return response
                else:
                    return jsonify({'error': result['error']}), 500
                    
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            except Exception as e:
                app.logger.error(f"Generate report API error: {e}")
                return jsonify({'error': 'Failed to generate report'}), 500
    
    def _register_static_routes(self, app):
        """Register static file routes."""
        
        @app.route('/')
        def index():
            """Serve main page."""
            return jsonify({
                'message': 'Weather Monitor API',
                'version': '1.0.0',
                'endpoints': [
                    '/api/health',
                    '/api/regions',
                    '/api/weather-data',
                    '/api/stats',
                    '/api/export/data',
                    '/api/export/chart',
                    '/api/export/report'
                ],
                'ui': '/dashboard'
            })
        
        @app.route('/dashboard')
        def dashboard():
            """Serve dashboard page."""
            try:
                from flask import render_template
                return render_template('dashboard.html')
            except ImportError:
                return jsonify({'error': 'Templates not available'}), 500
        
        @app.route('/static/<path:filename>')
        def static_files(filename):
            """Serve static files."""
            static_dir = os.path.join(os.path.dirname(__file__), 'web', 'static')
            if os.path.exists(static_dir):
                return send_from_directory(static_dir, filename)
            return jsonify({'error': 'Static files not found'}), 404
    
    def get_regions_data(self) -> List[Dict[str, Any]]:
        """Get formatted regions data."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Get regions with latest data
            cursor.execute('''
                SELECT 
                    region_code,
                    region_name,
                    latitude,
                    longitude,
                    MAX(timestamp) as last_update,
                    COUNT(*) as data_points
                FROM weather_data 
                GROUP BY region_code, region_name, latitude, longitude
                ORDER BY region_code
            ''')
            
            regions = []
            for row in cursor.fetchall():
                region = RegionInfo(
                    code=row[0],
                    name=row[1],
                    latitude=row[2],
                    longitude=row[3],
                    last_update=row[4],
                    data_points=row[5]
                )
                regions.append(asdict(region))
            
            return regions
        finally:
            conn.close()
    
    def get_weather_data_api(self, regions: List[str], metric: str, hours: int, limit: int) -> Dict[str, Any]:
        """Get weather data for API response."""
        # Validate metric
        valid_metrics = ['temperature', 'humidity', 'pressure', 'wind_speed', 'precipitation']
        if metric not in valid_metrics:
            raise ValueError(f"Invalid metric. Must be one of: {', '.join(valid_metrics)}")
        
        # Get data from database
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Build query
            query = f'''
                SELECT 
                    region_code, region_name, timestamp,
                    temperature, humidity, pressure, wind_speed, precipitation
                FROM weather_data 
                WHERE timestamp >= ?
            '''
            params = [cutoff_time.isoformat()]
            
            if regions:
                placeholders = ','.join(['?' for _ in regions])
                query += f' AND region_code IN ({placeholders})'
                params.extend(regions)
            
            query += f' ORDER BY timestamp DESC LIMIT {limit}'
            
            cursor.execute(query, params)
            
            data_points = []
            for row in cursor.fetchall():
                point = WeatherDataPoint(
                    region_code=row[0],
                    region_name=row[1],
                    timestamp=row[2],
                    temperature=row[3],
                    humidity=row[4],
                    pressure=row[5],
                    wind_speed=row[6],
                    precipitation=row[7]
                )
                data_points.append(asdict(point))
            
            return {
                'metric': metric,
                'hours': hours,
                'regions': regions if regions else 'all',
                'data_points': data_points,
                'count': len(data_points)
            }
        finally:
            conn.close()
    
    def get_stats_api(self, regions: List[str], metric: str, hours: int) -> Dict[str, Any]:
        """Get statistical data for API response."""
        # Validate metric
        valid_metrics = ['temperature', 'humidity', 'pressure', 'wind_speed', 'precipitation']
        if metric not in valid_metrics:
            raise ValueError(f"Invalid metric. Must be one of: {', '.join(valid_metrics)}")
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Build query
            query = f'''
                SELECT 
                    region_code,
                    MIN({metric}) as min_val,
                    MAX({metric}) as max_val,
                    AVG({metric}) as avg_val,
                    COUNT({metric}) as count
                FROM weather_data 
                WHERE timestamp >= ? AND {metric} IS NOT NULL
            '''
            params = [cutoff_time.isoformat()]
            
            if regions:
                placeholders = ','.join(['?' for _ in regions])
                query += f' AND region_code IN ({placeholders})'
                params.extend(regions)
            
            query += f' GROUP BY region_code ORDER BY region_code'
            
            cursor.execute(query, params)
            
            stats = []
            for row in cursor.fetchall():
                region_stats = {
                    'region_code': row[0],
                    'min': round(row[1], 2) if row[1] is not None else None,
                    'max': round(row[2], 2) if row[2] is not None else None,
                    'avg': round(row[3], 2) if row[3] is not None else None,
                    'count': row[4]
                }
                stats.append(region_stats)
            
            return {
                'metric': metric,
                'hours': hours,
                'regions': regions if regions else 'all',
                'statistics': stats
            }
        finally:
            conn.close()
    
    def get_health_status(self) -> HealthStatus:
        """Get system health status."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Get basic stats
            cursor.execute('SELECT COUNT(*) FROM weather_data')
            total_records = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT region_code) FROM weather_data')
            regions_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT MAX(timestamp) FROM weather_data')
            last_update = cursor.fetchone()[0]
            
            return HealthStatus(
                status='healthy',
                timestamp=datetime.now().isoformat(),
                database_connected=True,
                regions_count=regions_count,
                total_records=total_records,
                last_update=last_update
            )
        except Exception as e:
            return HealthStatus(
                status='unhealthy',
                timestamp=datetime.now().isoformat(),
                database_connected=False,
                regions_count=0,
                total_records=0,
                last_update=None
            )
        finally:
            conn.close()

    def export_data_api(self, regions: List[str], metric: str, hours: int, format: str = 'csv') -> Dict[str, Any]:
        """Export data in various formats via API."""
        from plotting import WeatherPlotter
        
        # Validate format
        supported_formats = ['csv', 'json', 'excel']
        if format not in supported_formats:
            raise ValueError(f"Unsupported format: {format}. Supported: {supported_formats}")
        
        # Validate metric
        valid_metrics = ['temperature', 'humidity', 'pressure', 'wind_speed', 'precipitation']
        if metric not in valid_metrics:
            raise ValueError(f"Invalid metric. Must be one of: {', '.join(valid_metrics)}")
        
        # Create plotter instance
        plotter = WeatherPlotter(self.db_path, self.config)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"weather_data_{metric}_{format}_{timestamp}.{format}"
        
        # Export data
        success = plotter.export_chart_data(metric, regions, hours, filename, format)
        
        if success:
            # Read the exported file
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clean up temporary file
            import os
            os.remove(filename)
            
            return {
                'success': True,
                'format': format,
                'filename': filename,
                'content': content,
                'content_type': self._get_content_type(format)
            }
        else:
            return {
                'success': False,
                'error': 'Failed to export data'
            }

    def export_chart_api(self, regions: List[str], metric: str, hours: int, format: str = 'png') -> Dict[str, Any]:
        """Export chart in various formats via API."""
        from plotting import WeatherPlotter
        
        # Validate format
        supported_formats = ['png', 'svg', 'pdf']
        if format not in supported_formats:
            raise ValueError(f"Unsupported format: {format}. Supported: {supported_formats}")
        
        # Validate metric
        valid_metrics = ['temperature', 'humidity', 'pressure', 'wind_speed', 'precipitation']
        if metric not in valid_metrics:
            raise ValueError(f"Invalid metric. Must be one of: {', '.join(valid_metrics)}")
        
        # Create plotter instance
        plotter = WeatherPlotter(self.db_path, self.config)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"weather_chart_{metric}_{format}_{timestamp}.{format}"
        
        # Export chart
        success = plotter.plot_metric_file(metric, regions, hours, filename)
        
        if success:
            # Read the exported file
            with open(filename, 'rb') as f:
                content = f.read()
            
            # Clean up temporary file
            import os
            os.remove(filename)
            
            return {
                'success': True,
                'format': format,
                'filename': filename,
                'content': content,
                'content_type': self._get_content_type(format)
            }
        else:
            return {
                'success': False,
                'error': 'Failed to export chart'
            }

    def generate_report_api(self, regions: List[str], metric: str, hours: int) -> Dict[str, Any]:
        """Generate PDF report via API."""
        from plotting import WeatherPlotter
        
        # Validate metric
        valid_metrics = ['temperature', 'humidity', 'pressure', 'wind_speed', 'precipitation']
        if metric not in valid_metrics:
            raise ValueError(f"Invalid metric. Must be one of: {', '.join(valid_metrics)}")
        
        # Create plotter instance
        plotter = WeatherPlotter(self.db_path, self.config)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"weather_report_{metric}_{timestamp}.pdf"
        
        # Generate report
        success = plotter.generate_report(metric, regions, hours, filename)
        
        if success:
            # Read the exported file
            with open(filename, 'rb') as f:
                content = f.read()
            
            # Clean up temporary file
            import os
            os.remove(filename)
            
            return {
                'success': True,
                'format': 'pdf',
                'filename': filename,
                'content': content,
                'content_type': 'application/pdf'
            }
        else:
            return {
                'success': False,
                'error': 'Failed to generate report'
            }

    def _get_content_type(self, format: str) -> str:
        """Get content type for export format."""
        content_types = {
            'csv': 'text/csv',
            'json': 'application/json',
            'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'png': 'image/png',
            'svg': 'image/svg+xml',
            'pdf': 'application/pdf'
        }
        return content_types.get(format, 'application/octet-stream')

    def run_server(self, host: str = None, port: int = None, debug: bool = False):
        """Run the web server."""
        if not self.app:
            self.create_app()
        
        host = host or self.default_host
        port = port or self.default_port
        
        self.app.run(host=host, port=port, debug=debug)
    
    def run_daemon(self, host: str = None, port: int = None):
        """Run server in daemon mode."""
        import threading
        
        def run():
            self.run_server(host, port, debug=False)
        
        self.server_thread = threading.Thread(target=run, daemon=True)
        self.server_thread.start()
    
    def stop_server(self):
        """Stop the server (if running in daemon mode)."""
        if self.server_thread and self.server_thread.is_alive():
            # Note: Flask doesn't have a built-in stop method
            # This would need to be implemented with a proper WSGI server
            logging.info("Server stop requested (not implemented for Flask development server)")


def main():
    """Main function for web server module."""
    print("Weather Web Server Module")
    
    if FLASK_AVAILABLE:
        print("Flask available - web server supported")
    else:
        print("Flask not available - web server disabled")


if __name__ == "__main__":
    main()

