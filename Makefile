# Earth Data Generator - Enhanced Makefile with Modular Testing Support
SCRIPTS_DIR := scripts
.PHONY: setup install test clean run help workflows sample-people sample-companies sample-dataset stats
.PHONY: test-all test-core test-generators test-modules test-app test-smoke test-quick test-verbose
.PHONY: test-coverage test-report test-list test-check

# Default target
help:
	@echo "🌍 Earth Data Generator - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  setup     - Initial project setup (create venv, install dependencies)"
	@echo "  install   - Install/reinstall the earth package"
	@echo ""
	@echo "Testing & Development:"
	@echo "  test           - Run comprehensive test suite (all modules)"
	@echo "  test-core      - Run core functionality tests (database, utilities)"
	@echo "  test-generators - Run data generator tests (person, company, etc.)"
	@echo "  test-modules   - Run optional module tests (companies, campaigns, etc.)"
	@echo "  test-app       - Run application layer tests (workflows, orchestration)"
	@echo "  test-smoke     - Run quick smoke test (basic functionality)"
	@echo "  test-quick     - Run essential tests only (fast)"
	@echo "  test-verbose   - Run all tests with detailed output"
	@echo "  test-coverage  - Run tests with coverage reporting"
	@echo "  test-list      - List all available test modules"
	@echo "  test-check     - Check test environment setup"
	@echo "  lint           - Run code formatting and type checking"
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
	@chmod +x setup.sh
	@./setup.sh

# Install the earth package in development mode
install:
	@echo "📦 Installing earth package..."
	@pip install -e .

# ============================================================================
# MODULAR TESTING SYSTEM
# ============================================================================

# Run comprehensive test suite (all modules)
test: test-all

test-all:
	@echo "🧪 Running Complete Earth Test Suite..."
	@python -m tests all --verbose

# Run core functionality tests
test-core:
	@echo "🗄️  Running Core Tests (database, utilities)..."
	@python -m tests core --verbose

# Run data generator tests
test-generators:
	@echo "🎲 Running Generator Tests (person, company, career)..."
	@python -m tests generators --verbose

# Run optional module tests
test-modules:
	@echo "📦 Running Module Tests (companies, campaigns, automotive)..."
	@python -m tests modules --verbose

# Run application layer tests
test-app:
	@echo "🔄 Running Application Tests (workflows, orchestration)..."
	@python -m tests app --verbose

# Quick smoke test for basic functionality
test-smoke:
	@echo "🚀 Running Smoke Test..."
	@python -m tests --smoke

# Run essential tests only (faster execution)
test-quick:
	@echo "⚡ Running Quick Tests..."
	@python -m tests core
	@python -m tests generators

# Run all tests with detailed verbose output
test-verbose:
	@echo "📝 Running Verbose Test Suite..."
	@python -m tests all --verbose

# Run tests with coverage reporting (requires coverage package)
test-coverage:
	@echo "📊 Running Tests with Coverage..."
	@command -v coverage >/dev/null 2>&1 || { echo "Installing coverage..."; pip install coverage; }
	@coverage run -m tests all
	@coverage report --show-missing
	@coverage html
	@echo "📈 Coverage report generated in htmlcov/"

# List all available test modules
test-list:
	@echo "📋 Available Test Modules:"
	@python -m tests --list

# Check test environment setup
test-check:
	@echo "🔍 Checking Test Environment..."
	@python -m tests --check

# Generate detailed test report
test-report:
	@echo "📄 Generating Test Report..."
	@cd $(PWD) && python $(SCRIPTS_DIR)/test/report.py

# ============================================================================
# LEGACY TESTING (for backward compatibility)
# ============================================================================

# Legacy comprehensive test (now redirects to modular system)
test-legacy:
	@echo "⚠️  Using legacy test system (consider using modular tests)"
	@python tests/unit_test.py

# ============================================================================
# DEVELOPMENT WORKFLOWS
# ============================================================================

# Run main application
run:
	@echo "🌍 Starting Earth Data Generator..."
	@python app/main.py

# List available workflows
workflows:
	@echo "📋 Available Earth Workflows:"
	@python -c "import sys; sys.path.insert(0, 'app'); from workflows import AVAILABLE_WORKFLOWS; [print(f'  • {name}: {info[\"description\"]}') for name, info in AVAILABLE_WORKFLOWS.items()]"

# ============================================================================
# SAMPLE DATA GENERATION
# ============================================================================

# Generate sample people data (100 records)
sample-people:
	@echo "👥 Generating sample people dataset (100 records)..."
	@python $(SCRIPTS_DIR)/data/sample.py --type people --count 100 -v

