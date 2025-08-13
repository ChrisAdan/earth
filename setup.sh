#!/bin/bash

# Earth Data Generator Setup Script
echo "🌍 Setting up Earth Data Generator..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9+ required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
echo "🔧 Upgrading pip..."
pip install --upgrade pip

# Install core dependencies
echo "📚 Installing core dependencies..."
pip install pandas>=2.0.0 duckdb>=0.9.0 faker>=20.0.0 typing-extensions>=4.0.0

# Install package in development mode
echo "🔨 Installing Earth package in development mode..."
pip install -e ./src

# Create necessary directories
echo "📁 Creating project structure..."
mkdir -p logs/loader
mkdir -p data/raw

# Set permissions
chmod +x app/main.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To get started:"
echo "  1. Activate the virtual environment:"
echo "     source earth-env/bin/activate"
echo ""
echo "  2. Run the main application:"
echo "     python app/main.py"
echo ""
echo "  3. Or run directly:"
echo "     ./app/main.py"
echo ""
echo "📚 For development dependencies (dbt, prefect), run:"
echo "     pip install -r requirements.txt"