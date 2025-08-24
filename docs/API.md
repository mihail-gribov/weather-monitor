# Weather Monitor API Documentation

## Overview

The Weather Monitor provides a RESTful API for accessing weather data and managing the system. The API is built with Flask and supports JSON responses.

## Base URL

```
http://localhost:8080/api
```

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## Response Format

All API responses are in JSON format with the following structure:

```json
{
  "status": "success|error",
  "data": {...},
  "message": "Optional message",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Endpoints

### Health Check

**GET** `/api/health`

Returns system health status and basic statistics.

**Response:**
```json
{
  "database_connected": true,
  "last_update": "2024-01-01T12:00:00",
  "regions_count": 22,
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.123456",
  "total_records": 1234
}
```

### Get Regions

**GET** `/api/regions`

Returns list of available regions with their information.

**Response:**
```json
[
  {
    "code": "moscow",
    "name": "Moscow",
    "latitude": 55.7558,
    "longitude": 37.6176,
    "latest_update": "2024-01-01T12:00:00",
    "record_count": 156
  }
]
```

### Get Weather Data

**GET** `/api/weather-data`

Returns weather data for specified parameters.

**Query Parameters:**
- `regions` (string): Comma-separated list of region codes
- `metric` (string): Weather metric (temperature, humidity, pressure, wind-speed, precipitation)
- `hours` (integer): Number of hours back to fetch (default: 24)
- `limit` (integer): Maximum number of records to return (default: 1000)

**Example Request:**
```
GET /api/weather-data?regions=moscow,spb&metric=temperature&hours=12&limit=100
```

**Response:**
```json
{
  "data_points": [
    {
      "timestamp": "2024-01-01T12:00:00",
      "moscow": 25.5,
      "spb": 22.3
    }
  ],
  "metadata": {
    "regions": ["moscow", "spb"],
    "metric": "temperature",
    "hours": 12,
    "total_points": 12
  }
}
```

### Get Statistics

**GET** `/api/stats`

Returns statistical information for weather data.

**Query Parameters:**
- `metric` (string): Weather metric (temperature, humidity, pressure, wind-speed, precipitation)
- `regions` (string): Comma-separated list of region codes
- `hours` (integer): Number of hours back to analyze (default: 24)

**Example Request:**
```
GET /api/stats?metric=temperature&regions=moscow,spb&hours=24
```

**Response:**
```json
{
  "statistics": {
    "moscow": {
      "min": 18.5,
      "max": 28.3,
      "avg": 23.4,
      "count": 24
    },
    "spb": {
      "min": 16.2,
      "max": 25.1,
      "avg": 20.8,
      "count": 24
    }
  },
  "metadata": {
    "metric": "temperature",
    "hours": 24,
    "regions": ["moscow", "spb"]
  }
}
```

### Export Data

**GET** `/api/export/data`

Exports weather data in various formats.

**Query Parameters:**
- `regions` (string): Comma-separated list of region codes
- `metric` (string): Weather metric
- `hours` (integer): Number of hours back to export
- `format` (string): Export format (csv, json, excel)

**Example Request:**
```
GET /api/export/data?regions=moscow&metric=temperature&hours=24&format=csv
```

**Response:**
Returns file download with appropriate Content-Type header.

### Export Chart

**GET** `/api/export/chart`

Exports weather chart in various formats.

**Query Parameters:**
- `regions` (string): Comma-separated list of region codes
- `metric` (string): Weather metric
- `hours` (integer): Number of hours back to chart
- `format` (string): Chart format (png, svg, pdf)

**Example Request:**
```
GET /api/export/chart?regions=moscow,spb&metric=temperature&hours=24&format=png
```

**Response:**
Returns image file download with appropriate Content-Type header.

### Generate Report

**POST** `/api/export/report`

Generates PDF report with weather data and charts.

**Request Body:**
```json
{
  "regions": ["moscow", "spb"],
  "metric": "temperature",
  "hours": 24,
  "title": "Weather Report",
  "include_charts": true,
  "include_statistics": true
}
```

**Response:**
Returns PDF file download with appropriate Content-Type header.

## Error Handling

### Error Response Format

```json
{
  "error": "Error message",
  "status": "error",
  "timestamp": "2024-01-01T12:00:00.123456"
}
```

### Common Error Codes

- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Example Error Response

```json
{
  "error": "Invalid metric. Must be one of: temperature, humidity, pressure, wind-speed, precipitation",
  "status": "error",
  "timestamp": "2024-01-01T12:00:00.123456"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. However, it's recommended to:

- Limit requests to reasonable frequency (e.g., max 100 requests per minute)
- Use appropriate caching for frequently accessed data
- Implement pagination for large datasets

## CORS Support

The API supports Cross-Origin Resource Sharing (CORS) for web applications. All endpoints are accessible from web browsers.

## Data Formats

### Timestamp Format

All timestamps are in ISO 8601 format: `YYYY-MM-DDTHH:MM:SS`

### Metric Values

- **Temperature**: Celsius (°C)
- **Humidity**: Percentage (%)
- **Pressure**: Hectopascals (hPa)
- **Wind Speed**: Meters per second (m/s)
- **Precipitation**: Millimeters (mm)

### Region Codes

Region codes are lowercase strings without spaces:
- `moscow` - Moscow
- `spb` - Saint Petersburg
- `novosibirsk` - Novosibirsk
- etc.

## Examples

### Complete Example: Get Temperature Data

```bash
curl "http://localhost:8080/api/weather-data?regions=moscow,spb&metric=temperature&hours=12&limit=50"
```

### Complete Example: Export Data

```bash
curl -o weather_data.csv "http://localhost:8080/api/export/data?regions=moscow&metric=temperature&hours=24&format=csv"
```

### Complete Example: Generate Report

```bash
curl -X POST "http://localhost:8080/api/export/report" \
  -H "Content-Type: application/json" \
  -d '{"regions":["moscow","spb"],"metric":"temperature","hours":24}' \
  -o weather_report.pdf
```

## Testing

You can test the API using:

1. **Web Browser**: Navigate to `http://localhost:8080/api/health`
2. **curl**: Use the examples above
3. **Postman**: Import the endpoints for testing
4. **JavaScript**: Use fetch() or axios for web applications

## Versioning

The current API version is v1. Future versions will be available at `/api/v2/`, etc.

## Support

For API support and questions, please refer to the main project documentation or create an issue in the project repository.


