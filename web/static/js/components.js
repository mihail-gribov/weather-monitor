/**
 * UI Components Module for Weather Monitor Dashboard
 * Handles region selector and parameter panel functionality
 */

class RegionSelector {
    constructor(containerId = 'region-selector') {
        this.container = document.getElementById(containerId);
        this.regions = [];
        this.selectedRegions = new Set();
        this.filteredRegions = [];
        this.searchTerm = '';
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadRegions();
        this.loadState();
    }

    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('region-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchTerm = e.target.value.toLowerCase();
                this.filterRegions();
            });
        }

        // Clear search
        const clearSearchBtn = document.getElementById('clear-search-btn');
        if (clearSearchBtn) {
            clearSearchBtn.addEventListener('click', () => {
                searchInput.value = '';
                this.searchTerm = '';
                this.filterRegions();
            });
        }

        // Select all / deselect all
        const selectAllBtn = document.getElementById('select-all-btn');
        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', () => this.selectAll());
        }

        const deselectAllBtn = document.getElementById('deselect-all-btn');
        if (deselectAllBtn) {
            deselectAllBtn.addEventListener('click', () => this.deselectAll());
        }

        // Preset selection
        const presetSelect = document.getElementById('preset-select');
        if (presetSelect) {
            presetSelect.addEventListener('change', (e) => {
                this.loadPreset(e.target.value);
            });
        }

        // Checkbox list delegation
        const checkboxList = document.getElementById('region-checkbox-list');
        if (checkboxList) {
            checkboxList.addEventListener('change', (e) => {
                if (e.target.type === 'checkbox') {
                    this.handleRegionToggle(e.target);
                }
            });
        }

        // Selected regions list delegation
        const selectedList = document.getElementById('selected-regions-list');
        if (selectedList) {
            selectedList.addEventListener('click', (e) => {
                if (e.target.classList.contains('btn-close')) {
                    const badge = e.target.closest('.selected-region-badge');
                    const regionCode = badge.dataset.regionCode;
                    this.deselectRegion(regionCode);
                }
            });
        }
    }

    async loadRegions() {
        this.showLoading(true);
        this.hideError();

        try {
            const regions = await weatherAPI.getRegions();
            
            if (APIUtils.validateResponse(regions)) {
                this.regions = regions;
                this.filteredRegions = [...regions];
                this.renderRegions();
                this.updateCounts();
            } else {
                this.showError('Failed to load regions');
            }
        } catch (error) {
            console.error('Failed to load regions:', error);
            this.showError('Failed to load regions');
        } finally {
            this.showLoading(false);
        }
    }

    renderRegions() {
        const container = document.getElementById('region-checkbox-list');
        if (!container) return;

        container.innerHTML = '';

        if (this.filteredRegions.length === 0) {
            document.getElementById('no-results').style.display = 'block';
            return;
        }

        document.getElementById('no-results').style.display = 'none';

        this.filteredRegions.forEach(region => {
            const regionItem = this.createRegionItem(region);
            container.appendChild(regionItem);
        });
    }

    createRegionItem(region) {
        const template = document.getElementById('region-item-template');
        if (!template) return document.createElement('div');

        const clone = template.content.cloneNode(true);
        const regionItem = clone.querySelector('.region-item');
        const checkbox = clone.querySelector('input[type="checkbox"]');
        const label = clone.querySelector('label');
        const nameSpan = clone.querySelector('.region-name');
        const detailsSpan = clone.querySelector('.region-details');

        // Set data attributes
        regionItem.dataset.regionCode = region.code;
        
        // Set checkbox properties
        checkbox.id = `region-${region.code}`;
        checkbox.checked = this.selectedRegions.has(region.code);
        
        // Set label properties
        label.htmlFor = checkbox.id;
        nameSpan.textContent = region.name;
        detailsSpan.textContent = `${region.latitude.toFixed(2)}, ${region.longitude.toFixed(2)}`;

        return regionItem;
    }

    filterRegions() {
        if (!this.searchTerm) {
            this.filteredRegions = [...this.regions];
        } else {
            this.filteredRegions = this.regions.filter(region => 
                region.name.toLowerCase().includes(this.searchTerm) ||
                region.code.toLowerCase().includes(this.searchTerm)
            );
        }

        this.renderRegions();
        this.updateCounts();
    }

    handleRegionToggle(checkbox) {
        const regionCode = checkbox.closest('.region-item').dataset.regionCode;
        
        if (checkbox.checked) {
            this.selectRegion(regionCode);
        } else {
            this.deselectRegion(regionCode);
        }
    }

    selectRegion(regionCode) {
        this.selectedRegions.add(regionCode);
        this.updateSelectedSummary();
        this.updateCounts();
        this.saveState();
        this.triggerChangeEvent();
    }

    deselectRegion(regionCode) {
        this.selectedRegions.delete(regionCode);
        this.updateSelectedSummary();
        this.updateCounts();
        this.saveState();
        this.triggerChangeEvent();
    }

    selectAll() {
        this.filteredRegions.forEach(region => {
            this.selectedRegions.add(region.code);
        });
        this.renderRegions();
        this.updateSelectedSummary();
        this.updateCounts();
        this.saveState();
        this.triggerChangeEvent();
    }

    deselectAll() {
        this.selectedRegions.clear();
        this.renderRegions();
        this.updateSelectedSummary();
        this.updateCounts();
        this.saveState();
        this.triggerChangeEvent();
    }

    loadPreset(presetName) {
        if (!presetName) return;

        const presets = {
            'major-cities': ['moscow', 'spb', 'belgrade', 'minsk'],
            'moscow-region': ['moskva_station', 'ostafyevo', 'domodedovo'],
            'international': ['belgrade', 'minsk', 'prague']
        };

        const presetRegions = presets[presetName] || [];
        
        // Clear current selection
        this.selectedRegions.clear();
        
        // Add preset regions
        presetRegions.forEach(regionCode => {
            if (this.regions.some(r => r.code === regionCode)) {
                this.selectedRegions.add(regionCode);
            }
        });

        this.renderRegions();
        this.updateSelectedSummary();
        this.updateCounts();
        this.saveState();
        this.triggerChangeEvent();
    }

    updateSelectedSummary() {
        const summary = document.getElementById('selected-summary');
        const list = document.getElementById('selected-regions-list');
        
        if (!summary || !list) return;

        if (this.selectedRegions.size === 0) {
            summary.style.display = 'none';
            return;
        }

        summary.style.display = 'block';
        list.innerHTML = '';

        this.selectedRegions.forEach(regionCode => {
            const region = this.regions.find(r => r.code === regionCode);
            if (region) {
                const badge = this.createSelectedRegionBadge(region);
                list.appendChild(badge);
            }
        });
    }

    createSelectedRegionBadge(region) {
        const template = document.getElementById('selected-region-badge-template');
        if (!template) return document.createElement('span');

        const clone = template.content.cloneNode(true);
        const badge = clone.querySelector('.selected-region-badge');
        const nameSpan = clone.querySelector('.region-name');

        badge.dataset.regionCode = region.code;
        nameSpan.textContent = region.name;

        return badge;
    }

    updateCounts() {
        const selectedCount = document.getElementById('selected-count');
        const totalCount = document.getElementById('total-count');
        const filteredCount = document.getElementById('filtered-count');

        if (selectedCount) selectedCount.textContent = this.selectedRegions.size;
        if (totalCount) totalCount.textContent = this.regions.length;
        if (filteredCount) filteredCount.textContent = this.filteredRegions.length;
    }

    showLoading(show) {
        const loading = document.getElementById('regions-loading');
        if (loading) {
            loading.style.display = show ? 'block' : 'none';
        }
    }

    showError(message) {
        const error = document.getElementById('regions-error');
        const errorText = document.getElementById('regions-error-text');
        
        if (error && errorText) {
            errorText.textContent = message;
            error.style.display = 'block';
        }
    }

    hideError() {
        const error = document.getElementById('regions-error');
        if (error) {
            error.style.display = 'none';
        }
    }

    saveState() {
        const state = {
            selectedRegions: Array.from(this.selectedRegions),
            searchTerm: this.searchTerm
        };
        localStorage.setItem('regionSelectorState', JSON.stringify(state));
    }

    loadState() {
        const saved = localStorage.getItem('regionSelectorState');
        if (saved) {
            try {
                const state = JSON.parse(saved);
                this.selectedRegions = new Set(state.selectedRegions || []);
                this.searchTerm = state.searchTerm || '';
                
                // Restore search term
                const searchInput = document.getElementById('region-search');
                if (searchInput) {
                    searchInput.value = this.searchTerm;
                }
            } catch (error) {
                console.error('Failed to load region selector state:', error);
            }
        }
    }

    triggerChangeEvent() {
        const event = new CustomEvent('regionsChanged', {
            detail: {
                selectedRegions: Array.from(this.selectedRegions)
            }
        });
        document.dispatchEvent(event);
    }

    getSelectedRegions() {
        return Array.from(this.selectedRegions);
    }

    setSelectedRegions(regions) {
        this.selectedRegions = new Set(regions);
        this.renderRegions();
        this.updateSelectedSummary();
        this.updateCounts();
        this.saveState();
    }
}

