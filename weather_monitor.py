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


# Add commands to CLI group
cli.add_command(fetch_weather)


if __name__ == '__main__':
    cli()
