/**
 * Weather Charts Module
 * Manages interactive charts using Plotly.js
 */

class WeatherChart {
    constructor(containerId, config = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.config = {
            colors: config.colors || ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'],
            height: config.height || 500,
            responsive: config.responsive !== false,
            showGrid: config.showGrid !== false,
            animationDuration: config.animationDuration || 500,
            ...config
        };
        
        this.currentData = null;
        this.currentLayout = null;
        this.isLoading = false;
        this.regionColors = {}; // Cache for region colors
        
        // Initialize chart
        this.init();
    }

    /**
     * Initialize the chart
     */
    async init() {
        if (!this.container) {
            console.error(`Chart container with id '${this.containerId}' not found`);
            return;
        }

        // Check if Plotly is available
        if (typeof Plotly === 'undefined') {
            this.showError('Plotly.js library is not loaded');
            return;
        }

        // Load region colors synchronously
        await this.loadRegionColors();

        // Create initial empty chart
        this.createEmptyChart();
    }

    /**
     * Create empty chart with placeholder
     */
    createEmptyChart() {
        const layout = this.getDefaultLayout();
        
        Plotly.newPlot(this.containerId, [], layout, {
            responsive: this.config.responsive,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            displaylogo: false
        });
    }

    /**
     * Get default chart layout
     */
    getDefaultLayout() {
        return {
            title: {
                text: 'Weather Data',
                font: { size: 18 }
            },
            xaxis: {
                title: 'Time',
                showgrid: this.config.showGrid,
                gridcolor: '#f0f0f0'
            },
            yaxis: {
                title: 'Value',
                showgrid: this.config.showGrid,
                gridcolor: '#f0f0f0'
            },
            margin: { l: 60, r: 40, t: 60, b: 60 },
            height: this.config.height,
            hovermode: 'closest',
            legend: {
                orientation: 'h',
                y: -0.2
            },
            showlegend: true
        };
    }

