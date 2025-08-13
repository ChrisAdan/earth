# Earth Data Generator - Makefile

.PHONY: setup install test clean run help

# Default target
help:
	@echo "🌍 Earth Data Generator - Available Commands:"
	@echo ""
	@echo "  setup     - Initial project setup (create venv, install dependencies)"
	@echo "  install   - Install/reinstall the earth package"
	@echo "  test      - Run quick functionality test"
	@echo "  run       - Run the main application"
	@echo "  clean     - Clean up generated files and databases"
	@echo "  lint      - Run code formatting and type checking"
	@echo "  help      - Show this help message"
	@echo ""

# Setup virtual environment and install dependencies
setup:
	@echo "🚀 Setting up Earth Data Generator..."
	@chmod +x setup.sh
	@./setup.sh

# Install the earth package in development mode
install:
	@echo "📦 Installing earth package..."
	@pip install -e ./src

# Run quick test
test:
	@echo "🧪 Running quick test..."
	@python test/unit_test.py

# Run main application
run:
	@echo "🌍 Starting Earth Data Generator..."
	@python app/main.py

# Clean up generated files
clean:
	@echo "🧹 Cleaning up generated files..."
	@rm -f earth.duckdb
	@rm -rf logs/
	@rm -rf src/earth.egg-info/
	@rm -rf src/build/
	@rm -rf src/dist/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "✅ Cleanup complete"

# Code formatting and type checking (requires dev dependencies)
lint:
	@echo "🔍 Running code formatting and type checking..."
	@black src/ app/ examples/ --line-length 88
	@mypy src/ --ignore-missing-imports
	@echo "✅ Linting complete"

# Generate sample data quickly (100 records)
sample:
	@echo "📊 Generating sample dataset (100 records)..."
	@python -c "import sys; sys.path.insert(0, 'src'); from earth.loader import connect_to_duckdb, operate_on_table; from earth.generators.person import generate_multiple_persons; import pandas as pd; conn = connect_to_duckdb(); persons = generate_multiple_persons(100, seed=42); df = pd.DataFrame([p.to_dict() for p in persons]); operate_on_table(conn, 'raw', 'persons', 'write', df, 'truncate'); print('✅ Sample data generated: 100 person records')"

# Show database stats
stats:
	@echo "📈 Database Statistics:"
	@python -c "import sys; sys.path.insert(0, 'src'); from earth.loader import connect_to_duckdb, operate_on_table; conn = connect_to_duckdb(); result = operate_on_table(conn, 'raw', 'persons', 'read', query='SELECT COUNT(*) as total_persons, MIN(age) as min_age, MAX(age) as max_age, AVG(age) as avg_age FROM raw.persons'); print(result.to_string(index=False)) if not result.empty else print('No data found')"