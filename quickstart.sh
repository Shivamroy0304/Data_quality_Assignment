#!/bin/bash
# Quick Start Script
# This script sets up the environment and runs the workflow engine

set -e

echo "================================================"
echo "Workflow Engine - Quick Start Setup"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python installation..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $python_version"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Run tests (optional)
echo "Running basic tests..."
python3 test_engine.py
echo ""

# Start server
echo "================================================"
echo "Starting Workflow Engine API Server"
echo "================================================"
echo ""
echo "Server will be available at:"
echo "  http://localhost:8000"
echo ""
echo "API Documentation:"
echo "  http://localhost:8000/docs (Swagger UI)"
echo "  http://localhost:8000/redoc (ReDoc)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 run.py