# Generate sample companies data (20 records)
sample-companies:
	@echo "🏢 Generating sample companies dataset (20 records)..."
	@python -c "import sys; sys.path.extend(['src', 'app']); from workflows import WorkflowConfig, CompaniesWorkflow; from earth.core.loader import DatabaseConfig; config = WorkflowConfig(batch_size=10, seed=42, write_mode='truncate'); workflow = CompaniesWorkflow(config, DatabaseConfig.for_dev()); result = workflow.execute(20); print(f'✅ Generated {result.records_generated} company records in {result.execution_time:.1f}s')"

# Generate complete mini dataset
sample-dataset:
	@echo "🌍 Generating complete sample dataset..."
	@python -c "import sys; sys.path.extend(['src', 'app']); \
	from workflows import WorkflowConfig, DatasetWorkflow, DatasetSpec; \
	from earth.core.loader import DatabaseConfig; \
	config = WorkflowConfig(batch_size=25, seed=42, write_mode='truncate'); \
	spec = DatasetSpec(people_count=100, companies_count=10, workflows={'people': 100, 'companies': 5}); \
	workflow = DatasetWorkflow(config, DatabaseConfig.for_dev(), spec); \
	result = workflow.execute(); \
	summary = workflow.get_execution_summary(); \
	print(f'✅ Generated complete dataset: {summary[\"dataset_spec\"][\"total_target_records\"]} \
	total records in {summary[\"execution_summary\"][\"overall_duration\"]:.1f}s')"

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

# Show database statistics for all tables
stats:
	@echo "📈 Database Statistics:"
	@echo ""
	@echo "📊 People Table:"
	@python -c "import sys; sys.path.insert(0, 'src'); from earth.core.loader import connect_to_duckdb, operate_on_table, DatabaseConfig; conn = connect_to_duckdb(DatabaseConfig.for_dev()); result = operate_on_table(conn, 'raw', 'persons', 'read', query='SELECT COUNT(*) as total_persons, MIN(age) as min_age, MAX(age) as max_age, AVG(age) as avg_age FROM raw.persons'); print(result.to_string(index=False)) if not result.empty else print('No person data found'); conn.close()" 2>/dev/null || echo "No person data found"
	@echo ""
	@echo "🏢 Companies Table:"
	@python -c "import sys; sys.path.insert(0, 'src'); from earth.core.loader import connect_to_duckdb, operate_on_table, DatabaseConfig; conn = connect_to_duckdb(DatabaseConfig.for_dev()); result = operate_on_table(conn, 'raw', 'companies', 'read', query='SELECT COUNT(*) as total_companies, AVG(employee_count) as avg_employees, COUNT(DISTINCT industry) as unique_industries FROM raw.companies'); print(result.to_string(index=False)) if not result.empty else print('No company data found'); conn.close()" 2>/dev/null || echo "No company data found"

# ============================================================================
# MAINTENANCE
# ============================================================================

# Clean up generated files
clean:
	@echo "🧹 Cleaning up generated files..."
	@rm -f earth.duckdb
	@rm -rf data/
	@rm -rf logs/
	@rm -rf htmlcov/
	@rm -rf .coverage
	@rm -rf src/earth.egg-info/
	@rm -rf src/build/
	@rm -rf src/dist/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "✅ Cleanup complete"

# Code formatting and type checking (requires dev dependencies)
lint:
	@echo "🔍 Running code formatting and type checking..."
	@command -v black >/dev/null 2>&1 || { echo "Installing black..."; pip install black; }
	@command -v mypy >/dev/null 2>&1 || { echo "Installing mypy..."; pip install mypy; }
	@black src/ app/ tests/ scripts/ --line-length 88
	@mypy src/ --ignore-missing-imports
	@echo "✅ Linting complete"

# ============================================================================
# DEVELOPMENT CYCLES
# ============================================================================

# Development workflow - install and run essential tests
dev-test: install test-quick
	@echo "🔄 Development test cycle complete"

# Full development cycle - install, lint, and test everything
dev-full: install lint test-all
	@echo "🚀 Full development cycle complete"

# Pre-commit workflow - quick validation before commit
pre-commit: lint test-smoke
	@echo "✅ Pre-commit checks passed"

# ============================================================================
# PRODUCTION WORKFLOWS
# ============================================================================

# Production-ready dataset generation
prod-dataset:
	@echo "🚀 Generating production-scale dataset..."
	@echo "⚠️  This will generate a large dataset and may take several minutes"
	@read -p "Continue? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@python -c "import sys; sys.path.extend(['src', 'app']); from workflows import WorkflowConfig, FullDatasetWorkflow, DatasetSpec; from earth.core.loader import DatabaseConfig; config = WorkflowConfig(batch_size=1000, seed=42, write_mode='truncate'); spec = DatasetSpec(people_count=10000, companies_count=500); workflow = FullDatasetWorkflow(config, DatabaseConfig.for_dev(), spec); result = workflow.execute(); summary = workflow.get_execution_summary(); print(f'✅ Generated production dataset: {summary[\"overall_stats\"][\"total_records_generated\"]} total records in {summary[\"overall_stats\"][\"total_duration\"]:.1f}s')"

