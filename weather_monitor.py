#!/usr/bin/env python3
"""Weather monitoring CLI script."""

import os
import sys
import logging
import yaml
import click
from datetime import datetime, timedelta
from meteostat import Point, Hourly
from typing import Dict, Any

from database import WeatherDatabase
from export import WeatherExporter
from plotting import WeatherPlotter
from interactive import PresetManager
from web_server import WeatherWebServer


def setup_logging():
    """Setup logging configuration."""
    import os
    
    # Create logs directory if it doesn't exist
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # Use logs directory for all log files
    log_file = os.path.join(log_dir, 'weather_monitor.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def load_config(config_path: str = 'config.yaml') -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logging.error(f"Configuration file {config_path} not found")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Error parsing configuration file: {e}")
        raise


def get_weather_data(latitude: float, longitude: float, hours_back: int = 6) -> Any:
    """Fetch weather data for given coordinates."""
    try:
        point = Point(latitude, longitude)
        
        # Get data for the last specified hours
        start = datetime.now() - timedelta(hours=hours_back)
        end = datetime.now()
        
        data = Hourly(point, start, end)
        result = data.fetch()
        
        if result.empty:
            logging.warning(f"No weather data available for coordinates {latitude}, {longitude}")
            return None
        
        return result
    except Exception as e:
        logging.error(f"Error fetching weather data for {latitude}, {longitude}: {e}")
        return None


def process_region(region_code: str, region_config: Dict[str, Any], 
                  db: WeatherDatabase, hours_back: int = 6) -> int:
    """Process weather data for a single region."""
    region_name = region_config['name']
    latitude = region_config['latitude']
    longitude = region_config['longitude']
    
    logging.info(f"Processing weather data for {region_name}")
    
    # Fetch weather data
    weather_data = get_weather_data(latitude, longitude, hours_back)
    if weather_data is None or weather_data.empty:
        logging.warning(f"No weather data available for {region_name}")
        return 0
    
    saved_count = 0
    
    # Process each weather record
    for timestamp, row in weather_data.iterrows():
        # Convert pandas series to dict and add timestamp
        weather_row = row.to_dict()
        weather_row['time'] = timestamp
        
        # Save to database
        if db.save_weather_data(region_code, region_name, latitude, longitude, weather_row):
            saved_count += 1
    
    logging.info(f"Saved {saved_count} new weather records for {region_name}")
    return saved_count


@click.command()
@click.option('--config', '-c', default='config.yaml', 
              help='Path to configuration file (default: config.yaml)')
@click.option('--verbose', '-v', is_flag=True, 
              help='Enable verbose logging')
@click.option('--hours', '-h', default=6, type=int,
              help='Hours back to fetch data (default: 6)')
def fetch_weather(config: str, verbose: bool, hours: int):
    """Fetch and save weather data for configured regions."""
    # Setup logging
    setup_logging()
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logging.info("Starting weather data collection")
    
    try:
        # Load configuration
        config_data = load_config(config)
        
        # Initialize database
        db_path = config_data.get('database', {}).get('path', 'weather_data.db')
        db = WeatherDatabase(db_path)
        
        regions = config_data.get('regions', {})
        if not regions:
            logging.error("No regions configured")
            return
        
        total_saved = 0
        
        # Process each region
        for region_code, region_config in regions.items():
            try:
                saved_count = process_region(region_code, region_config, db, hours)
                total_saved += saved_count
            except Exception as e:
                logging.error(f"Error processing region {region_code}: {e}")
                continue
        
        logging.info(f"Weather data collection completed. Total new records saved: {total_saved}")
        
    except Exception as e:
        logging.error(f"Error during weather data collection: {e}")
        sys.exit(1)


@click.group()
def cli():
    """Weather monitoring CLI."""
    pass


@cli.command()
@click.argument('region_code')
@click.option('--config', '-c', default='config.yaml', 
              help='Path to configuration file (default: config.yaml)')
def latest(region_code: str, config: str):
    """Show latest weather data for a region."""
    setup_logging()
    
    try:
        config_data = load_config(config)
        db_path = config_data.get('database', {}).get('path', 'weather_data.db')
        db = WeatherDatabase(db_path)
        
        record = db.get_latest_record(region_code)
        if record:
            click.echo(f"Latest weather data for {region_code}:")
            for key, value in record.items():
                click.echo(f"  {key}: {value}")
        else:
            click.echo(f"No weather data found for region {region_code}")
    
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)