class ParameterPanel {
    constructor(containerId = 'parameter-panel') {
        this.container = document.getElementById(containerId);
        this.currentMetric = 'temperature';
        this.currentTimeRange = 24;
        this.dataLimit = 1000;
        this.autoRefresh = false;
        this.refreshInterval = 30;
        this.refreshTimer = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadState();
        this.updateStatus('Ready');
    }

    setupEventListeners() {
        // Metric selection
        document.querySelectorAll('input[name="metric"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.currentMetric = e.target.value;
                this.saveState();
                this.triggerChangeEvent();
            });
        });

        // Time range selection
        document.querySelectorAll('input[name="time-range"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.currentTimeRange = e.target.value;
                this.handleTimeRangeChange();
            });
        });

        // Custom date inputs
        const dateFrom = document.getElementById('date-from');
        const dateTo = document.getElementById('date-to');
        if (dateFrom) {
            dateFrom.addEventListener('change', () => this.saveState());
        }
        if (dateTo) {
            dateTo.addEventListener('change', () => this.saveState());
        }

        // Data limit
        const dataLimit = document.getElementById('data-limit');
        if (dataLimit) {
            dataLimit.addEventListener('change', (e) => {
                this.dataLimit = parseInt(e.target.value);
                this.saveState();
                this.triggerChangeEvent();
            });
        }

        // Auto refresh
        const autoRefresh = document.getElementById('auto-refresh');
        if (autoRefresh) {
            autoRefresh.addEventListener('change', (e) => {
                this.autoRefresh = e.target.checked;
                this.handleAutoRefreshChange();
            });
        }

        const refreshSeconds = document.getElementById('refresh-seconds');
        if (refreshSeconds) {
            refreshSeconds.addEventListener('change', (e) => {
                this.refreshInterval = parseInt(e.target.value);
                this.saveState();
                if (this.autoRefresh) {
                    this.startAutoRefresh();
                }
            });
        }

        // Action buttons
        const updateBtn = document.getElementById('update-chart-btn');
        if (updateBtn) {
            updateBtn.addEventListener('click', () => {
                this.triggerUpdateEvent();
            });
        }

        const exportBtn = document.getElementById('export-data-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.triggerExportEvent();
            });
        }

        const resetBtn = document.getElementById('reset-params-btn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.resetToDefaults();
            });
        }
    }

    handleTimeRangeChange() {
        const customInputs = document.getElementById('custom-date-inputs');
        if (this.currentTimeRange === 'custom') {
            if (customInputs) customInputs.style.display = 'block';
        } else {
            if (customInputs) customInputs.style.display = 'none';
        }
        
        this.saveState();
        this.triggerChangeEvent();
    }

    handleAutoRefreshChange() {
        const refreshInterval = document.getElementById('refresh-interval');
        if (refreshInterval) {
            refreshInterval.style.display = this.autoRefresh ? 'block' : 'none';
        }

        if (this.autoRefresh) {
            this.startAutoRefresh();
        } else {
            this.stopAutoRefresh();
        }

        this.saveState();
    }

    startAutoRefresh() {
        this.stopAutoRefresh();
        this.refreshTimer = setInterval(() => {
            this.triggerUpdateEvent();
        }, this.refreshInterval * 1000);
    }

    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    resetToDefaults() {
        // Reset metric
        const tempRadio = document.getElementById('metric-temp');
        if (tempRadio) tempRadio.checked = true;
        this.currentMetric = 'temperature';

        // Reset time range
        const time24h = document.getElementById('time-24h');
        if (time24h) time24h.checked = true;
        this.currentTimeRange = 24;

        // Reset data limit
        const dataLimit = document.getElementById('data-limit');
        if (dataLimit) dataLimit.value = 1000;
        this.dataLimit = 1000;

        // Reset auto refresh
        const autoRefresh = document.getElementById('auto-refresh');
        if (autoRefresh) autoRefresh.checked = false;
        this.autoRefresh = false;

        // Hide custom date inputs
        const customInputs = document.getElementById('custom-date-inputs');
        if (customInputs) customInputs.style.display = 'none';

        // Hide refresh interval
        const refreshInterval = document.getElementById('refresh-interval');
        if (refreshInterval) refreshInterval.style.display = 'none';

        this.stopAutoRefresh();
        this.saveState();
        this.triggerChangeEvent();
        this.updateStatus('Reset to defaults');
    }

    updateStatus(message) {
        const status = document.getElementById('param-status');
        if (status) {
            status.textContent = message;
        }
    }

    updateLastUpdateTime() {
        const timeElement = document.getElementById('last-update-time');
        if (timeElement) {
            timeElement.textContent = new Date().toLocaleTimeString();
        }
    }

    saveState() {
        const state = {
            metric: this.currentMetric,
            timeRange: this.currentTimeRange,
            dataLimit: this.dataLimit,
            autoRefresh: this.autoRefresh,
            refreshInterval: this.refreshInterval,
            dateFrom: document.getElementById('date-from')?.value || '',
            dateTo: document.getElementById('date-to')?.value || ''
        };
        localStorage.setItem('parameterPanelState', JSON.stringify(state));
    }

    loadState() {
        const saved = localStorage.getItem('parameterPanelState');
        if (saved) {
            try {
                const state = JSON.parse(saved);
                
                // Restore metric
                this.currentMetric = state.metric || 'temperature';
                const metricRadio = document.querySelector(`input[name="metric"][value="${this.currentMetric}"]`);
                if (metricRadio) metricRadio.checked = true;

                // Restore time range
                this.currentTimeRange = state.timeRange || 24;
                const timeRadio = document.querySelector(`input[name="time-range"][value="${this.currentTimeRange}"]`);
                if (timeRadio) timeRadio.checked = true;

                // Restore data limit
                this.dataLimit = state.dataLimit || 1000;
                const dataLimit = document.getElementById('data-limit');
                if (dataLimit) dataLimit.value = this.dataLimit;

                // Restore auto refresh
                this.autoRefresh = state.autoRefresh || false;
                const autoRefresh = document.getElementById('auto-refresh');
                if (autoRefresh) autoRefresh.checked = this.autoRefresh;

                // Restore refresh interval
                this.refreshInterval = state.refreshInterval || 30;
                const refreshSeconds = document.getElementById('refresh-seconds');
                if (refreshSeconds) refreshSeconds.value = this.refreshInterval;

                // Restore custom dates
                const dateFrom = document.getElementById('date-from');
                const dateTo = document.getElementById('date-to');
                if (dateFrom && state.dateFrom) dateFrom.value = state.dateFrom;
                if (dateTo && state.dateTo) dateTo.value = state.dateTo;

                // Apply restored state
                this.handleTimeRangeChange();
                this.handleAutoRefreshChange();

            } catch (error) {
                console.error('Failed to load parameter panel state:', error);
            }
        }
    }

    triggerChangeEvent() {
        const event = new CustomEvent('parametersChanged', {
            detail: this.getParameters()
        });
        document.dispatchEvent(event);
    }

    triggerUpdateEvent() {
        const event = new CustomEvent('updateChart', {
            detail: this.getParameters()
        });
        document.dispatchEvent(event);
    }

    triggerExportEvent() {
        const event = new CustomEvent('exportData', {
            detail: this.getParameters()
        });
        document.dispatchEvent(event);
    }

    getParameters() {
        return {
            metric: this.currentMetric,
            timeRange: this.currentTimeRange,
            dataLimit: this.dataLimit,
            autoRefresh: this.autoRefresh,
            refreshInterval: this.refreshInterval,
            dateFrom: document.getElementById('date-from')?.value || '',
            dateTo: document.getElementById('date-to')?.value || ''
        };
    }

    setParameters(params) {
        if (params.metric) {
            this.currentMetric = params.metric;
            const metricRadio = document.querySelector(`input[name="metric"][value="${this.currentMetric}"]`);
            if (metricRadio) metricRadio.checked = true;
        }

        if (params.timeRange) {
            this.currentTimeRange = params.timeRange;
            const timeRadio = document.querySelector(`input[name="time-range"][value="${this.currentTimeRange}"]`);
            if (timeRadio) timeRadio.checked = true;
        }

        if (params.dataLimit) {
            this.dataLimit = params.dataLimit;
            const dataLimit = document.getElementById('data-limit');
            if (dataLimit) dataLimit.value = this.dataLimit;
        }

        this.handleTimeRangeChange();
        this.saveState();
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { RegionSelector, ParameterPanel };
}



