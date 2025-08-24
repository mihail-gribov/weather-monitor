/**
 * Export Module for Weather Monitor
 * Handles data and chart export functionality
 */

class ExportManager {
    constructor() {
        this.supportedDataFormats = ['csv', 'json', 'excel'];
        this.supportedChartFormats = ['png', 'svg', 'pdf'];
    }

    /**
     * Export data in various formats
     */
    async exportData(regions, metric, hours, format = 'csv') {
        if (!this.supportedDataFormats.includes(format)) {
            throw new Error(`Unsupported data format: ${format}`);
        }

        try {
            const params = new URLSearchParams({
                regions: regions.join(','),
                metric: metric,
                hours: hours,
                format: format
            });

            const response = await fetch(`/api/export/data?${params}`);
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Export failed');
            }

            // Get filename from response headers
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = `weather_data_${metric}_${format}_${new Date().toISOString().split('T')[0]}.${format}`;
            
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                if (filenameMatch) {
                    filename = filenameMatch[1];
                }
            }

            // Download file
            const blob = await response.blob();
            this.downloadFile(blob, filename);

            return { success: true, filename: filename };

        } catch (error) {
            console.error('Data export error:', error);
            throw error;
        }
    }

    /**
     * Export chart in various formats
     */
    async exportChart(regions, metric, hours, format = 'png') {
        if (!this.supportedChartFormats.includes(format)) {
            throw new Error(`Unsupported chart format: ${format}`);
        }

        try {
            const params = new URLSearchParams({
                regions: regions.join(','),
                metric: metric,
                hours: hours,
                format: format
            });

            const response = await fetch(`/api/export/chart?${params}`);
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Chart export failed');
            }

            // Get filename from response headers
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = `weather_chart_${metric}_${format}_${new Date().toISOString().split('T')[0]}.${format}`;
            
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                if (filenameMatch) {
                    filename = filenameMatch[1];
                }
            }

            // Download file
            const blob = await response.blob();
            this.downloadFile(blob, filename);

            return { success: true, filename: filename };

        } catch (error) {
            console.error('Chart export error:', error);
            throw error;
        }
    }

    /**
     * Generate PDF report
     */
    async generateReport(regions, metric, hours) {
        try {
            const response = await fetch('/api/export/report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    regions: regions,
                    metric: metric,
                    hours: hours
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Report generation failed');
            }

            // Get filename from response headers
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = `weather_report_${metric}_${new Date().toISOString().split('T')[0]}.pdf`;
            
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                if (filenameMatch) {
                    filename = filenameMatch[1];
                }
            }

            // Download file
            const blob = await response.blob();
            this.downloadFile(blob, filename);

            return { success: true, filename: filename };

        } catch (error) {
            console.error('Report generation error:', error);
            throw error;
        }
    }

    /**
     * Export chart using Plotly.js (client-side)
     */
    exportChartPlotly(chartContainerId, format = 'png') {
        if (typeof Plotly === 'undefined') {
            throw new Error('Plotly.js is not available');
        }

        if (!this.supportedChartFormats.includes(format)) {
            throw new Error(`Unsupported chart format: ${format}`);
        }

        try {
            const filename = `weather_chart_plotly_${new Date().toISOString().split('T')[0]}.${format}`;
            
            Plotly.downloadImage(chartContainerId, {
                format: format,
                filename: filename,
                height: 500,
                width: 800
            });

            return { success: true, filename: filename };

        } catch (error) {
            console.error('Plotly chart export error:', error);
            throw error;
        }
    }

    /**
     * Export data as JSON (client-side)
     */
    exportDataJSON(data, filename = null) {
        try {
            if (!filename) {
                filename = `weather_data_${new Date().toISOString().split('T')[0]}.json`;
            }

            const jsonData = JSON.stringify(data, null, 2);
            const blob = new Blob([jsonData], { type: 'application/json' });
            
            this.downloadFile(blob, filename);

            return { success: true, filename: filename };

        } catch (error) {
            console.error('JSON export error:', error);
            throw error;
        }
    }

    /**
     * Export data as CSV (client-side)
     */
    exportDataCSV(data, filename = null) {
        try {
            if (!filename) {
                filename = `weather_data_${new Date().toISOString().split('T')[0]}.csv`;
            }

            // Convert data to CSV format
            let csvContent = 'Region,Timestamp,Value\n';
            
            if (data.data_points) {
                data.data_points.forEach(point => {
                    csvContent += `${point.region_code},${point.timestamp},${point.value}\n`;
                });
            }

            const blob = new Blob([csvContent], { type: 'text/csv' });
            this.downloadFile(blob, filename);

            return { success: true, filename: filename };

        } catch (error) {
            console.error('CSV export error:', error);
            throw error;
        }
    }

    /**
     * Download file to user's device
     */
    downloadFile(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    /**
     * Get supported formats
     */
    getSupportedFormats() {
        return {
            data: this.supportedDataFormats,
            chart: this.supportedChartFormats
        };
    }

    /**
     * Validate export parameters
     */
    validateExportParams(regions, metric, hours) {
        const errors = [];

        if (!regions || regions.length === 0) {
            errors.push('At least one region must be selected');
        }

        if (!metric) {
            errors.push('Metric must be specified');
        }

        if (!hours || hours <= 0 || hours > 168) {
            errors.push('Hours must be between 1 and 168');
        }

        return {
            valid: errors.length === 0,
            errors: errors
        };
    }
}

// Utility functions for export
const ExportUtils = {
    /**
     * Format filename with timestamp
     */
    formatFilename(baseName, extension, includeTimestamp = true) {
        let filename = baseName;
        
        if (includeTimestamp) {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
            filename += `_${timestamp}`;
        }
        
        return `${filename}.${extension}`;
    },

    /**
     * Get file size in human readable format
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    /**
     * Show export progress
     */
    showExportProgress(message) {
        // Create or update progress indicator
        let progressElement = document.getElementById('export-progress');
        
        if (!progressElement) {
            progressElement = document.createElement('div');
            progressElement.id = 'export-progress';
            progressElement.className = 'export-progress';
            progressElement.innerHTML = `
                <div class="progress-content">
                    <div class="spinner-border spinner-border-sm" role="status"></div>
                    <span class="ms-2">${message}</span>
                </div>
            `;
            document.body.appendChild(progressElement);
        } else {
            progressElement.querySelector('span').textContent = message;
        }
        
        progressElement.style.display = 'block';
    },

    /**
     * Hide export progress
     */
    hideExportProgress() {
        const progressElement = document.getElementById('export-progress');
        if (progressElement) {
            progressElement.style.display = 'none';
        }
    },

    /**
     * Show export success message
     */
    showExportSuccess(filename) {
        // Create success notification
        const notification = document.createElement('div');
        notification.className = 'export-notification success';
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-check-circle text-success"></i>
                <span class="ms-2">Export successful: ${filename}</span>
                <button type="button" class="btn-close ms-2" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    },

    /**
     * Show export error message
     */
    showExportError(error) {
        // Create error notification
        const notification = document.createElement('div');
        notification.className = 'export-notification error';
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-exclamation-triangle text-danger"></i>
                <span class="ms-2">Export failed: ${error}</span>
                <button type="button" class="btn-close ms-2" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 10000);
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ExportManager, ExportUtils };
}
