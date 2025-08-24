# Earth Data Generator - Enhanced Makefile with Nested Help System
SCRIPTS_DIR := scripts
.PHONY: setup install test clean run help workflows sample-people sample-companies sample-dataset stats
.PHONY: test-all test-core test-generators test-modules test-app test-smoke test-quick test-verbose
.PHONY: test-coverage test-report test-list test-check
.PHONY: help-setup help-test help-sample help-data help-dev help-prod help-reports help-modules

# ============================================================================
# DEFAULT HELP - DIRECTORY OVERVIEW
# ============================================================================

# Default target - show main help directory
help:
	@echo "🌍 Earth Data Generator - Command Directory"
	@echo "Author: Chris Adan"
	@echo "Github: https://github.com/ChrisAdan/earth/tree/main"
	@echo ""
	@echo "📋 COMMAND CATEGORIES - Use 'make help-[category]' for details:"
	@echo ""
	@echo "🔧 Setup & Installation:"
	@echo "   make help-setup      - Environment setup, installation, dependencies"
	@echo ""
	@echo "🧪 Testing & Development:"
	@echo "   make help-test       - Testing system (unit, integration, coverage)"
	@echo "   make help-dev        - Development workflows and tools"
	@echo ""
	@echo "🎲 Data Generation:"
	@echo "   make help-sample     - Quick sample data generation"
	@echo "   make help-data       - Database operations and statistics"
	@echo ""
	@echo "📊 Reporting & Analysis:"
	@echo "   make help-reports    - Test reporting and export options"
	@echo ""
	@echo "📦 Module Development:"
	@echo "   make help-modules    - Module creation and testing"
	@echo ""
	@echo "🚀 Production & CI/CD:"
	@echo "   make help-prod       - Production workflows and validation"
	@echo ""
	@echo "⚡ QUICK COMMANDS:"
	@echo "   make hello           - Say hi"
	@echo "   make run             - Start interactive application"
	@echo "   make workflows       - List available workflows"
	@echo "   make clean           - Clean up generated files"
	@echo ""
	@echo "💡 TIP: Run 'make help-[category]' to see detailed commands for each area"

hello:
	@echo "Hello, world! 🌍"

# ============================================================================
# SETUP & INSTALLATION HELP
# ============================================================================

help-setup:
	@echo "🔧 Setup & Installation Commands"
	@echo "================================"
	@echo ""
	@echo "Initial Setup:"
	@echo "   make setup           - Complete project setup (venv + dependencies)"
	@echo "   make install         - Install/reinstall earth package in dev mode"
	@echo ""
	@echo "Development Dependencies:"
	@echo "   make lint            - Install and run code formatting + type checking"
	@echo ""
	@echo "Environment Management:"
	@echo "   make clean           - Clean up generated files and databases"
	@echo ""
	@echo "Prerequisites:"
	@echo "   • Python 3.8+ required"
	@echo "   • pip package manager"
	@echo "   • Virtual environment recommended"
	@echo ""
	@echo "Quick Start:"
	@echo "   make setup && make install && make test-smoke"

# ============================================================================
# TESTING HELP
# ============================================================================

help-test:
	@echo "🧪 Testing System Commands"
	@echo "==========================="
	@echo ""
	@echo "🎯 Test Categories:"
	@echo "   make test-core       - Core functionality (database, utilities)"
	@echo "   make test-generators - Data generators (person, company, career)"
	@echo "   make test-modules    - Optional modules (companies, campaigns, automotive)"
	@echo "   make test-app        - Application layer (workflows, orchestration)"
	@echo ""
	@echo "⚡ Execution Modes:"
	@echo "   make test            - Complete test suite (default: test-all)"
	@echo "   make test-all        - Run comprehensive test suite"
	@echo "   make test-quick      - Essential tests only (core + generators)"
	@echo "   make test-smoke      - Quick smoke test for basic validation"
	@echo "   make test-verbose    - All tests with detailed output"
	@echo ""
	@echo "📊 Coverage & Analysis:"
	@echo "   make test-coverage   - Run tests with HTML coverage report"
	@echo "   make test-report     - Generate detailed test summary"
	@echo ""
	@echo "🔍 Test Management:"
	@echo "   make test-list       - List all available test modules"
	@echo "   make test-check      - Verify test environment setup"
	@echo ""
	@echo "Development Cycles:"
	@echo "   make dev-test        - Install + quick tests (fast cycle)"
	@echo "   make dev-full        - Install + lint + all tests (thorough)"
	@echo "   make pre-commit      - Quick validation before commit"
	@echo ""
	@echo "💡 Coverage reports saved to: htmlcov/"

