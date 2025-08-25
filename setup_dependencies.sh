#!/bin/bash

# Setup script for external dependencies
# This script downloads required external libraries

set -e

echo "Setting up external dependencies..."

# Create libs directory if it doesn't exist
mkdir -p web/static/js/libs

# Download Plotly.js if not exists
if [ ! -f "web/static/js/libs/plotly.min.js" ]; then
    echo "Downloading Plotly.js..."
    cd web/static/js/libs
    wget https://cdn.plot.ly/plotly-2.27.0.min.js -O plotly.min.js
    cd ../../..
    echo "Plotly.js downloaded successfully"
else
    echo "Plotly.js already exists"
fi

echo "Dependencies setup completed!"
