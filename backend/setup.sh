#!/bin/bash
# LePetPal Backend Setup Script
# This script automates the initial setup process

set -e

echo "=========================================="
echo "LePetPal Backend Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env from example
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "  Please edit .env to customize your configuration"
else
    echo ""
    echo "✓ .env file already exists"
fi

# Create calibration.json from example
if [ ! -f calibration.json ]; then
    echo ""
    echo "Creating calibration.json from calibration.json.example..."
    cp calibration.json.example calibration.json
    echo "✓ calibration.json created"
    echo "  Please edit calibration.json to match your hardware setup"
else
    echo ""
    echo "✓ calibration.json already exists"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env to configure your deployment"
echo "2. Edit calibration.json to match your hardware"
echo "3. Run the server: python run_backend.py"
echo "4. Test health check: curl http://localhost:5000/health"
echo ""
echo "For development without hardware, ensure USE_MOCK_HARDWARE=true in .env"
echo ""
