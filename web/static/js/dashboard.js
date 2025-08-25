/**
 * Dashboard Module for Weather Monitor
 * Main logic for the weather dashboard interface
 */

// Global utilities (using existing APIUtils from api.js)

// ChartUtils is available from charts.js

class WeatherDashboard {
    constructor() {
        this.currentRegions = [];
        this.currentMetric = 'temperature';
        this.currentHours = 24;
        this.currentLimit = 100;
        this.isLoading = false;
        this.autoRefresh = false;
        this.autoRefreshInterval = null;
        
        // Initialize dashboard
        this.init();
    }

    /**
     * Initialize the dashboard
     */
    async init() {
        try {
            console.log('Initializing dashboard...');
            
            // Load initial data
            await this.loadSystemStatus();
            console.log('System status loaded');
            
            await this.loadRegions();
            console.log('Regions loaded');
            
            // Set up event listeners
            this.setupEventListeners();
            console.log('Event listeners set up');
            
            // Load initial chart data
            await this.loadChartData();
            console.log('Dashboard initialization completed');
            
        } catch (error) {
            console.error('Dashboard initialization failed:', error);
            this.showError('Failed to initialize dashboard');
        }
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Metric selection
        const metricSelect = document.getElementById('metric-select');
        if (metricSelect) {
            metricSelect.addEventListener('change', (e) => {
                this.currentMetric = e.target.value;
                this.loadChartData();
            });
        }

        // Hours selection
        const hoursSelect = document.getElementById('hours-select');
        if (hoursSelect) {
            hoursSelect.addEventListener('change', (e) => {
                this.currentHours = parseInt(e.target.value);
                this.loadChartData();
            });
        }

        // Auto refresh toggle
        const autoRefreshToggle = document.getElementById('auto-refresh-toggle');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                this.autoRefresh = e.target.checked;
                this.toggleAutoRefresh();
            });
        }
    }

    /**
     * Generate stable color for a region based on its index in the regions array
     */
    getRegionColor(regionCode) {
        // Find index of region in current regions array
        const regionIndex = this.currentRegions.indexOf(regionCode);
        
        if (regionIndex === -1) {
            // If region not found, add it to the array
            this.currentRegions.push(regionCode);
            return this.getRegionColor(regionCode); // Recursive call with new index
        }
        
        // Use golden angle to generate distinct colors
        const goldenAngle = 137.508; // Degrees for maximum color separation
        const hue = (regionIndex * goldenAngle) % 360;
        
        return `hsl(${hue}, 70%, 60%)`;
    }
    
    /**
     * Load system status
     */
    async loadSystemStatus() {
        try {
            const response = await fetch('/api/health');
            const health = await response.json();
            
            if (APIUtils.validateResponse(health)) {
                this.updateSystemStatus(health);
            } else {
                this.showError('Failed to load system status');
            }
        } catch (error) {
            console.error('Error loading system status:', error);
            this.showError('Failed to load system status');
        }
    }

    /**
     * Update system status display
     */
    updateSystemStatus(health) {
        const dbStatus = document.getElementById('db-status');
        const regionsCount = document.getElementById('regions-count');
        const recordsCount = document.getElementById('records-count');
        const lastUpdateTime = document.getElementById('last-update-time');
        
        if (dbStatus) {
            dbStatus.innerHTML = health.database_connected ? 
                '<i class="fas fa-check-circle"></i> Connected' : 
                '<i class="fas fa-times-circle"></i> Disconnected';
            dbStatus.className = health.database_connected ? 'text-success' : 'text-danger';
        }
        
        if (regionsCount) {
            regionsCount.textContent = health.regions_count || 0;
        }
        
        if (recordsCount) {
            recordsCount.textContent = health.total_records || 0;
        }
        
        if (lastUpdateTime) {
            lastUpdateTime.textContent = APIUtils.formatTimestamp(health.last_update);
        }
    }

    /**
     * Load regions
     */
    async loadRegions() {
        try {
            const response = await fetch('/api/regions');
            const regions = await response.json();
            
            if (APIUtils.validateResponse(regions)) {
                this.populateRegionSelector(regions);
                console.log('Regions loaded:', regions.length);
            } else {
                this.showError('Failed to load regions');
            }
        } catch (error) {
            console.error('Error loading regions:', error);
            this.showError('Failed to load regions');
        }
    }

    /**
     * Populate region selector
     */
    populateRegionSelector(regions) {
        const regionList = document.getElementById('region-list');
        if (!regionList) {
            console.error('Region list container not found');
            return;
        }
        
        console.log('Populating region selector with', regions.length, 'regions');
        regionList.innerHTML = '';
        
        if (regions.length === 0) {
            regionList.innerHTML = '<div class="text-muted">No regions available</div>';
            return;
        }
        
        regions.forEach(region => {
            const div = document.createElement('div');
            div.className = 'form-check mb-2';
            div.innerHTML = `
                <input class="form-check-input" type="checkbox" value="${region.code}" id="region-${region.code}">
                <label class="form-check-label" for="region-${region.code}">
                    <strong>${region.name}</strong>
                </label>
            `;
            regionList.appendChild(div);
            
            // Add event listener
            const checkbox = div.querySelector('input');
            checkbox.addEventListener('change', (e) => {
                if (e.target.checked) {
                    if (!this.currentRegions.includes(region.code)) {
                        this.currentRegions.push(region.code);
                    }
                } else {
                    this.currentRegions = this.currentRegions.filter(r => r !== region.code);
                }
                console.log('Selected regions:', this.currentRegions);
                this.loadChartData();
            });
        });
        
        console.log('Region selector populated successfully');
    }

    /**
     * Load chart data
     */
    async loadChartData() {
        if (this.currentRegions.length === 0) {
            this.showMessage('Please select at least one region');
            return;
        }
        
        this.showLoading(true);
        this.hideError();
        
        try {
            const params = new URLSearchParams({
                regions: this.currentRegions.join(','),
                metric: this.currentMetric,
                hours: this.currentHours,
                limit: this.currentLimit
            });
            
            const response = await fetch(`/api/weather-data?${params}`);
            const weatherData = await response.json();
            
            if (APIUtils.validateResponse(weatherData)) {
                this.updateChart(weatherData);
                this.updateStats(weatherData);
            } else {
                this.showError('Failed to load weather data');
            }
        } catch (error) {
            console.error('Error loading chart data:', error);
            this.showError('Failed to load weather data');
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * Update chart
     */
    updateChart(weatherData) {
        const chartContainer = document.getElementById('chart-container');
        if (!chartContainer) return;
        
        // Simple chart display using Plotly
        if (typeof Plotly !== 'undefined') {
            const traces = [];
            const regions = {};
            
            // Group data by region
            weatherData.data_points.forEach(point => {
                if (!regions[point.region_code]) {
                    regions[point.region_code] = {
                        x: [],
                        y: [],
                        name: point.region_name
                    };
                }
                regions[point.region_code].x.push(point.timestamp);
                regions[point.region_code].y.push(point[this.currentMetric]);
            });
            
            // Update current regions array to maintain order
            this.currentRegions = Object.keys(regions);
            
            // Create traces for each region
            Object.keys(regions).forEach(regionCode => {
                const region = regions[regionCode];
                const color = this.getRegionColor(regionCode);
                traces.push({
                    x: region.x,
                    y: region.y,
                    name: region.name,
                    type: 'scatter',
                    mode: 'lines+markers',
                    line: { color: color },
                    marker: { color: color }
                });
            });
            
            const layout = {
                title: `${APIUtils.getMetricDisplayName(this.currentMetric)} - Last ${this.currentHours} hours`,
                xaxis: { title: 'Time' },
                yaxis: { title: APIUtils.getMetricDisplayName(this.currentMetric) },
                height: 500
            };
            
            Plotly.newPlot('chart-container', traces, layout);
        } else {
            // Fallback to simple text display
            chartContainer.innerHTML = `
                <div class="alert alert-info">
                    <h5>Weather Data</h5>
                    <p>Metric: ${APIUtils.getMetricDisplayName(this.currentMetric)}</p>
                    <p>Regions: ${this.currentRegions.join(', ')}</p>
                    <p>Data points: ${weatherData.data_points.length}</p>
                </div>
            `;
        }
    }

    /**
     * Update statistics
     */
    updateStats(weatherData) {
        const statsContainer = document.getElementById('stats-container');
        if (!statsContainer) return;
        
        const stats = APIUtils.calculateStats(weatherData.data_points, this.currentMetric);
        
        statsContainer.innerHTML = `
            <div class="row">
                <div class="col-4">
                    <div class="text-center">
                        <div class="h4 text-primary">${APIUtils.formatMetricValue(stats.min, this.currentMetric)}</div>
                        <small class="text-muted">Min</small>
                    </div>
                </div>
                <div class="col-4">
                    <div class="text-center">
                        <div class="h4 text-success">${APIUtils.formatMetricValue(stats.avg, this.currentMetric)}</div>
                        <small class="text-muted">Average</small>
                    </div>
                </div>
                <div class="col-4">
                    <div class="text-center">
                        <div class="h4 text-warning">${APIUtils.formatMetricValue(stats.max, this.currentMetric)}</div>
                        <small class="text-muted">Max</small>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Show loading indicator
     */
    showLoading(show) {
        const loadingIndicator = document.getElementById('loading-indicator');
        const chartContainer = document.getElementById('chart-container');
        
        if (loadingIndicator) {
            loadingIndicator.style.display = show ? 'block' : 'none';
        }
        
        // Add loading class to chart container to prevent layout shift
        if (chartContainer) {
            if (show) {
                chartContainer.classList.add('loading');
            } else {
                chartContainer.classList.remove('loading');
            }
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        const errorMessage = document.getElementById('error-message');
        const errorText = document.getElementById('error-text');
        
        if (errorMessage && errorText) {
            errorText.textContent = message;
            errorMessage.style.display = 'block';
        }
    }

    /**
     * Hide error message
     */
    hideError() {
        const errorMessage = document.getElementById('error-message');
        if (errorMessage) {
            errorMessage.style.display = 'none';
        }
    }

    /**
     * Show message
     */
    showMessage(message) {
        const chartContainer = document.getElementById('chart-container');
        if (chartContainer) {
            chartContainer.innerHTML = `
                <div class="alert alert-info text-center">
                    <i class="fas fa-info-circle me-2"></i>
                    ${message}
                </div>
            `;
        }
    }

    /**
     * Toggle auto refresh
     */
    toggleAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
        
        if (this.autoRefresh) {
            this.autoRefreshInterval = setInterval(() => {
                this.loadChartData();
            }, 30000); // Refresh every 30 seconds
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new WeatherDashboard();
});