# ============================================================================
# SAMPLE DATA HELP
# ============================================================================

help-sample:
	@echo "🎲 Sample Data Generation Commands"
	@echo "=================================="
	@echo ""
	@echo "🚀 Quick Samples (for testing):"
	@echo "   make sample-people       - Generate 100 person records"
	@echo "   make sample-companies    - Generate 20 company records"
	@echo "   make sample-dataset      - Complete mini dataset (template-based)"
	@echo ""
	@echo "🎯 Dataset Generation Options:"
	@echo "   make sample-dataset-template  - Generate from 'small_demo' template"
	@echo "   make sample-dataset-custom    - Custom sized dataset (150 people, 15 companies)"
	@echo "   make sample-dataset-memory    - Quick in-memory generation (no database)"
	@echo "   make sample-dataset-extended  - Extended dataset with validation"
	@echo ""
	@echo "📈 Available Templates:"
	@echo "   • small_demo    - 50 people, 10 companies"
	@echo "   • medium_dev    - 500 people, 50 companies"
	@echo "   • large_production - 5000 people, 200 companies"
	@echo ""
	@echo "⚙️  Configuration:"
	@echo "   • All samples use seed=42 for reproducible results"
	@echo "   • Data stored in earth.duckdb by default"
	@echo "   • Batch processing optimized for performance"
	@echo ""
	@echo "💡 Use 'make workflows' to see all available data generation workflows"

# ============================================================================
# DATABASE & DATA HELP
# ============================================================================

help-data:
	@echo "📊 Database Operations & Statistics"
	@echo "==================================="
	@echo ""
	@echo "📈 Statistics & Analysis:"
	@echo "   make stats           - Show database statistics for all tables"
	@echo "   make validate        - Validate data quality across all tables"
	@echo "   make benchmark       - Performance benchmark of workflows"
	@echo ""
	@echo "🔍 Data Inspection:"
	@echo "   • People Table: Age ranges, income statistics, job titles"
	@echo "   • Companies Table: Employee counts, industry distribution"
	@echo ""
	@echo "🗄️  Database Management:"
	@echo "   • Default database: earth.duckdb"
	@echo "   • Schema: raw (persons, companies tables)"
	@echo "   • Connection: DuckDB embedded database"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "   make clean           - Remove database and generated files"
	@echo ""
	@echo "💡 Database files are automatically created when first running data generation"

# ============================================================================
# DEVELOPMENT HELP
# ============================================================================

help-dev:
	@echo "⚙️  Development Tools & Workflows"
	@echo "================================="
	@echo ""
	@echo "🔄 Development Cycles:"
	@echo "   make dev-test        - Fast cycle: install + essential tests"
	@echo "   make dev-full        - Full cycle: install + lint + all tests"
	@echo "   make pre-commit      - Pre-commit validation: lint + smoke test"
	@echo ""
	@echo "🔍 Code Quality:"
	@echo "   make lint            - Code formatting (black) + type checking (mypy)"
	@echo ""
	@echo "🎯 Application Testing:"
	@echo "   make run             - Start interactive Earth application"
	@echo "   make workflows       - List available data generation workflows"
	@echo ""
	@echo "📦 Package Management:"
	@echo "   make install         - Reinstall earth package in dev mode"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "   make clean           - Clean generated files and caches"
	@echo ""
	@echo "Configuration Files:"
	@echo "   • setup.py           - Package configuration"
	@echo "   • setup.sh           - Environment setup script"
	@echo "   • Makefile           - Build and development commands"

# ============================================================================
# PRODUCTION & CI/CD HELP
# ============================================================================

