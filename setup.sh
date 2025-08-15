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
pip install -e .

# Create necessary directories
echo "📁 Creating project structure..."
mkdir -p logs/loader
mkdir -p data/raw
mkdir -p data/schemas
mkdir -p data/samples

# Set permissions for executable files
chmod +x app/main.py

# Create __init__.py files for Python packages (if they don't exist)
echo "🐍 Ensuring Python package structure..."
touch app/__init__.py
touch app/workflows/__init__.py
touch src/earth/__init__.py
touch src/earth/core/__init__.py
touch src/earth/generators/__init__.py
touch src/earth/modules/__init__.py
touch tests/__init__.py

# Optional: Install development dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📚 Installing development dependencies from requirements.txt..."
    pip install -r requirements.txt
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📁 Project structure created:"
echo "   ├── app/              (Application layer)"
echo "   ├── src/earth/        (Installable package)"
echo "   ├── logs/             (Application logs)"
echo "   ├── data/             (Data and schemas)"
echo "   └── tests/            (Test suite)"
echo ""
echo "🚀 To get started:"
echo "  1. Activate the virtual environment:"
echo "     source .venv/bin/activate"
echo ""
echo "  2. Run the main application:"
echo "     python app/main.py"
echo ""
echo "  3. Or run directly:"
echo "     ./app/main.py"
echo ""
echo "📝 For development:"
echo "   • Tests: python -m pytest tests/"
echo "   • Package import: from earth.core import loader"
echo "   • Application workflow: check app/workflows/"
echo ""
echo "📚 For additional development tools, install:"
echo "     pip install -r requirements.txt"