#!/bin/bash
# CLI Runner Script for Persona-Driven PDF Analysis System

echo "🚀 Persona-Driven PDF Analysis System - CLI Mode"
echo "================================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed."
    exit 1
fi

# Check if offline CLI script exists
if [ ! -f "cli_offline.py" ]; then
    echo "❌ Error: cli_offline.py not found."
    exit 1
fi

# Run with provided arguments or interactively
if [ $# -eq 0 ]; then
    echo "🔧 Running in interactive mode..."
    python3 cli_offline.py
else
    echo "🔧 Running with arguments: $@"
    python3 cli_offline.py "$@"
fi