help-prod:
	@echo "🚀 Production & CI/CD Commands"
	@echo "==============================="
	@echo ""
	@echo "🏭 Production Workflows:"
	@echo "   make prod-dataset    - Generate production-scale dataset"
	@echo "                         (⚠️  Large dataset: 10k people, 500 companies)"
	@echo ""
	@echo "✅ Validation & Quality:"
	@echo "   make validate        - Data quality validation across all tables"
	@echo "   make benchmark       - Workflow performance benchmarking"
	@echo ""
	@echo "🤖 CI/CD Integration:"
	@echo "   make ci-test         - Comprehensive testing for CI pipelines"
	@echo "   make cd-validate     - Validation for CD deployment"
	@echo ""
	@echo "📊 Performance Metrics:"
	@echo "   • Record generation rates"
	@echo "   • Memory usage validation"
	@echo "   • Database integrity checks"
	@echo ""
	@echo "⚠️  Production Notes:"
	@echo "   • Production dataset generation may take several minutes"
	@echo "   • Requires confirmation before execution"
	@echo "   • Uses optimized batch sizes for performance"

# ============================================================================
# REPORTS HELP
# ============================================================================

help-reports:
	@echo "📊 Test Reporting & Export System"
	@echo "=================================="
	@echo ""
	@echo "📄 Report Generation:"
	@echo "   make test-report         - Generate console test summary"
	@echo "   make test-report-export  - Run tests + export HTML report"
	@echo "   make test-full-report    - Complete test cycle with HTML export"
	@echo ""
	@echo "📤 Export Formats:"
	@echo "   make test-export-html      - Professional HTML report"
	@echo "   make test-export-json      - JSON report (CI/CD integration)"
	@echo "   make test-export-markdown  - Markdown report (documentation)"
	@echo "   make test-export-all       - Export all formats"
	@echo ""
	@echo "📁 Report Management:"
	@echo "   make test-reports-latest   - Show latest exported reports"
	@echo "   make test-report-open      - Open latest HTML report in browser"
	@echo "   make clean-test-reports    - Clean all exported reports"
	@echo ""
	@echo "📂 Export Location:"
	@echo "   • Reports saved to: logs/test/reports/"
	@echo "   • Latest reports: logs/test/reports/latest/"
	@echo ""
	@echo "🎯 Usage Examples:"
	@echo "   make test-export-html && make test-report-open"
	@echo "   make test-full-report    # Complete test + HTML export"

# ============================================================================
# MODULES HELP
# ============================================================================

help-modules:
	@echo "📦 Module Development System"
	@echo "============================="
	@echo ""
	@echo "🏗️  Module Creation:"
	@echo "   make create-module-tests - Create test structure for new module"
	@echo "                             (Interactive: prompts for module name)"
	@echo ""
	@echo "🧪 Module Testing:"
	@echo "   make test-modules        - Test all optional modules"
	@echo "   make test-module         - Test specific module (interactive)"
	@echo ""
	@echo "📁 Module Structure:"
	@echo "   src/earth/modules/your_module/        # Module source code"
	@echo "   tests/modules/test_your_module/       # Module tests"
	@echo "   ├── __init__.py                       # Test initialization"
	@echo "   ├── test_core.py                      # Core functionality"
	@echo "   ├── test_generation.py                # Data generation"
	@echo "   └── test_integration.py               # Integration tests"
	@echo ""
	@echo "🎯 Current Modules:"
	@echo "   • companies     - Company data and operations"
	@echo "   • campaigns     - Marketing campaign generation"
	@echo "   • automotive    - Vehicle and automotive data"
	@echo ""
	@echo "💡 Module Development Workflow:"
	@echo "   1. Create module code in src/earth/modules/"
	@echo "   2. Run 'make create-module-tests' for test structure"
	@echo "   3. Add tests and run 'make test-module'"

# ============================================================================
# SETUP & INSTALLATION
# ============================================================================

# Setup virtual environment and install dependencies
setup:
	@chmod +x setup.sh
	@./setup.sh

# Install the earth package in development mode
install:
	@echo "📦 Installing earth package..."
	@pip install -e .

