# Robo Automation Test Kit

A comprehensive pytest plugin for test automation reporting with interactive HTML reports, chart visualizations, and support for parallel test execution.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-Apache%202.0-green)
![PyPI](https://img.shields.io/badge/PyPI-robo--automation--test--kit-brightgreen)

## Features

- 🧪 **Pytest Plugin Integration** - Seamless pytest hook-based integration
- 📊 **Interactive HTML Reports** - Beautiful, interactive test reports with charts
- 📈 **Data Visualization** - Multiple chart types:
  - Test status summary charts
  - Category breakdown analysis
  - Phase analysis
  - Center-based metrics
  - Status distribution by center
- 🔄 **Parallel Execution Support** - Built-in support for pytest-xdist
- 📑 **CSV/Excel Data Parametrization** - Load test data from CSV and Excel files
- 🎨 **Customizable Reports** - Extend reports with custom attributes and metrics
- 🚀 **Zero Configuration** - Works out of the box with sensible defaults

## Installation

### Basic Installation

```bash
pip install robo-automation-test-kit
```

### With Optional Features

```bash
# For parallel test execution
pip install robo-automation-test-kit[parallel]

# For Selenium-based browser automation
pip install robo-automation-test-kit[selenium]

# For system utilities
pip install robo-automation-test-kit[utils]

# For development
pip install robo-automation-test-kit[pytest]

# All features combined
pip install robo-automation-test-kit[pytest,selenium,parallel,utils]
```

### Using Poetry

```bash
poetry add robo-automation-test-kit
```

## Quick Start

### 1. Basic Test Setup

Create a test file `tests/test_example.py`:

```python
import pytest

class TestExample:
    def test_login_success(self):
        """User successfully logs in with valid credentials"""
        assert True
    
    def test_dashboard_loads(self):
        """Dashboard page loads and displays correctly"""
        assert True
    
    @pytest.mark.skip(reason="Feature not implemented")
    def test_future_feature(self):
        """This feature is planned for next release"""
        pass
```

### 2. Run Tests

```bash
# Run with default settings (parallel execution enabled by default)
pytest

# Run serially (disable parallel execution)
pytest -n 1

# Run specific test file
pytest tests/test_example.py::TestExample::test_login_success
```

### 3. View Report

After tests complete, open the generated HTML report:
```
reports/test_report_<timestamp>.html
```

### 4. Parameterized Tests with CSV Data

Create test data file `data/TestData.csv`:
```csv
username,password,expected_result
user1@example.com,ValidPass123,success
user2@example.com,WrongPass,failure
user3@example.com,ValidPass456,success
```

Create test with parametrization `tests/test_login.py`:
```python
import pytest

class TestLogin:
    @pytest.mark.datafile("TestData.csv")
    def test_login_with_data(self, row):
        """Login test with parameterized data: {username}"""
        username = row['username']
        password = row['password']
        expected = row['expected_result']
        
        # Your test logic here
        result = login(username, password)
        assert result == expected
```

## Configuration

### pytest.ini

Basic configuration is pre-configured in `pytest.ini`:

```ini
[pytest]
addopts = -n logical --capture=tee-sys
markers = 
    datafile: Mark test to use CSV/Excel data parametrization
```

### Environment Variables

Control test behavior via environment variables:

```powershell
# Windows PowerShell
$env:LOG_LEVEL="DEBUG"
$env:PARALLEL_EXECUTION="N"  # Disable parallel execution
$env:PROJECT_NAME="My Project"
$env:APP_ENV="staging"
$env:TEST_FRAMEWORK="pytest"

# Run tests
pytest
```

```bash
# Linux/macOS
export LOG_LEVEL=DEBUG
export PARALLEL_EXECUTION=N
export PROJECT_NAME="My Project"

pytest
```

### Dynamic Logging

Control pytest log level at runtime:

```powershell
# Windows PowerShell
$env:LOG_LEVEL="WARNING"
pytest --log-cli-level=$env:LOG_LEVEL
```

```bash
# Linux/macOS
export LOG_LEVEL=WARNING
pytest --log-cli-level=$LOG_LEVEL
```

Valid log levels: `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`, `NOTSET`

## Advanced Usage

### Customize Report Titles

```bash
pytest --robo-report-title="Smoke Tests - Sprint 45"
```

### Custom Report Attributes

Extend `conftest.py` with the `robo_modify_report_row` hook:

```python
def robo_modify_report_row(report_row, test_data):
    """Add custom attributes to each test result"""
    report_row['phase'] = test_data.get('Phase', 'General')
    report_row['category'] = test_data.get('Request Category', 'Functional')
    report_row['center'] = test_data.get('Center', 'HQ')
```

### Disable Parallel Execution Conditionally

```bash
# Via environment variable
export PARALLEL_EXECUTION=N
pytest

# Via command line
pytest -n 1
```

## Report Structure

Generated HTML reports include:

- **Summary Dashboard** - Quick overview of test results
- **Status Charts** - Visual breakdown of PASSED/FAILED/SKIPPED tests
- **Category Analysis** - Test distribution by category
- **Phase Breakdown** - Test distribution by phase
- **Results Table** - Detailed results with test names, duration, status, and logs
- **Error Details** - Full error messages and stack traces for failed tests

## Architecture

```
robo_automation_test_kit/
├── plugin.py                 # Pytest hook implementations
├── hookspec.py              # Hook specifications
├── utils/
│   ├── RoboHelper.py        # Core utilities (CSV loading, result aggregation)
│   └── reports/
│       ├── HtmlReportUtils.py       # HTML generation
│       └── EmailReportUtils.py      # Email notifications (future)
└── templates/
    └── html_report/
        ├── html_template.html       # Main template
        └── components/
            ├── summary-chart.html
            ├── category-chart.html
            ├── phase-chart.html
            ├── center-chart.html
            ├── status-center-chart.html
            └── results-table.html
```

## Data Flow

1. Tests execute via pytest (with optional xdist parallelization)
2. Plugin captures test results via `pytest_runtest_makereport` hook
3. Custom attributes injected via `robo_modify_report_row` hook
4. Results aggregated in `pytest_sessionfinish`
5. HTML report generated in `pytest_unconfigure`

## Extension Points

### Custom Report Metrics

Modify `RoboHelper.aggregate_test_results()` to compute custom metrics:

```python
def robo_modify_report_row(report_row, test_data):
    """Custom metric: Execution environment"""
    report_row['environment'] = os.getenv('APP_ENV', 'production')
    report_row['execution_date'] = datetime.now().strftime('%Y-%m-%d')
```

### Email Notifications

Extend `pytest_unconfigure` hook in conftest to send reports via email:

```python
from robo_automation_test_kit.utils.reports.EmailReportUtils import send_report

def pytest_unconfigure(config):
    """Send report via email after test completion"""
    report_path = config.robo_report_path
    send_report(report_path, to_addresses=['team@example.com'])
```

## Troubleshooting

### Missing Test Attributes

- Verify `robo_modify_report_row()` is defined in `conftest.py` (not plugin.py)
- Ensure CSV columns match field names in the hook

### Template Not Found

- Check `templates/html_report/` directory exists in project root
- Verify templates are included in package via `MANIFEST.in`

### CSV Encoding Errors

- Plugin automatically tries: utf-8-sig → latin-1 → utf-8
- For manual fixes, ensure CSV is UTF-8 encoded

### Parallel Execution Issues

- Verify pytest-xdist is installed: `pip install pytest-xdist`
- Check `pytest.ini` has `-n logical` option
- Disable via `PARALLEL_EXECUTION=N` or `-n 1`

## Common Commands

```bash
# Run all tests with default parallel execution
pytest

# Run serially (no parallelization)
pytest -n 1

# Run specific test
pytest tests/test_example.py::test_function

# Run with verbose output
pytest -v

# Run with specific log level
pytest --log-cli-level=DEBUG

# Run only failed tests from last run
pytest --lf

# Show print statements
pytest -s

# Generate report with custom title
pytest --robo-report-title="Custom Title"
```

## Development

### Local Development Setup

```bash
# Install in editable mode with all dev dependencies
poetry install

# Run tests
poetry run pytest

# Build package
poetry build

# Publish to PyPI (requires credentials)
poetry publish
```

### Prerequisites

- Python 3.8+
- pytest >= 7.4.0
- pandas >= 2.2.0
- jinja2 >= 3.0.0

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Commit with clear messages (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review test examples in `tests/` directory

## Related Projects

- [pytest](https://pytest.org) - Testing framework
- [pytest-xdist](https://pytest-xdist.readthedocs.io) - Parallel test execution
- [pandas](https://pandas.pydata.org) - Data manipulation
- [Jinja2](https://jinja.palletsprojects.com) - Template engine

## Changelog

### Version 1.0.0 (2026-02-03)
- Initial release
- Pytest plugin with HTML reporting
- CSV/Excel parametrization
- Parallel execution support (xdist)
- Interactive chart visualizations
- Customizable report attributes

---

**Happy Testing! 🧪**