@cli.command()
@click.argument('metric', type=click.Choice(['temperature', 'humidity', 'pressure', 'wind-speed', 'precipitation', 'all']))
@click.option('--regions', '-r', required=True, help='Comma-separated list of region codes')
@click.option('--hours', '-h', type=int, help='Hours back to fetch data')
@click.option('--days', '-d', type=int, help='Days back to fetch data (alternative to hours)')
@click.option('--ascii', is_flag=True, help='Show ASCII plot in terminal')
@click.option('--save', help='Save plot to file (PNG/SVG/PDF)')
@click.option('--export-data', type=click.Choice(['csv', 'json', 'excel']), 
              help='Export data to file (CSV/JSON/Excel)')
@click.option('--width', type=int, default=800, help='Plot width in pixels (default: 800)')
@click.option('--height', type=int, default=600, help='Plot height in pixels (default: 600)')
@click.option('--config', '-c', default='config.yaml', help='Path to configuration file (default: config.yaml)')
def plot(metric: str, regions: str, hours: int, days: int, ascii: bool, save: str, export_data: str, width: int, height: int, config: str):
    """Create weather data plots and charts."""
    setup_logging()
    
    try:
        # Validate mutually exclusive options
        if hours is not None and days is not None:
            click.echo("Error: Cannot specify both --hours and --days")
            sys.exit(1)
        
        if not ascii and not save:
            click.echo("Error: Must specify either --ascii or --save")
            sys.exit(1)
        
        # Calculate hours from days if specified
        if days is not None:
            hours = days * 24
        elif hours is None:
            hours = 24  # Default to 24 hours
        
        # Load configuration
        config_data = load_config(config)
        db_path = config_data.get('database', {}).get('path', 'weather_data.db')
        
        # Initialize plotter
        plotter = WeatherPlotter(db_path, config_data)
        
        # Parse regions
        region_list = [r.strip() for r in regions.split(',')]
        
        # Validate regions
        valid_regions = plotter.validate_regions(region_list)
        if not valid_regions:
            click.echo(f"Error: No valid regions found. Available regions: {', '.join(plotter.validate_regions(plotter.get_available_regions()))}")
            sys.exit(1)
        
        # Update figure size if specified
        if width != 800 or height != 600:
            plotter.figure_size = [width / 100, height / 100]  # Convert pixels to inches
        
        # Create plots
        if ascii:
            try:
                result = plotter.plot_metric_ascii(metric, valid_regions, hours)
                click.echo(result)
            except ImportError as e:
                click.echo(f"Error: ASCII plotting not available - {e}")
                sys.exit(1)
            except Exception as e:
                click.echo(f"Error creating ASCII plot: {e}")
                sys.exit(1)
        
        if save:
            try:
                success = plotter.plot_metric_file(metric, valid_regions, hours, save)
                if success:
                    click.echo(f"Plot saved to {save}")
                else:
                    click.echo("Error: Failed to create plot file")
                    sys.exit(1)
            except ImportError as e:
                click.echo(f"Error: File plotting not available - {e}")
                sys.exit(1)
            except Exception as e:
                click.echo(f"Error creating plot file: {e}")
                sys.exit(1)
        
        # Export data if requested
        if export_data:
            if export_data not in ['csv', 'json', 'excel']:
                click.echo(f"Error: Unsupported export format '{export_data}'. Supported formats: csv, json, excel")
                return
            
            # Generate filename for export
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_filename = f"weather_data_{metric}_{regions.replace(',', '_')}_{timestamp}.{export_data}"
            
            try:
                plotter.export_chart_data(metric, valid_regions, hours, export_filename, export_data)
                click.echo(f"Data exported successfully to: {export_filename}")
            except Exception as e:
                click.echo(f"Error exporting data: {e}")
                return
    
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)


@cli.command()
@click.argument('output_file')
@click.option('--format', '-f', 'export_format', 
              type=click.Choice(['csv', 'tsv', 'json', 'xml', 'txt', 'sql']),
              default='csv', help='Export format (default: csv)')
@click.option('--region', '-r', help='Filter by region code')
@click.option('--start-date', '-s', help='Start date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)')
@click.option('--end-date', '-e', help='End date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)')
@click.option('--limit', '-l', type=int, help='Maximum number of records to export')
@click.option('--config', '-c', default='config.yaml', 
              help='Path to configuration file (default: config.yaml)')
@click.option('--pretty', is_flag=True, 
              help='Pretty format for JSON (default: enabled)')
