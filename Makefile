# Earth Data Generator - Enhanced Makefile with Workflow Support

.PHONY: setup install test clean run help workflows sample-people sample-companies sample-dataset stats

# Default target
help:
	@echo "🌍 Earth Data Generator - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  setup     - Initial project setup (create venv, install dependencies)"
	@echo "  install   - Install/reinstall the earth package"
	@echo ""
	@echo "Testing & Development:"
	@echo "  test      - Run comprehensive functionality tests"
	@echo "  lint      - Run code formatting and type checking"
	@echo ""
	@echo "Data Generation:"
	@echo "  run       - Run the main interactive application"
	@echo "  workflows - List available data generation workflows"
	@echo ""
	@echo "Quick Samples (for testing):"
	@echo "  sample-people    - Generate 100 person records"
	@echo "  sample-companies - Generate 20 company records"
	@echo "  sample-dataset   - Generate complete mini dataset (people + companies)"
	@echo ""
	@echo "Database Management:"
	@echo "  stats     - Show database statistics"
	@echo "  clean     - Clean up generated files and databases"
	@echo ""

# Setup virtual environment and install dependencies
setup:
	@echo "🚀 Setting up Earth Data Generator..."
	@chmod +x setup.sh
	@./setup.sh

# Install the earth package in development mode
install:
	@echo "📦 Installing earth package..."
	@pip install -e .

# Run comprehensive test suite
test:
	@echo "🧪 Running enhanced test suite..."
	@python tests/unit_test.py

# Run main application
run:
	@echo "🌍 Starting Earth Data Generator..."
	@python app/main.py

# List available workflows
workflows:
	@echo "📋 Available Earth Workflows:"
	@python -c "import sys; sys.path.insert(0, 'app'); from workflows import AVAILABLE_WORKFLOWS; [print(f'  • {name}: {info[\"description\"]}') for name, info in AVAILABLE_WORKFLOWS.items()]"

# Generate sample people data (100 records)
sample-people:
	@echo "👥 Generating sample people dataset (100 records)..."
	@python -c "import sys; sys.path.extend(['src', 'app']); from workflows import WorkflowConfig, PeopleWorkflow; from loader import DatabaseConfig; config = WorkflowConfig(batch_size=50, seed=42, write_mode='truncate'); workflow = PeopleWorkflow(config, DatabaseConfig.for_dev()); result = workflow.execute(100); print(f'✅ Generated {result.records_generated} person records in {result.execution_time:.1f}s')"

# Generate sample companies data (20 records)
sample-companies:
	@echo "🏢 Generating sample companies dataset (20 records)..."
	@python -c "import sys; sys.path.extend(['src', 'app']); from workflows import WorkflowConfig, CompaniesWorkflow; from loader import DatabaseConfig; config = WorkflowConfig(batch_size=10, seed=42, write_mode='truncate'); workflow = CompaniesWorkflow(config, DatabaseConfig.for_dev()); result = workflow.execute(20); print(f'✅ Generated {result.records_generated} company records in {result.execution_time:.1f}s')"

# Generate complete mini dataset
sample-dataset:
	@echo "🌍 Generating complete sample dataset..."
	@python -c "import sys; sys.path.extend(['src', 'app']); from workflows import WorkflowConfig, FullDatasetWorkflow, DatasetSpec; from loader import DatabaseConfig; config = WorkflowConfig(batch_size=25, seed=42, write_mode='truncate'); spec = DatasetSpec(people_count=100, companies_count=10); workflow = FullDatasetWorkflow(config, DatabaseConfig.for_dev(), spec); result = workflow.execute(); summary = workflow.get_execution_summary(); print(f'✅ Generated complete dataset: {summary[\"overall_stats\"][\"total_records_generated\"]} total records in {summary[\"overall_stats\"][\"total_duration\"]:.1f}s')"

