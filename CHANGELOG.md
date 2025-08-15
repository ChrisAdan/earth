# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Modular architecture for optional components
- Companies module for enterprise data generation
- Campaigns module for marketing campaign simulation
- Automotive module for vehicle ownership modeling

### Changed

- Refactored package structure for PyPI distribution
- Improved industry classification system

### Deprecated

### Removed

### Fixed

### Security

## [0.1.0] - 2025-08-15

### Added

- Initial release of Earth synthetic data generator
- Person profile generation with realistic demographics
- Career progression modeling with age-based job titles and salaries
- 8-level career progression system (CL-1 to CL-8)
- Industry-aware salary calculations
- DuckDB integration for high-performance data storage
- Comprehensive US address and contact information generation
- Realistic email and phone number formatting
- Support for 150k+ person profiles with sub-second generation times

### Features

- **Core Data Generation**:
  - Person profiles with demographics, career, and contact info
  - Age-appropriate career progression modeling
  - Industry-specific salary calculations
- **Data Storage**:
  - DuckDB backend for efficient querying
  - Optimized for analytical workloads
- **Data Quality**:
  - Sanitized and validated US-specific data
  - Realistic correlations between age, career level, and income
  - Professional email and phone number formatting

### Technical Details

- Python 3.9+ support
- Pandas and DuckDB for data operations
- Faker integration for base data generation
- Type hints throughout codebase
- Comprehensive test suite

---

## Template for Future Releases

## [X.Y.Z] - YYYY-MM-DD

### Added

- New features, modules, or capabilities

### Changed

- Changes in existing functionality
- Performance improvements
- API modifications

### Deprecated

- Features marked for removal in future versions

### Removed

- Features removed in this version

### Fixed

- Bug fixes and corrections

### Security

- Security-related fixes and improvements

---

## Categories Guide

**Added** for new features.
**Changed** for changes in existing functionality.
**Deprecated** for soon-to-be removed features.
**Removed** for now removed features.
**Fixed** for any bug fixes.
**Security** in case of vulnerabilities.

## Version Numbering

- **MAJOR** version when you make incompatible API changes
- **MINOR** version when you add functionality in a backwards compatible manner
- **PATCH** version when you make backwards compatible bug fixes

## Module-Specific Changes

When adding module-specific changes, use subheadings:

### Companies Module (0.2.0)

- Added Fortune 500 company simulation
- Industry-specific company size distributions

### Campaigns Module (0.3.0)

- Multi-channel campaign modeling
- Brand portfolio management

### Automotive Module (0.4.0)

- Vehicle ownership probability modeling
- Realistic VIN and license plate generation