def export(output_file: str, export_format: str, region: str, 
           start_date: str, end_date: str, limit: int, config: str, pretty: bool):
    """Export weather data to various formats."""
    setup_logging()
    
    try:
        config_data = load_config(config)
        db_path = config_data.get('database', {}).get('path', 'weather_data.db')
        
        exporter = WeatherExporter(db_path)
        
        # Get data with filters
        data = exporter.get_weather_data(
            region_code=region,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        if not data:
            click.echo("No data found matching the specified criteria")
            return
        
        # Export based on format
        success = False
        if export_format == 'csv':
            success = exporter.export_csv(output_file, data)
        elif export_format == 'tsv':
            success = exporter.export_tsv(output_file, data)
        elif export_format == 'json':
            success = exporter.export_json(output_file, data, pretty=pretty)
        elif export_format == 'xml':
            success = exporter.export_xml(output_file, data)
        elif export_format == 'txt':
            success = exporter.export_txt(output_file, data)
        elif export_format == 'sql':
            success = exporter.export_sql(output_file, data)
        
        if success:
            click.echo(f"Successfully exported {len(data)} records to {output_file}")
        else:
            click.echo("Export failed")
            
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)


def _display_full_dashboard(data: Dict[str, Dict[str, Any]]):
    """Display full dashboard with detailed information."""
    click.echo("\n" + "="*80)
    click.echo("WEATHER DASHBOARD")
    click.echo("="*80)
    
    for region, metrics in data.items():
        click.echo(f"\n📍 {region.upper()}")
        click.echo("-" * 40)
        
        if metrics.get('temperature') is not None:
            click.echo(f"🌡️  Temperature: {metrics['temperature']:.1f}°C")
        else:
            click.echo("🌡️  Temperature: N/A")
        
        if metrics.get('humidity') is not None:
            click.echo(f"💧 Humidity: {metrics['humidity']:.1f}%")
        else:
            click.echo("💧 Humidity: N/A")
        
        if metrics.get('pressure') is not None:
            click.echo(f"🌪️  Pressure: {metrics['pressure']:.1f} hPa")
        else:
            click.echo("🌪️  Pressure: N/A")
        
        if metrics.get('wind-speed') is not None:
            click.echo(f"💨 Wind Speed: {metrics['wind-speed']:.1f} km/h")
        else:
            click.echo("💨 Wind Speed: N/A")


def _display_compact_dashboard(data: Dict[str, Dict[str, Any]]):
    """Display compact dashboard in table format."""
    click.echo("\n" + "="*80)
    click.echo("WEATHER DASHBOARD (COMPACT)")
    click.echo("="*80)
    
    # Header
    header = f"{'Region':<15} {'Temp':<8} {'Humidity':<10} {'Pressure':<10} {'Wind':<8}"
    click.echo(header)
    click.echo("-" * len(header))
    
    # Data rows
    for region, metrics in data.items():
        temp = f"{metrics.get('temperature', 'N/A'):.1f}°C" if metrics.get('temperature') is not None else "N/A"
        humidity = f"{metrics.get('humidity', 'N/A'):.1f}%" if metrics.get('humidity') is not None else "N/A"
        pressure = f"{metrics.get('pressure', 'N/A'):.1f}hPa" if metrics.get('pressure') is not None else "N/A"
        wind = f"{metrics.get('wind-speed', 'N/A'):.1f}km/h" if metrics.get('wind-speed') is not None else "N/A"
        
        row = f"{region:<15} {temp:<8} {humidity:<10} {pressure:<10} {wind:<8}"
        click.echo(row)