# Validate data quality across all tables
validate:
	@echo "🔍 Validating data quality..."
	@python -c "import sys; sys.path.extend(['src', 'app']); from workflows import WorkflowConfig, PeopleWorkflow, CompaniesWorkflow; from earth.core.loader import connect_to_duckdb, DatabaseConfig; import pandas as pd; config = WorkflowConfig(seed=42); db_config = DatabaseConfig.for_dev(); conn = connect_to_duckdb(); people_valid = len(conn.execute('SELECT * FROM raw.persons WHERE age < 18 OR age > 85').fetchall()) == 0; companies_valid = len(conn.execute('SELECT * FROM raw.companies WHERE employee_count <= 0').fetchall()) == 0; print('✅ Data validation passed' if people_valid and companies_valid else '❌ Data validation failed'); conn.close()"

# Show workflow execution performance
benchmark:
	@echo "⏱️  Benchmarking workflow performance..."
	@python -c "import sys, time; \
	sys.path.extend(['src', 'app']); \
	from workflows import WorkflowConfig, PeopleWorkflow, CompaniesWorkflow; \
	from earth.core.loader import DatabaseConfig; \
	config = WorkflowConfig(batch_size=100, seed=42); \
	results = []; \
	for workflow_class, name, count in [(PeopleWorkflow, 'People', 500), \
	(CompaniesWorkflow, 'Companies', 50)]: \
		start = time.time(); \
	workflow = workflow_class(config, DatabaseConfig.for_testing()); \
	result = workflow.execute(count); \
	duration = time.time() - start; rate = count / duration; \
	results.append((name, count, duration, rate)); \
	print('\\n⏱️  Workflow Performance:'); \
	[print(f'	{name}: {count} records in {duration:.1f}s ({rate:.0f} records/sec)') for name, count, duration, rate in results]"

# ============================================================================
# CI/CD SUPPORT
# ============================================================================

# CI pipeline - comprehensive testing for continuous integration
ci-test: test-check test-all test-coverage
	@echo "🤖 CI pipeline tests complete"

# CD pipeline - validation for continuous deployment
cd-validate: test-smoke validate benchmark
	@echo "🚀 CD pipeline validation complete"

# ============================================================================
# MODULE DEVELOPMENT SUPPORT
# ============================================================================

# Create new module test structure
create-module-tests:
	@read -p "Module name: " module_name; \
	mkdir -p tests/modules/test_$$module_name; \
	echo "#!/usr/bin/env python3" > tests/modules/test_$$module_name/__init__.py; \
	echo "\"\"\"Tests for $$module_name module.\"\"\"" >> tests/modules/test_$$module_name/__init__.py; \
	echo "✅ Created test structure for $$module_name module"

# Run tests for specific module
test-module:
	@read -p "Module name: " module_name; \
	if [ -d "tests/modules/test_$$module_name" ]; then \
		echo "🧪 Running tests for $$module_name module..."; \
		python -m pytest tests/modules/test_$$module_name -v; \
	else \
		echo "❌ Module tests not found: tests/modules/test_$$module_name"; \
		echo "💡 Use 'make create-module-tests' to create test structure"; \
	fi
# ============================================================================
# TEST REPORTING AND EXPORTS
# ============================================================================

# Generate detailed test report (console only)
test-report:
	@echo "📄 Generating Test Report..."
	@cd $(PWD) && python $(SCRIPTS_DIR)/test/report.py

# Export test reports in various formats
test-export-html:
	@echo "📄 Exporting HTML Test Report..."
	@cd $(PWD) && python $(SCRIPTS_DIR)/test/report.py --export html

test-export-json:
	@echo "📄 Exporting JSON Test Report..."
	@cd $(PWD) && python $(SCRIPTS_DIR)/test/report.py --export json

test-export-markdown:
	@echo "📄 Exporting Markdown Test Report..."
	@cd $(PWD) && python $(SCRIPTS_DIR)/test/report.py --export markdown

test-export-all:
	@echo "📄 Exporting All Test Report Formats..."
	@cd $(PWD) && python $(SCRIPTS_DIR)/test/report.py --export all

# Generate and export test report (HTML by default)
test-report-export: test-export-html
	@echo "✅ Test report exported to logs/test/reports/"

# Show latest test reports
test-reports-latest:
	@echo "📁 Latest test reports:"
	@ls -la logs/test/reports/latest/ 2>/dev/null || echo "No reports found. Run 'make test-export-all' first."