    /**
     * Update chart with new data
     */
    updateChart(weatherData, metric = 'temperature') {
        if (!weatherData || !weatherData.data_points || weatherData.data_points.length === 0) {
            this.showNoDataMessage();
            return;
        }

        this.setLoading(true);

        try {
            // Process data for Plotly
            const traces = this.createTraces(weatherData.data_points, metric);
            const layout = this.createLayout(metric, weatherData.time_range);
            
            // Update chart with animation
            Plotly.react(this.containerId, traces, layout, {
                responsive: this.config.responsive,
                displayModeBar: true,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
                displaylogo: false
            });

            this.currentData = weatherData;
            this.currentLayout = layout;

            // Add event listeners
            this.addEventListeners();

        } catch (error) {
            console.error('Error updating chart:', error);
            this.showError('Failed to update chart');
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Create traces for each region
     */
    createTraces(dataPoints, metric) {
        const traces = [];
        const groupedData = this.groupDataByRegion(dataPoints);
        const metricDisplayName = this.getMetricDisplayName(metric);
        const metricUnit = this.getMetricUnit(metric);

        Object.keys(groupedData).forEach((regionCode, index) => {
            const regionData = groupedData[regionCode];
            const color = this.getRegionColor(regionCode);

            const trace = {
                x: regionData.timestamps,
                y: regionData.values,
                type: 'scatter',
                mode: 'lines+markers',
                name: regionData.name,
                line: {
                    color: color,
                    width: 2
                },
                marker: {
                    color: color,
                    size: 4
                },
                hovertemplate: 
                    `<b>${regionData.name}</b><br>` +
                    `Time: %{x}<br>` +
                    `${metricDisplayName}: %{y}${metricUnit}<br>` +
                    `<extra></extra>`,
                showlegend: true
            };

            traces.push(trace);
        });

        return traces;
    }

    /**
     * Group data points by region
     */
    groupDataByRegion(dataPoints) {
        const grouped = {};

        dataPoints.forEach(point => {
            const regionCode = point.region_code;
            
            if (!grouped[regionCode]) {
                grouped[regionCode] = {
                    name: point.region_name,
                    timestamps: [],
                    values: []
                };
            }

            grouped[regionCode].timestamps.push(point.timestamp);
            grouped[regionCode].values.push(point[metric] || 0);
        });

        return grouped;
    }

    /**
     * Create chart layout with metric-specific settings
     */
    createLayout(metric, timeRange) {
        const metricDisplayName = this.getMetricDisplayName(metric);
        const metricUnit = this.getMetricUnit(metric);
        
        const layout = this.getDefaultLayout();
        
        layout.title.text = `${metricDisplayName} Comparison`;
        layout.yaxis.title = `${metricDisplayName} (${metricUnit})`;
        
        // Add time range info if available
        if (timeRange) {
            layout.title.text += ` - ${this.formatTimeRange(timeRange)}`;
        }

        // Metric-specific axis settings
        switch (metric) {
            case 'temperature':
                layout.yaxis.range = [-50, 50];
                break;
            case 'humidity':
                layout.yaxis.range = [0, 100];
                break;
            case 'pressure':
                layout.yaxis.range = [900, 1100];
                break;
            case 'wind_speed':
                layout.yaxis.range = [0, 50];
                break;
            case 'precipitation':
                layout.yaxis.range = [0, 100];
                break;
        }

        return layout;
    }

    /**
     * Get metric display name
     */
    getMetricDisplayName(metric) {
        const names = {
            'temperature': 'Temperature',
            'humidity': 'Humidity',
            'pressure': 'Pressure',
            'wind_speed': 'Wind Speed',
            'precipitation': 'Precipitation'
        };
        return names[metric] || metric;
    }

    /**
     * Get metric unit
     */
    getMetricUnit(metric) {
        const units = {
            'temperature': '°C',
            'humidity': '%',
            'pressure': ' hPa',
            'wind_speed': ' m/s',
            'precipitation': ' mm'
        };
        return units[metric] || '';
    }

    /**
     * Format time range for display
     */
    formatTimeRange(timeRange) {
        if (!timeRange) return '';
        
        const start = new Date(timeRange.start);
        const end = new Date(timeRange.end);
        
        const startStr = start.toLocaleDateString() + ' ' + start.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        const endStr = end.toLocaleDateString() + ' ' + end.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        return `${startStr} - ${endStr}`;
    }

    /**
     * Add event listeners for chart interactions
     */
    addEventListeners() {
        if (!this.container) return;

        // Listen for legend clicks
        this.container.on('plotly_legendclick', (data) => {
            // Prevent default legend click behavior
            return false;
        });

        // Listen for double-click to reset zoom
        this.container.on('plotly_doubleclick', () => {
            Plotly.relayout(this.containerId, {
                'xaxis.autorange': true,
                'yaxis.autorange': true
            });
        });
    }

    /**
     * Show no data message
     */
    showNoDataMessage() {
        const layout = this.getDefaultLayout();
        layout.title.text = 'No Data Available';
        
        Plotly.react(this.containerId, [], layout, {
            responsive: this.config.responsive,
            displayModeBar: false,
            displaylogo: false
        });

        // Add custom message
        this.container.innerHTML += `
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; color: #666;">
                <i class="fas fa-chart-line fa-3x mb-3"></i>
                <p>No data available for selected criteria</p>
                <p class="small">Try selecting different regions or time range</p>
            </div>
        `;
    }

    /**
     * Show error message
     */
    showError(message) {
        if (!this.container) return;

        this.container.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #dc3545;">
                <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
                <h4>Chart Error</h4>
                <p>${message}</p>
            </div>
        `;
    }

    /**
     * Set loading state
     */
    setLoading(loading) {
        this.isLoading = loading;
        
        if (loading) {
            this.container.classList.add('loading');
            this.container.style.pointerEvents = 'none';
        } else {
            this.container.classList.remove('loading');
            this.container.style.pointerEvents = 'auto';
        }
    }

    /**
     * Export chart as image
     */
    exportChart(format = 'png') {
        if (!this.currentData) {
            console.warn('No chart data to export');
            return;
        }

        const filename = `weather_chart_${new Date().toISOString().split('T')[0]}.${format}`;
        
        Plotly.downloadImage(this.containerId, {
            format: format,
            filename: filename,
            height: this.config.height,
            width: this.container.offsetWidth
        });
    }

    /**
     * Get chart data for export
     */
    getChartData() {
        return this.currentData;
    }

    /**
     * Get stable color for a region
     */
    getRegionColor(regionCode) {
        // Check cache first
        if (this.regionColors[regionCode]) {
            return this.regionColors[regionCode];
        }
        
        // Return fallback color if not in cache
        return this.config.colors[0];
    }
    
    /**
     * Load region colors from API
     */
    async loadRegionColors() {
        try {
            const response = await fetch('/api/region-colors');
            if (response.ok) {
                const data = await response.json();
                this.regionColors = data.colors || {};
            }
        } catch (error) {
            console.warn('Failed to load region colors:', error);
        }
    }
    
    /**
     * Clear chart
     */
    clearChart() {
        if (this.container) {
            Plotly.purge(this.containerId);
            this.currentData = null;
            this.currentLayout = null;
        }
    }

    /**
     * Resize chart
     */
    resize() {
        if (this.currentData && this.currentLayout) {
            Plotly.relayout(this.containerId, {
                width: this.container.offsetWidth,
                height: this.config.height
            });
        }
    }

    /**
     * Destroy chart and cleanup
     */
    destroy() {
        if (this.container) {
            Plotly.purge(this.containerId);
        }
        this.currentData = null;
        this.currentLayout = null;
    }
}

// Utility functions for chart management
const ChartUtils = {
    /**
     * Create chart configuration from config object
     */
    createConfig(config = {}) {
        return {
            colors: config.colors || ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'],
            height: config.height || 500,
            responsive: config.responsive !== false,
            showGrid: config.showGrid !== false,
            animationDuration: config.animationDuration || 500
        };
    },

    /**
     * Validate weather data structure
     */
    validateData(data) {
        return data && 
               Array.isArray(data.data_points) && 
               data.data_points.length > 0;
    },

    /**
     * Format timestamp for display
     */
    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString();
    },

    /**
     * Format metric value with unit
     */
    formatMetricValue(value, metric) {
        if (value === null || value === undefined) return 'N/A';
        
        const unit = {
            'temperature': '°C',
            'humidity': '%',
            'pressure': ' hPa',
            'wind_speed': ' m/s',
            'precipitation': ' mm'
        }[metric] || '';
        
        return `${value}${unit}`;
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { WeatherChart, ChartUtils };
}
