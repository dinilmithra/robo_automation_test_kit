"""
Robo Automation
Comprehensive test reporting for Python projects with HTML reports and chart visualizations.
"""

from robo_automation_test_kit.utils import RoboHelper
from robo_automation_test_kit.utils.kill_stale_browsers import kill_browser_instance

__version__ = RoboHelper.get_version()

__all__ = ["RoboHelper", "kill_browser_instance"]