# ============================================================================
# TESTING SYSTEM
# ============================================================================

# Run comprehensive test suite (default)
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

# Run tests with coverage reporting
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
# DEVELOPMENT WORKFLOWS
# ============================================================================

# Run main application
run:
	@echo "🌍 Starting Earth Data Generator..."
	@python app/main.py

# List available workflows
workflows:
	@echo "📋 Available Earth Workflows:"
	@cd $(PWD) && python $(SCRIPTS_DIR)/main/workflows.py

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
# SAMPLE DATA GENERATION
# ============================================================================

# Generate sample people data (100 records)
sample-people:
	@echo "👥 Generating sample people dataset (100 records)..."
	@python $(SCRIPTS_DIR)/data/sample.py --type people --count 100 -v

# Generate sample companies data (20 records)
sample-companies:
	@echo "🏢 Generating sample companies dataset (20 records)..."
	@python $(SCRIPTS_DIR)/data/sample.py --type companies --count 20 -v

# Generate complete sample dataset using template
sample-dataset:
	@echo "🌍 Generating sample dataset from template..."
	@python $(SCRIPTS_DIR)/data/sample.py --type dataset --count 20 -v


# Alternative: Generate from template 
sample-dataset-template:
	@echo "🌍 Generating sample dataset from template..."
	@python -c "import sys; sys.path.extend(['src', 'app']); \
	from workflows import create_dataset_workflow, WorkflowConfig; \
	from earth.core.loader import DatabaseConfig; \
	config = WorkflowConfig(batch_size=25, seed=42, write_mode='truncate'); \
	workflow = create_dataset_workflow('small_demo', config=config, db_config=DatabaseConfig.for_dev()); \
	result = workflow.execute(); \
	summary = workflow.get_execution_summary(); \
	print(f'✅ Generated template dataset: {summary[\"execution_summary\"][\"total_records_generated\"]} total records in {summary[\"execution_summary\"][\"overall_duration\"]:.1f}s')"

# Generate custom dataset with specific counts
sample-dataset-custom:
	@echo "🌍 Generating custom dataset..."
	@python -c "import sys; sys.path.extend(['src', 'app']); \
	from workflows import create_dataset_workflow, WorkflowConfig; \
	from earth.core.loader import DatabaseConfig; \
	config = WorkflowConfig(batch_size=50, seed=42, write_mode='truncate'); \
	workflow = create_dataset_workflow(companies=15, people=150, config=config, db_config=DatabaseConfig.for_dev()); \
	result = workflow.execute(); \
	summary = workflow.get_execution_summary(); \
	exec_summary = summary['execution_summary']; \
	perf_metrics = summary['performance_metrics']; \
	print(f'✅ Dataset complete: {exec_summary[\"total_records_generated\"]} records'); \
	print(f'   • Duration: {exec_summary[\"overall_duration\"]:.1f}s'); \
	print(f'   • Rate: {perf_metrics[\"average_records_per_second\"]:.0f} records/sec'); \
	print(f'   • Workflows: {perf_metrics[\"workflows_completed\"]} completed')"

# Quick in-memory dataset generation (no database)
sample-dataset-memory:
	@echo "🧠 Generating in-memory dataset..."
	@python -c "import sys; sys.path.extend(['src', 'app']); \
	from workflows import quick_generate_full_dataset; \
	import json; \
	result = quick_generate_full_dataset(companies=5, people=25, seed=42); \
	total_records = sum(len(records) for records in result.values()); \
	print(f'✅ Generated in-memory dataset: {total_records} total records'); \
	for entity_type, records in result.items(): \
		print(f'   • {entity_type}: {len(records)} records'); \
	print('📋 Sample company:', json.dumps(result['company'][0], indent=2, default=str) if result['company'] else 'None')"