# Open latest HTML report in browser (macOS/Linux)
test-report-open:
	@if [ -f "logs/test/reports/latest/latest.html" ]; then \
		echo "🌐 Opening latest test report in browser..."; \
		if command -v xdg-open >/dev/null 2>&1; then \
			xdg-open logs/test/reports/latest/latest.html; \
		elif command -v open >/dev/null 2>&1; then \
			open logs/test/reports/latest/latest.html; \
		else \
			echo "📄 Report available at: $(PWD)/logs/test/reports/latest/latest.html"; \
		fi; \
	else \
		echo "❌ No HTML report found. Run 'make test-export-html' first."; \
	fi

# Clean test reports
clean-test-reports:
	@echo "🧹 Cleaning test reports..."
	@rm -rf logs/test/reports/
	@echo "✅ Test reports cleaned"

# Full test cycle with HTML export
test-full-report: test-all test-export-html
	@echo "🎉 Complete test cycle with report export finished"

# ============================================================================
# HELP AND DOCUMENTATION
# ============================================================================

# Show testing help
test-help:
	@echo "🧪 Earth Testing System Help"
	@echo "============================="
	@echo ""
	@echo "Core Test Categories:"
	@echo "  core       - Database operations, utilities, core functionality"
	@echo "  generators - Data generators (person, company, career, etc.)"
	@echo "  modules    - Optional domain modules (companies, campaigns, automotive)"
	@echo "  app        - Application layer (workflows, orchestration, main app)"
	@echo ""
	@echo "Test Execution Modes:"
	@echo "  test-all      - Run complete test suite with full coverage"
	@echo "  test-quick    - Run essential tests only (core + generators)"
	@echo "  test-smoke    - Run basic smoke test for rapid validation"
	@echo "  test-verbose  - Run with detailed output and debugging info"
	@echo ""
	@echo "Development Workflows:"
	@echo "  dev-test      - Install + quick tests (fast development cycle)"
	@echo "  dev-full      - Install + lint + all tests (thorough validation)"
	@echo "  pre-commit    - Quick validation before committing code"
	@echo ""
	@echo "Coverage and Reporting:"
	@echo "  test-coverage - Generate HTML coverage report"
	@echo "  test-report   - Generate summary test report"
	@echo "  benchmark     - Performance benchmarking"
	@echo ""

# Show module development help
module-help:
	@echo "📦 Module Development Help"
	@echo "=========================="
	@echo ""
	@echo "Creating New Modules:"
	@echo "  1. Add module code to src/earth/modules/your_module/"
	@echo "  2. Run 'make create-module-tests' to create test structure"
	@echo "  3. Add tests to tests/modules/test_your_module/"
	@echo "  4. Run 'make test-module' to test your module"
	@echo ""
	@echo "Testing Modules:"
	@echo "  make test-modules      - Test all modules"
	@echo "  make test-module       - Test specific module (interactive)"
	@echo ""
	@echo "Module Test Structure:"
	@echo "  tests/modules/test_your_module/"
	@echo "  ├── __init__.py        - Module test initialization"
	@echo "  ├── test_core.py       - Core functionality tests"
	@echo "  ├── test_generation.py - Data generation tests"
	@echo "  └── test_integration.py- Integration tests"

	# Show test reporting help
test-report-help:
	@echo "📊 Earth Test Reporting System Help"
	@echo "===================================="
	@echo ""
	@echo "Basic Reporting:"
	@echo "  test-report           - Generate console test report"
	@echo "  test-report-export    - Run tests and export HTML report"
	@echo "  test-full-report      - Complete test cycle with HTML export"
	@echo ""
	@echo "Export Formats:"
	@echo "  test-export-html      - Export professional HTML report"
	@echo "  test-export-json      - Export JSON report for CI/CD integration"
	@echo "  test-export-markdown  - Export Markdown report for documentation"
	@echo "  test-export-all       - Export all formats (HTML, JSON, Markdown)"
	@echo ""
	@echo "Report Management:"
	@echo "  test-reports-latest   - Show latest exported reports"
	@echo "  test-report-open      - Open latest HTML report in browser"
	@echo "  clean-test-reports    - Clean all exported reports"
	@echo ""
	@echo "Export Location:"
	@echo "  📁 Reports are saved to: logs/test/reports/"
	@echo "  🔗 Latest reports linked in: logs/test/reports/latest/"
	@echo ""
	@echo "Usage Examples:"
	@echo "  make test-export-html                    # Quick HTML export"
	@echo "  make test-full-report && make test-report-open  # Test + view report"
	@echo "  make test-export-all                     # Export all formats"
	@echo ""