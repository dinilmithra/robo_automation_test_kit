"""
Utility functions for robo-reporter
"""

from .RoboHelper import (
    load_test_data,
    get_env,
    extract_test_case_name_from_docstring,
    print_results_summary,
    flatten_results,
)
from .kill_stale_browsers import kill_browser_instance as kill_stale_browsers

__all__ = [
    "load_test_data",
    "get_env",
    "extract_test_case_name_from_docstring",
    "print_results_summary",
    "flatten_results",
    "kill_stale_browsers",
]