# Extended dataset with validation
sample-dataset-extended:
	@echo "🌍 Generating extended dataset with validation..."
	@python -c "import sys; sys.path.extend(['src', 'app']); \
	from workflows import WorkflowConfig, DatasetSpec, create_dataset_workflow; \
	from workflows.config import validate_full_dataset_ratios; \
	from earth.core.loader import DatabaseConfig; \
	import time; \
	start = time.time(); \
	companies, people = 20, 200; \
	warnings = validate_full_dataset_ratios({'companies': companies, 'people': people}); \
	if warnings: [print(f'⚠️  {w}') for w in warnings]; \
	config = WorkflowConfig(batch_size=50, seed=42, write_mode='truncate'); \
	workflow = create_dataset_workflow(companies=companies, people=people, config=config, db_config=DatabaseConfig.for_dev()); \
	result = workflow.execute(); \
	summary = workflow.get_execution_summary(); \
	exec_sum = summary['execution_summary']; \
	steps = summary['workflow_steps']; \
	print(f'\\n✅ Extended dataset complete in {time.time()-start:.1f}s total'); \
	print(f'   • Records generated: {exec_sum[\"total_records_generated\"]}'); \
	print(f'   • Parallel efficiency: {exec_sum[\"parallel_efficiency\"]:.2f}x'); \
	print('\\n📊 Workflow breakdown:'); \
	[print(f'   • {step[\"workflow_name\"]}: {step.get(\"records_generated\", 0)} records in {step[\"duration\"]:.1f}s') for step in steps if step['status'] == 'completed']"

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

# Show database statistics for all tables
stats:
	@echo "📈 Database Statistics:"
	@cd $(PWD) && python $(SCRIPTS_DIR)/data/stats.py


# ============================================================================
# PRODUCTION WORKFLOWS
# ============================================================================

# Production-ready dataset generation
prod-dataset:
	@echo "🚀 Generating production-scale dataset..."
	@echo "⚠️  This will generate a large dataset and may take several minutes"
	@read -p "Continue? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@python -c "import sys; sys.path.extend(['src', 'app']); from workflows import create_dataset_workflow, WorkflowConfig; from earth.core.loader import DatabaseConfig; config = WorkflowConfig(batch_size=1000, seed=42, write_mode='truncate'); workflow = create_dataset_workflow(people=10000, companies=500, config=config, db_config=DatabaseConfig.for_dev()); result = workflow.execute(); summary = workflow.get_execution_summary(); exec_summary = summary['execution_summary']; print(f'✅ Generated production dataset: {exec_summary[\"total_records_generated\"]} total records in {exec_summary[\"overall_duration\"]:.1f}s')"

# Validate data quality across all tables
validate:
	@echo "🔍 Validating data quality..."
	@python -c "import sys; sys.path.extend(['src', 'app']); from workflows import WorkflowConfig, PeopleWorkflow, CompaniesWorkflow; from earth.core.loader import connect_to_duckdb, DatabaseConfig; import pandas as pd; config = WorkflowConfig(seed=42); db_config = DatabaseConfig.for_dev(); conn = connect_to_duckdb(); people_valid = len(conn.execute('SELECT * FROM raw.persons WHERE age < 18 OR age > 85').fetchall()) == 0; companies_valid = len(conn.execute('SELECT * FROM raw.companies WHERE employee_count <= 0').fetchall()) == 0; print('✅ Data validation passed' if people_valid and companies_valid else '❌ Data validation failed'); conn.close()"

# Show workflow execution performance
benchmark:
	@echo "⏱️  Benchmarking workflow performance..."
	@cd $(PWD) && python $(SCRIPTS_DIR)/data/benchmark.py
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
	@if [ -d "logs/test/reports/latest" ]; then \
		echo "Directory contents:"; \
		ls -la logs/test/reports/latest/; \
		echo ""; \
		echo "File types:"; \
		for file in logs/test/reports/latest/latest.*; do \
			if [ -f "$$file" ]; then \
				if [ -L "$$file" ]; then \
					echo "🔗 $$file -> $$(readlink $$file) (SYMLINK)"; \
				else \
					echo "📄 $file ($(stat -f%z $file 2>/dev/null || stat -c%s $file 2>/dev/null) bytes) (REAL FILE)"; \
				fi; \
			fi; \
		done; \
	else \
		echo "No reports found. Run 'make test-export-all' first."; \
	fi

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