@cli.command()
@click.option('--regions', '-r', help='Comma-separated list of region codes')
@click.option('--preset', '-p', help='Use region preset from config')
@click.option('--refresh', type=int, help='Auto-refresh interval in seconds')
@click.option('--compact', is_flag=True, help='Compact display mode')
@click.option('--config', '-c', default='config.yaml', help='Path to configuration file (default: config.yaml)')
def dashboard(regions: str, preset: str, refresh: int, compact: bool, config: str):
    """Show ASCII dashboard with multiple weather metrics."""
    setup_logging()
    
    try:
        # Load configuration
        config_data = load_config(config)
        db_path = config_data.get('database', {}).get('path', 'weather_data.db')
        
        # Initialize plotter for data access
        plotter = WeatherPlotter(db_path, config_data)
        
        # Determine regions to display
        region_list = []
        
        if preset:
            # Use preset regions
            preset_manager = PresetManager(config_data)
            if preset not in preset_manager.list_presets():
                click.echo(f"Error: Preset '{preset}' not found. Available: {', '.join(preset_manager.list_presets())}")
                sys.exit(1)
            
            available_regions = plotter.get_available_regions()
            region_list = preset_manager.validate_preset(preset, available_regions)
            
            if not region_list:
                click.echo(f"Error: No valid regions found in preset '{preset}'")
                sys.exit(1)
        
        elif regions:
            # Use specified regions
            region_list = [r.strip() for r in regions.split(',')]
            valid_regions = plotter.validate_regions(region_list)
            if not valid_regions:
                click.echo(f"Error: No valid regions found. Available: {', '.join(plotter.get_available_regions())}")
                sys.exit(1)
            region_list = valid_regions
        
        else:
            # Use all available regions (limit to first 5 for readability)
            all_regions = plotter.get_available_regions()
            region_list = all_regions[:5]
            if len(all_regions) > 5:
                click.echo(f"Note: Showing first 5 regions. Use --regions to specify specific regions.")
        
        # Create dashboard
        dashboard_data = {}
        metrics = ['temperature', 'humidity', 'pressure', 'wind-speed']
        
        for region in region_list:
            dashboard_data[region] = {}
            for metric in metrics:
                try:
                    data = plotter.get_metric_data(metric, [region], 1)  # Last hour
                    if data and region in data and data[region]:
                        latest_value = data[region][-1][1]  # Get latest value
                        dashboard_data[region][metric] = latest_value
                    else:
                        dashboard_data[region][metric] = None
                except Exception as e:
                    dashboard_data[region][metric] = None
        
        # Display dashboard
        if compact:
            _display_compact_dashboard(dashboard_data)
        else:
            _display_full_dashboard(dashboard_data)
        
        # Auto-refresh if specified
        if refresh:
            click.echo(f"\nAuto-refreshing every {refresh} seconds. Press Ctrl+C to stop.")
            try:
                import time
                while True:
                    time.sleep(refresh)
                    click.echo("\n" + "="*80)
                    if compact:
                        _display_compact_dashboard(dashboard_data)
                    else:
                        _display_full_dashboard(dashboard_data)
            except KeyboardInterrupt:
                click.echo("\nDashboard stopped.")
    
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)


@cli.command()
@click.option('--port', '-p', type=int, default=8080, help='Port to run server on (default: 8080)')
@click.option('--host', '-h', default='localhost', help='Host to bind server to (default: localhost)')
@click.option('--open-browser', '-o', is_flag=True, help='Automatically open browser')
@click.option('--daemon', '-d', is_flag=True, help='Run server in background')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--config', '-c', default='config.yaml', help='Path to configuration file (default: config.yaml)')
def serve(port: int, host: str, open_browser: bool, daemon: bool, debug: bool, config: str):
    """Start web server for weather dashboard."""
    setup_logging()
    
    try:
        # Load configuration
        config_data = load_config(config)
        db_path = config_data.get('database', {}).get('path', 'weather_data.db')
        
        # Check if database exists
        if not os.path.exists(db_path):
            click.echo(f"Error: Database file '{db_path}' not found. Run 'fetch-weather' first.")
            sys.exit(1)
        
        # Initialize web server
        server = WeatherWebServer(db_path, config_data)
        
        # Override config with command line options
        if port != 8080:
            server.default_port = port
        if host != 'localhost':
            server.default_host = host
        
        # Create Flask app
        try:
            app = server.create_app()
        except ImportError as e:
            click.echo(f"Error: {e}")
            click.echo("Please install Flask: pip install flask flask-cors")
            sys.exit(1)
        
        # Prepare server URL
        server_url = f"http://{host}:{port}"
        
        if daemon:
            # Run in daemon mode
            click.echo(f"Starting server in daemon mode on {server_url}")
            server.run_daemon(host=host, port=port)
            
            # Wait a moment for server to start
            import time
            time.sleep(1)
            
            click.echo(f"Server started in background. Access at: {server_url}")
            click.echo("Use Ctrl+C to stop the server.")
            
            try:
                # Keep main thread alive
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                click.echo("\nStopping server...")
                server.stop_server()
                click.echo("Server stopped.")
        else:
            # Run in foreground mode
            click.echo(f"Starting server on {server_url}")
            
            if open_browser:
                # Open browser after a short delay
                import threading
                import webbrowser
                
                def open_browser_delayed():
                    time.sleep(2)  # Wait for server to start
                    try:
                        webbrowser.open(server_url)
                        click.echo(f"Browser opened: {server_url}")
                    except Exception as e:
                        click.echo(f"Failed to open browser: {e}")
                
                browser_thread = threading.Thread(target=open_browser_delayed, daemon=True)
                browser_thread.start()
            
            # Start server
            try:
                server.run_server(host=host, port=port, debug=debug)
            except KeyboardInterrupt:
                click.echo("\nServer stopped by user.")
            except Exception as e:
                click.echo(f"Error starting server: {e}")
                sys.exit(1)
    
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)


# Add commands to CLI group
cli.add_command(fetch_weather)


if __name__ == '__main__':
    cli()
