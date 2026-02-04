# AI Coding Agent Instructions - robo_automation_test_kit

## Project Overview

**robo_automation_test_kit** is a pytest plugin for comprehensive test automation reporting. It extracts test execution data from pytest and generates interactive HTML reports with chart visualizations (status summaries, category breakdowns, phase analysis). The plugin supports parallel test execution via pytest-xdist, reads test data from CSV/Excel files for parameterized testing, and provides extensibility hooks for projects to enrich test reports with custom attributes.

## Architecture & Key Components

### Core Plugin Structure (`robo_automation_test_kit/`)
- **plugin.py**: Pytest hook implementations in 13-hook lifecycle (pytest_addoption → pytest_plugin_registered → pytest_configure → pytest_sessionstart → pytest_collection → pytest_collection_modifyitems → pytest_generate_tests → pytest_runtest_protocol → pytest_runtest_makereport → pytest_configure_node → pytest_testnodedown → pytest_sessionfinish → pytest_unconfigure)
- **utils/RoboHelper.py**: Core utilities including `load_test_data()` (handles CSV/Excel with encoding fallbacks: utf-8-sig → latin-1 → utf-8), `get_env()`, `extract_test_case_name_from_docstring()`, `profile_name_from_driver()`, `print_results_summary()`, `aggregate_test_results()`, `build_test_data()`, `generate_report()`
- **utils/reports/HtmlReportUtils.py**: HTML generation helpers including `get_html_template()`, `get_report_summary()`, `get_report_data()`, `generate_and_save_html_report()`
- **templates/**: Jinja2 HTML templates (html_report/ and email_report/) with chart components and result tables using `FileSystemLoader` for templates in project root

### Data Flow
1. Tests execute via pytest (parallel via xdist by default: `-n logical` in pytest.ini)
2. `pytest_configure` initializes `config.test_results_summary` list, stores `_MASTER_CONFIG` globally, and caches conftest module for `robo_modify_report_row` hook
3. `pytest_generate_tests` hook parametrizes tests using CSV/Excel data from `@pytest.mark.datafile("filename.csv")` marker
4. `pytest_runtest_makereport` hook captures each test result (status, duration, title from docstring, error logs) and calls `robo_modify_report_row(report_row, test_data)` for custom attributes
5. For xdist workers: Each worker has own `config.test_results_summary`; worker results passed to master via `pytest_testnodedown`
6. Master aggregates worker results via `aggregate_test_results()` which merges all collected test results
7. On `pytest_unconfigure`: `generate_report()` renders Jinja2 templates with aggregated results and saves to `reports/test_report_<timestamp>.html`

### Critical Patterns
- **Result Collection**: Results in `config.test_results_summary` as dict list with keys: `test_status` (PASSED/FAILED/ERROR/SKIPPED), `test_name`, `test_title`, `duration`, `error_log`, plus custom fields merged from CSV test data (Phase, Request Category, Center, etc.)
- **Hook Implementation Discovery**: `robo_modify_report_row()` hook found via direct `sys.modules` lookup in `pytest_configure()` (not pytest's hook discovery) because conftest.py loaded before hookspec registration; implementation must be in conftest.py
- **xdist Aggregation**: Master config stored in global `_MASTER_CONFIG`; per-worker `config.test_results_summary` lists collected independently; master aggregates all results via `aggregate_test_results()` which combines lists
- **Template Rendering**: Uses `FileSystemLoader` with fallback: first tries project root `templates/html_report/`, then falls back to package-nested templates; not PackageLoader
- **Environment Configuration**: Read via `os.getenv()` for `PROJECT_NAME`, `APP_ENV`, `TEST_FRAMEWORK`, `PARALLEL_EXECUTION`, `LOG_LEVEL` (can disable xdist via `PARALLEL_EXECUTION=N`)
- **Status Mapping**: ERROR status treated as FAILED in summary calculations (see `get_report_summary()`)

## Common Workflows & Commands

### Setup & Installation
```powershell
# Local dev install (editable mode)
pip install -e .

# Run tests with default HTML report (parallel via xdist by default: -n logical in pytest.ini)
pytest

# Run tests serially (disable xdist)
pytest -n 1

# Run with custom report title
pytest --robo-report-title="Smoke Tests"

# Run specific test file or test
pytest tests/test_Template.py::test_name

# Disable parallel execution via environment
$env:PARALLEL_EXECUTION="N"; pytest

# Control log level dynamically (PowerShell)
$env:LOG_LEVEL="DEBUG"; pytest --log-cli-level=$env:LOG_LEVEL

# View console summary before HTML report is generated
# (use print_results_summary() in pytest_unconfigure hook)
```

### Test Data Integration
- CSV/Excel files in `data/` directory (TestData.csv, RoboTestData.csv)
- Parametrize tests via `@pytest.mark.datafile("filename.csv")` marker (pytest.ini registers marker)
- `pytest_generate_tests()` hook loads data via `load_test_data()` which handles encoding fallbacks: utf-8-sig → latin-1 → utf-8
- Handles .xlsx via zipfile detection + openpyxl; .csv via pandas with encoding retry logic
- Test receives each row as dict parameter `row` in test function signature

### Test Naming & Reporting & Custom Attributes
- Test titles from function docstring extracted via `extract_test_case_name_from_docstring()`; falls back to pytest nodeid if docstring empty
- Custom test data fields (Phase, Request Category, Center) merged from CSV data into result dict via `robo_modify_report_row()` hook implementation in conftest.py
- Hook signature: `robo_modify_report_row(report_row, test_data)` - modifies `report_row` dict in-place to add custom fields
- Use `print_results_summary()` to view console summary before HTML report generation

### Debugging & Verification
- HTML reports saved to `reports/` with timestamp; check browser logs for rendering issues
- Console shows test status, duration, and custom fields via `print_results_summary()`
- For xdist issues: Check worker node configs initialized and results aggregated properly
- Log level via environment: `$env:LOG_LEVEL="DEBUG"`

## Project-Specific Conventions

1. **Test Naming**: Docstrings provide human-readable test titles in reports; fallback to pytest nodeid if missing
2. **Report Organization**: Results grouped by status (PASSED/FAILED/SKIPPED/RERUN); ERROR status treated as FAILED in summaries
3. **Parallel Safety**: Global state (`_MASTER_CONFIG`, `test_results_summary`) isolated per worker; aggregation happens only in master
4. **Template Inheritance**: Base template includes component partials via Jinja2 `{% include %}` for modular report structure

## Key Files & Their Roles

| File | Purpose |
|------|---------|
| robo_automation_test_kit/plugin.py | 13-hook pytest lifecycle - initialization, result capture, xdist aggregation, report generation |
| robo_automation_test_kit/utils/RoboHelper.py | CSV/Excel loading via `load_test_data()`, docstring extraction, test result aggregation via `aggregate_test_results()` |
| robo_automation_test_kit/utils/reports/HtmlReportUtils.py | `get_html_template()`, `get_report_summary()`, `generate_and_save_html_report()` for Jinja2 rendering |
| templates/html_report/html_template.html | Main Jinja2 template rendering summary and results table (looks in project root first, falls back to package) |
| templates/html_report/components/ | Chart partials (summary-chart, category-chart, phase-chart, center-chart, status-center-chart, results-table) |
| conftest.py | Project's `robo_modify_report_row()` hook implementation - enriches test results with custom attributes |
| pytest.ini | pytest config: xdist `-n logical` default, custom `datafile` marker, logging format with --capture=tee-sys |
| data/ | CSV/Excel test data files (TestData.csv, RoboTestData.csv) |
| reports/ | Output directory for generated HTML reports with timestamp naming (e.g., test_report_2024-02-03_14-30-45.html) |

## Critical Integration Points

- **pytest Hook Execution Order**: `pytest_addoption` → `pytest_plugin_registered` (xdist check) → `pytest_configure` (init) → `pytest_collection` (parse test selectors) → `pytest_collection_modifyitems` (reserved) → `pytest_generate_tests` (parametrize from CSV) → `pytest_runtest_makereport` (per test result) → `pytest_configure_node` (xdist workers) → `pytest_testnodedown` (workers finish) → `pytest_sessionfinish` (before report) → `pytest_unconfigure` (report generation)
- **Global State for xdist**: `_MASTER_CONFIG` and `_CONFTEST_HOOK_MODULE` stored globally; workers initialize own `config.test_results_summary` independently; master aggregates all results via `aggregate_test_results()`
- **Hook Implementation Discovery**: `robo_modify_report_row()` hook from conftest.py found via direct `sys.modules` lookup in `pytest_configure()` because conftest loads before hookspec registration (pytest's standard hook discovery fails here)
- **Jinja2 Template Loading**: `get_html_template()` tries `Path.cwd() / templates/html_report/` first (source template), then falls back to package-nested location (installed template)
- **Result Dict Structure**: Each result dict must include: `test_status`, `test_name`, `test_title`, `duration` (float seconds), `error_log`, custom fields from CSV merged via `robo_modify_report_row()` hook
- **CSV Encoding Handling**: `load_test_data()` tries utf-8-sig → latin-1 → utf-8 for .csv; detects .xlsx via zipfile and uses openpyxl engine; always returns pandas DataFrame as dict records

## Typical Extension Scenarios

- **Adding Custom Test Attributes**: Implement `robo_modify_report_row(report_row, test_data)` in conftest.py to merge CSV fields into result dict (already shown as example in conftest.py)
- **Adding Report Metrics**: Modify `get_report_summary()` in HtmlReportUtils.py to compute new metrics; update html_template.html to display them
- **Custom Chart Types**: Add new component HTML file in `templates/html_report/components/` (e.g., custom-chart.html); include via `{% include "custom-chart.html" %}` in main template
- **Email Notifications**: Template structure exists in `templates/email_report/`; hook into `pytest_unconfigure` in plugin.py to send via SMTP after `generate_report()`
- **Disabling Parallel Execution Conditionally**: Set `PARALLEL_EXECUTION=N` env var before pytest run; `pytest_plugin_registered()` hook will unregister xdist dsession plugin

## Gotchas & Debugging Tips

- **Missing Custom Attributes**: Verify `robo_modify_report_row()` is in conftest.py (not plugin.py); verify hook called in `pytest_runtest_makereport()` with correct signature `(report_row, row)` where `row` is CSV data dict
- **Missing Results in xdist**: Check that `aggregate_test_results()` is called in `pytest_unconfigure()`; verify worker results passed via `pytest_testnodedown` hook
- **Template Not Found**: Plugin tries project root `templates/html_report/` first via FileSystemLoader, then falls back to package; ensure templates/ directory exists and is in MANIFEST.in for package builds
- **Encoding Errors in CSV**: `load_test_data()` tries utf-8-sig → latin-1 → utf-8 but logs errors; check logger for encoding fallback messages; pandas dtype=str prevents float/int conversion
- **Report Path Issues**: Default path is `reports/test_report_<timestamp>.html`; ensure reports/ directory writable; custom path via `--robo-report=path.html` option
- **Parallel Execution Not Working**: Check `pytest.ini` has `-n logical` and pytest-xdist installed; verify PARALLEL_EXECUTION env var not set to "N"; check `pytest_plugin_registered()` is called
- **Hook Not Found**: If `robo_modify_report_row()` not discovered, check it's in conftest.py module (not imported); plugin looks via direct sys.modules scan in `pytest_configure()`