# Show database statistics for all tables
stats:
	@echo "📈 Database Statistics:"
	@echo ""
	@echo "📊 People Table:"
	@python -c "import sys; sys.path.insert(0, 'src'); from loader import connect_to_duckdb, operate_on_table, DatabaseConfig; conn = connect_to_duckdb(DatabaseConfig.for_dev()); result = operate_on_table(conn, 'raw', 'persons', 'read', query='SELECT COUNT(*) as total_persons, MIN(age) as min_age, MAX(age) as max_age, AVG(age) as avg_age FROM raw.persons'); print(result.to_string(index=False)) if not result.empty else print('No person data found'); conn.close()" 2>/dev/null || echo "No person data found"
	@echo ""
	@echo "🏢 Companies Table:"
	@python -c "import sys; sys.path.insert(0, 'src'); from loader import connect_to_duckdb, operate_on_table, DatabaseConfig; conn = connect_to_duckdb(DatabaseConfig.for_dev()); result = operate_on_table(conn, 'raw', 'companies', 'read', query='SELECT COUNT(*) as total_companies, AVG(employee_count) as avg_employees, COUNT(DISTINCT industry) as unique_industries FROM raw.companies'); print(result.to_string(index=False)) if not result.empty else print('No company data found'); conn.close()" 2>/dev/null || echo "No company data found"

# Clean up generated files
clean:
	@echo "🧹 Cleaning up generated files..."
	@rm -f earth.duckdb
	@rm -rf data/
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
	@black src/ app/ tests/ --line-length 88
	@mypy src/ --ignore-missing-imports
	@echo "✅ Linting complete"

# Development workflow - quick test cycle
dev-test: install test
	@echo "🔄 Development test cycle complete"

# Production-ready dataset generation
prod-dataset:
	@echo "🚀 Generating production-scale dataset..."
	@echo "⚠️  This will generate a large dataset and may take several minutes"
	@read -p "Continue? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@python -c "import sys; sys.path.extend(['src', 'app']); from workflows import WorkflowConfig, FullDatasetWorkflow, DatasetSpec; from loader import DatabaseConfig; config = WorkflowConfig(batch_size=1000, seed=42, write_mode='truncate'); spec = DatasetSpec(people_count=10000, companies_count=500); workflow = FullDatasetWorkflow(config, DatabaseConfig.for_dev(), spec); result = workflow.execute(); summary = workflow.get_execution_summary(); print(f'✅ Generated production dataset: {summary[\"overall_stats\"][\"total_records_generated\"]} total records in {summary[\"overall_stats\"][\"total_duration\"]:.1f}s')"

# Validate data quality across all tables
validate:
	@echo "🔍 Validating data quality..."
	@python -c "import sys; sys.path.extend(['src', 'app']); from workflows import WorkflowConfig, PeopleWorkflow, CompaniesWorkflow; from loader import DatabaseConfig; import pandas as pd; config = WorkflowConfig(seed=42); db_config = DatabaseConfig.for_dev(); conn = db_config.connect_to_duckdb(); people_valid = len(conn.execute('SELECT * FROM raw.persons WHERE age < 18 OR age > 85').fetchall()) == 0; companies_valid = len(conn.execute('SELECT * FROM raw.companies WHERE employee_count <= 0').fetchall()) == 0; print('✅ Data validation passed' if people_valid and companies_valid else '❌ Data validation failed'); conn.close()"

# Show workflow execution performance
benchmark:
	@echo "⏱️  Benchmarking workflow performance..."
	@python -c "import sys, time; sys.path.extend(['src', 'app']); from workflows import WorkflowConfig, PeopleWorkflow, CompaniesWorkflow; from loader import DatabaseConfig; config = WorkflowConfig(batch_size=100, seed=42); results = []; for workflow_class, name, count in [(PeopleWorkflow, 'People', 500), (CompaniesWorkflow, 'Companies', 50)]: start = time.time(); workflow = workflow_class(config, DatabaseConfig.for_testing()); result = workflow.execute(count); duration = time.time() - start; rate = count / duration; results.append((name, count, duration, rate)); print('\\n⏱️  Workflow Performance:'); [print(f'  {name}: {count} records in {duration:.1f}s ({rate:.0f} records/sec)') for name, count, duration, rate in results]"