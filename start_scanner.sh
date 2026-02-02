#!/bin/bash
# Linux/Mac Startup Script for Epstein Files GitHub Scanner
# Make executable: chmod +x start_scanner.sh

echo "========================================"
echo "EPSTEIN FILES - GITHUB SCANNER"
echo "Starting automated monitoring..."
echo "========================================"
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Run the scheduler
python3 auto_scheduler.py
