"""Export module for weather data in various formats."""

import csv
import json
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging


class WeatherExporter:
    """Weather data exporter supporting multiple formats."""
    
    def __init__(self, db_path: str):
        """Initialize exporter with database path."""
        self.db_path = db_path
    
    def get_weather_data(self, region_code: Optional[str] = None, 
                        start_date: Optional[str] = None, 
                        end_date: Optional[str] = None,
                        limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get weather data from database with optional filters."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Build query with filters
            query = "SELECT * FROM weather_data WHERE 1=1"
            params = []
            
            if region_code:
                query += " AND region_code = ?"
                params.append(region_code)
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
            
            query += " ORDER BY timestamp DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor.execute(query, params)
            
            # Get column names
            columns = [description[0] for description in cursor.description]
            
            # Convert rows to dictionaries
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
            
        finally:
            conn.close()
    
    def export_csv(self, output_file: str, data: List[Dict[str, Any]], 
                   delimiter: str = ',') -> bool:
        """Export data to CSV format."""
        try:
            if not data:
                logging.warning("No data to export")
                return False
            
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=delimiter)
                
                writer.writeheader()
                for row in data:
                    writer.writerow(row)
            
            logging.info(f"Successfully exported {len(data)} records to {output_file}")
            return True
            
        except Exception as e:
            logging.error(f"Error exporting to CSV: {e}")
            return False
    
    def export_tsv(self, output_file: str, data: List[Dict[str, Any]]) -> bool:
        """Export data to TSV format."""
        return self.export_csv(output_file, data, delimiter='\t')
    
    def export_json(self, output_file: str, data: List[Dict[str, Any]], 
                    pretty: bool = True) -> bool:
        """Export data to JSON format."""
        try:
            if not data:
                logging.warning("No data to export")
                return False
            
            with open(output_file, 'w', encoding='utf-8') as jsonfile:
                if pretty:
                    json.dump(data, jsonfile, indent=2, ensure_ascii=False, default=str)
                else:
                    json.dump(data, jsonfile, ensure_ascii=False, default=str)
            
            logging.info(f"Successfully exported {len(data)} records to {output_file}")
            return True
            
        except Exception as e:
            logging.error(f"Error exporting to JSON: {e}")
            return False
    
    def export_xml(self, output_file: str, data: List[Dict[str, Any]]) -> bool:
        """Export data to XML format."""
        try:
            if not data:
                logging.warning("No data to export")
                return False
            
            # Create root element
            root = ET.Element("weather_data")
            root.set("exported_at", datetime.now().isoformat())
            root.set("total_records", str(len(data)))
            
            # Add each record as an element
            for record in data:
                record_elem = ET.SubElement(root, "record")
                for key, value in record.items():
                    elem = ET.SubElement(record_elem, key)
                    elem.text = str(value) if value is not None else ""
            
            # Create tree and write to file
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ", level=0)
            tree.write(output_file, encoding='utf-8', xml_declaration=True)
            
            logging.info(f"Successfully exported {len(data)} records to {output_file}")
            return True
            
        except Exception as e:
            logging.error(f"Error exporting to XML: {e}")
            return False
    
    def export_txt(self, output_file: str, data: List[Dict[str, Any]], 
                   separator: str = ' | ') -> bool:
        """Export data to plain text format."""
        try:
            if not data:
                logging.warning("No data to export")
                return False
            
            with open(output_file, 'w', encoding='utf-8') as txtfile:
                # Write header
                headers = list(data[0].keys())
                txtfile.write(separator.join(headers) + '\n')
                txtfile.write('=' * len(separator.join(headers)) + '\n')
                
                # Write data rows
                for record in data:
                    values = [str(record.get(key, '')) for key in headers]
                    txtfile.write(separator.join(values) + '\n')
            
            logging.info(f"Successfully exported {len(data)} records to {output_file}")
            return True
            
        except Exception as e:
            logging.error(f"Error exporting to TXT: {e}")
            return False
    
    def export_sql(self, output_file: str, data: List[Dict[str, Any]], 
                   table_name: str = "weather_data_export") -> bool:
        """Export data to SQL INSERT statements."""
        try:
            if not data:
                logging.warning("No data to export")
                return False
            
            with open(output_file, 'w', encoding='utf-8') as sqlfile:
                # Write table creation statement
                first_record = data[0]
                columns = list(first_record.keys())
                
                sqlfile.write(f"-- Weather data export generated at {datetime.now().isoformat()}\n")
                sqlfile.write(f"-- Total records: {len(data)}\n\n")
                
                sqlfile.write(f"CREATE TABLE IF NOT EXISTS {table_name} (\n")
                column_defs = []
                for col in columns:
                    if col == 'id':
                        column_defs.append(f"  {col} INTEGER PRIMARY KEY")
                    elif col in ['latitude', 'longitude', 'temperature', 'dewpoint', 'humidity', 
                                'precipitation', 'pressure', 'wind_speed', 'wind_direction']:
                        column_defs.append(f"  {col} REAL")
                    else:
                        column_defs.append(f"  {col} TEXT")
                
                sqlfile.write(',\n'.join(column_defs))
                sqlfile.write("\n);\n\n")
                
                # Write INSERT statements
                for record in data:
                    columns_str = ', '.join(columns)
                    values = []
                    for key in columns:
                        value = record[key]
                        if value is None:
                            values.append('NULL')
                        elif isinstance(value, str):
                            # Escape single quotes
                            escaped_value = value.replace("'", "''")
                            values.append(f"'{escaped_value}'")
                        else:
                            values.append(str(value))
                    
                    values_str = ', '.join(values)
                    sqlfile.write(f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str});\n")
            
            logging.info(f"Successfully exported {len(data)} records to {output_file}")
            return True
            
        except Exception as e:
            logging.error(f"Error exporting to SQL: {e}")
            return False
