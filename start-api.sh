#!/bin/bash
#
# Kosty API Server Startup Script
#
# This script starts the Kosty API server for AWS cost optimization and security audits.
# 
# Usage:
#   ./start-api.sh
#
# Environment Variables:
#   PORT - Port to run the server on (default: 5000)
#   HOST - Host to bind to (default: 0.0.0.0)
#   DEBUG - Enable debug mode (default: false)
#

# Change to the repository root directory
cd "$(dirname "$0")"

echo "🚀 Starting Kosty API Server..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

# Check if required packages are installed
echo "📦 Checking dependencies..."
if ! python3 -c "import flask" 2> /dev/null; then
    echo "⚠️  Flask not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the API server
echo "🌐 Starting server..."
python3 -m kosty.api
