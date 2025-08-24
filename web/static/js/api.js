/**
 * API Module for Weather Monitor Dashboard
 * Handles all API communication with the backend
 */

class WeatherAPI {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
        this.endpoints = {
            health: '/api/health',
            regions: '/api/regions',
            weatherData: '/api/weather-data',
            stats: '/api/stats'
        };
    }

    /**
     * Make a generic API request
     * @param {string} endpoint - API endpoint
     * @param {Object} params - Query parameters
     * @returns {Promise} - API response
     */
    async request(endpoint, params = {}) {
        try {
            const url = new URL(this.baseURL + endpoint, window.location.origin);
            
            // Add query parameters
            Object.keys(params).forEach(key => {
                if (params[key] !== null && params[key] !== undefined) {
                    url.searchParams.append(key, params[key]);
                }
            });

            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    /**
     * Get system health status
     * @returns {Promise<Object>} - Health status data
     */
    async getHealthStatus() {
        return this.request(this.endpoints.health);
    }

    /**
     * Get list of available regions
     * @returns {Promise<Array>} - List of regions
     */
    async getRegions() {
        return this.request(this.endpoints.regions);
    }

    /**
     * Get weather data
     * @param {Array} regions - List of region codes
     * @param {string} metric - Weather metric
     * @param {number} hours - Time range in hours
     * @param {number} limit - Maximum number of data points
     * @returns {Promise<Object>} - Weather data
     */
    async getWeatherData(regions = [], metric = 'temperature', hours = 24, limit = 1000) {
        const params = {
            metric: metric,
            hours: hours,
            limit: limit
        };

        if (regions && regions.length > 0) {
            params.regions = regions.join(',');
        }

        return this.request(this.endpoints.weatherData, params);
    }

    /**
     * Get statistical data
     * @param {Array} regions - List of region codes
     * @param {string} metric - Weather metric
     * @param {number} hours - Time range in hours
     * @returns {Promise<Object>} - Statistical data
     */
    async getStats(regions = [], metric = 'temperature', hours = 24) {
        const params = {
            metric: metric,
            hours: hours
        };

        if (regions && regions.length > 0) {
            params.regions = regions.join(',');
        }

        return this.request(this.endpoints.stats, params);
    }
}

/**
 * Utility functions for API data processing
 */
class APIUtils {
    /**
     * Format timestamp for display
     * @param {string} timestamp - ISO timestamp
     * @returns {string} - Formatted date/time
     */
    static formatTimestamp(timestamp) {
        if (!timestamp) return '-';
        
        const date = new Date(timestamp);
        return date.toLocaleString();
    }

    /**
     * Format metric value with units
     * @param {number} value - Metric value
     * @param {string} metric - Metric type
     * @returns {string} - Formatted value with units
     */
    static formatMetricValue(value, metric) {
        if (value === null || value === undefined) return 'N/A';
        
        const units = {
            temperature: '°C',
            humidity: '%',
            pressure: ' hPa',
            wind_speed: ' km/h',
            precipitation: ' mm'
        };

        const unit = units[metric] || '';
        return `${value.toFixed(1)}${unit}`;
    }

    /**
     * Get metric display name
     * @param {string} metric - Metric code
     * @returns {string} - Display name
     */
    static getMetricDisplayName(metric) {
        const names = {
            temperature: 'Temperature',
            humidity: 'Humidity',
            pressure: 'Pressure',
            wind_speed: 'Wind Speed',
            precipitation: 'Precipitation'
        };

        return names[metric] || metric;
    }

    /**
     * Get metric icon class
     * @param {string} metric - Metric code
     * @returns {string} - Font Awesome icon class
     */
    static getMetricIcon(metric) {
        const icons = {
            temperature: 'fas fa-thermometer-half',
            humidity: 'fas fa-tint',
            pressure: 'fas fa-compress-alt',
            wind_speed: 'fas fa-wind',
            precipitation: 'fas fa-cloud-rain'
        };

        return icons[metric] || 'fas fa-chart-line';
    }

    /**
     * Get metric color class
     * @param {string} metric - Metric code
     * @returns {string} - Bootstrap color class
     */
    static getMetricColor(metric) {
        const colors = {
            temperature: 'text-primary',
            humidity: 'text-info',
            pressure: 'text-warning',
            wind_speed: 'text-success',
            precipitation: 'text-secondary'
        };

        return colors[metric] || 'text-dark';
    }

    /**
     * Group data by region
     * @param {Array} dataPoints - Array of data points
     * @returns {Object} - Data grouped by region
     */
    static groupDataByRegion(dataPoints) {
        const grouped = {};
        
        dataPoints.forEach(point => {
            if (!grouped[point.region_code]) {
                grouped[point.region_code] = {
                    name: point.region_name,
                    data: []
                };
            }
            grouped[point.region_code].data.push(point);
        });

        return grouped;
    }

    /**
     * Sort data points by timestamp
     * @param {Array} dataPoints - Array of data points
     * @returns {Array} - Sorted data points
     */
    static sortDataByTimestamp(dataPoints) {
        return dataPoints.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    }

    /**
     * Calculate statistics from data points
     * @param {Array} dataPoints - Array of data points
     * @param {string} metric - Metric to calculate stats for
     * @returns {Object} - Statistics object
     */
    static calculateStats(dataPoints, metric) {
        const values = dataPoints
            .map(point => point[metric])
            .filter(value => value !== null && value !== undefined);

        if (values.length === 0) {
            return {
                min: null,
                max: null,
                avg: null,
                count: 0
            };
        }

        const min = Math.min(...values);
        const max = Math.max(...values);
        const avg = values.reduce((sum, val) => sum + val, 0) / values.length;

        return {
            min: min,
            max: max,
            avg: avg,
            count: values.length
        };
    }

    /**
     * Validate API response
     * @param {Object} response - API response
     * @returns {boolean} - True if response is valid
     */
    static validateResponse(response) {
        return response && typeof response === 'object' && !response.error;
    }

    /**
     * Handle API errors
     * @param {Error} error - Error object
     * @returns {Object} - Error information
     */
    static handleError(error) {
        console.error('API Error:', error);
        
        return {
            error: true,
            message: error.message || 'An unknown error occurred',
            timestamp: new Date().toISOString()
        };
    }
}

// Create global API instance
const weatherAPI = new WeatherAPI();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { WeatherAPI, APIUtils };
}



