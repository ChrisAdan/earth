# Earth 🌍

A synthetic data generation platform for analytics engineering and machine learning experimentation.

## Purpose

Earth enables downstream analytics and machine learning by generating realistic, incremental synthetic datasets. Built with modern data engineering best practices, Earth provides a foundation for testing data pipelines, developing ML models, and experimenting with analytics workflows using synthetic person profiles and time-series data.

## Technology Stack

| Stage                   | Technologies                                                                                                                                                                                              |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Data Generation**     | ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Faker](https://img.shields.io/badge/Faker-FF6B6B?style=for-the-badge&logo=python&logoColor=white) |
| **Data Storage**        | ![DuckDB](https://img.shields.io/badge/DuckDB-FFF000?style=for-the-badge&logo=duckdb&logoColor=black)                                                                                                     |
| **Data Processing**     | ![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)                                                                                                     |
| **Data Transformation** | ![dbt](https://img.shields.io/badge/dbt-FF694B?style=for-the-badge&logo=dbt&logoColor=white)                                                                                                              |
| **Orchestration**       | ![Prefect](https://img.shields.io/badge/Prefect-026AA7?style=for-the-badge&logo=prefect&logoColor=white)                                                                                                  |

## Architecture

```bash
earth/
├── README.md
├── CHANGELOG.md
├── LICENSE
├── pyproject.toml                   # Build
├── .gitignore
├── Makefile
├── requirements.txt
├── setup.sh                         # Installation shell script
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── release-please.yml
│   │   └── test-publish.yml
│   └── release-please-config.json
│
├── app/                             # Application layer
│   ├── __init__.py
│   ├── main.py                      # ← Primary orchestrator
│   └── workflows/                   # Application-specific workflows
│       ├── __init__.py
│       ├── base.py                  # Base classes and patterns for scalable workflow management
│       ├── config.py                # Workflow config metadata e.g. available workflows, templates
│       ├── base.py                  # Abstract base workflow generation class
│       ├── dataset_orchestrator.py  # Coordinate workflow executions
│       └── unified_workflow.py      # Unified workflow using base generator
│
├── src/                             # Package source for PyPI
│   └── earth/                       # The installable package
│       ├── __init__.py              # Package entry point
│       ├── core/                    # Core functionality
│       │   ├── __init__.py
│       │   ├── loader.py            # DuckDB interface & CRUD
│       │   ├── utils.py             # Utilities and constants
│       │   └── database.py          # Database schema management
│       ├── generators/              # Data generators
│       │   ├── __init__.py
│       │   ├── base.py              # Base generator class
│       │   ├── factory.py           # Factory class for creating generators
│       │   ├── person.py            # Person generator
│       │   ├── company.py           # Company generator
│       │   └── career.py            # Career generator
│       └── modules/                 # Optional modules [TBD]
│           ├── __init__.py
│           ├── companies/
│           │   ├── __init__.py
│           │   ├── generator.py
│           │   ├── industries.py
│           │   └── schemas.py
│           ├── campaigns/
│           │   ├── __init__.py
│           │   ├── generator.py
│           │   ├── products.py
│           │   ├── brands.py
│           │   └── schemas.py
│           └── automotive/
│               ├── __init__.py
│               ├── generator.py
│               ├── vehicles.py
│               └── schemas.py
│
├── logs/                            # Application logs
│   └── loader/                      # Loader-specific logs
│
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── test_core/
│   │   ├── test_loader.py
│   │   └── test_utils.py
│   ├── test_generators/
│   │   ├── test_person.py
│   │   └── test_career.py
│   ├── test_modules/
│   │   ├── test_companies/
│   │   ├── test_campaigns/
│   │   └── test_automotive/
│   └── test_app/                    # Test the application layer
│       ├── test_main.py
│       └── test_workflows.py
│
├── docs/                            # Documentation
│   ├── index.md
│   ├── installation.md
│   ├── application-usage.md         # How to use app/main.py
│   ├── package-usage.md             # How to use as pip package
│   ├── modules/
│   └── examples/
│       ├── generate_150k_people.py
│       ├── package_usage.py
│       └── application_usage.py
│
└── data/                           # Optional: Sample data or schemas
    ├── schemas/
    │   ├── person.sql
    │   ├── companies.sql
    │   └── campaigns.sql
    └── samples/
        └── sample_output.parquet
```

## How to Use Locally

### Prerequisites

- Python 3.9+
- pip or poetry

### Installation [WIP]

```bash
# Clone repository
git clone https://github.com/ChrisAdan/earth
cd earth

# Install package in development mode
pip install -e ./src

# Install dependencies
pip install pandas duckdb faker dbt-duckdb prefect
```

### Quick Start

```bash
# Generate synthetic person profiles
python app/main.py

# Follow prompts to:
# - Specify number of records to generate
# - Choose append vs. overwrite existing data
```

### Database Schema [WIP]

The `earth.duckdb` database will be created automatically with the following structure:

- `raw.persons` - Synthetic person profiles with demographic and contact information

## Technology Glossary

**DuckDB**: An in-process SQL OLAP database management system optimized for analytics workloads. Provides fast analytical query performance with minimal setup.

**Faker**: A Python library for generating fake but realistic data. Used to create synthetic person profiles, addresses, and other demographic information.

**dbt**: Data Build Tool for transforming data in warehouses using SQL and Jinja templating. Enables version-controlled, tested data transformations.

**Prefect**: Modern workflow orchestration framework for building, scheduling, and monitoring data pipelines with Python.

## Roadmap

### Stage 1: Foundation ✅

- [✅] Core database architecture with DuckDB
- [✅] Person profile generation with Faker
- [✅] CRUD operations and logging infrastructure
- [✅] Interactive CLI for data generation

### Stage 2: Enhanced Entities 🚧

- [ ] Additional entity generators (companies, products, transactions)
- [ ] Relationship mapping between entities
- [ ] Data quality validation and constraints

### Stage 3: Time Series Integration 📅

- [ ] Temporal data generation patterns
- [ ] Event-based data simulation
- [ ] Historical data backfilling capabilities

### Stage 4: External API Integration 🌐

- [ ] TMDB API integration for entertainment data
- [ ] Synthetic person-to-event mapping
- [ ] Weather and location-based data enrichment

### Stage 5: Advanced Analytics 📊

- [ ] dbt transformation models
- [ ] Data marts for common analytics patterns
- [ ] ML feature engineering pipelines

### Stage 6: Production Orchestration 🔄

- [ ] Prefect workflow implementation
- [ ] Automated incremental data generation
- [ ] Data quality monitoring and alerting

## Stay Connected

[![Read On](https://img.shields.io/badge/Read%20On-Medium-12100E?style=for-the-badge&logo=medium&logoColor=white)](https://www.linkedin.com/in/chrisadan/)
[![Connect On](https://img.shields.io/badge/Connect%20On-LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/chrisadan/)
