"""
Simplified conftest.py - uses robo-reporter plugin for report generation
All fixtures, hooks, and environment setup are provided by the robo_reporter plugin
"""

import pytest
import logging
from robo_automation_test_kit.utils import get_env
from src.utils.CommonUtils import CommonUtils

logger = logging.getLogger(__name__)


# ============================================================================
# Project-Specific Fixtures (if needed)
# ============================================================================
# All standard fixtures (row, driver, wait) are provided by robo_automation_test_kit plugin
# Add project-specific fixtures here if required


# ============================================================================
# robo_modify_report_row Hook Implementation
# ============================================================================
# This function enriches test report rows with custom data from CSV test data
# Called directly by robo_automation_test_kit plugin for each test execution


def robo_modify_report_row(report_row, test_data):
    """
    Example implementation of robo_custom_attribute_data hook.

    This function allows the source project to:
    - Extract custom attributes from the data_row
    - Add project-specific fields to test results
    - Transform or enrich test data

    Args:
        report_row: Dictionary with default test report data
        test_data: Dictionary with parametrized test data from CSV

    Returns:
        Dictionary with custom attributes to merge into test_data.
        Keys will override or extend the default test_data fields.
    """
    # Example: Extract 'Test Case Name' from data_row
    # and add any custom fields
    report_row["test_case_name"] = test_data.get("Test Case Name", "")
    report_row["Phase"] = test_data.get("Phase", "")
    report_row["Request Category"] = test_data.get("Request Category", "")
    report_row["Request Sub-Category"] = test_data.get("Request Sub-Category", "")
    report_row["Center"] = test_data.get("Center", "")
    # Add more custom attributes as needed from data_row
    # "Jira ID": data_row.get("Jira ID", ""),
    # "sprint": data_row.get("Sprint", ""),

    return report_row


# ============================================================================
# robo_html_report_ready Hook Implementation
# ============================================================================
# This hook is called after HTML report is generated and saved
# Use this to send email, upload to cloud, or integrate with other systems


@pytest.hookimpl
def robo_html_content_ready(config, html_content, report_path, email_body):
    """
    Example implementation of robo_html_content_ready hook.

    This hook is called after the HTML report is successfully generated.
    Use this to send the report via email or integrate with other systems.

    Args:
        config: Pytest config object with access to options and settings
        html_content: Complete HTML content as string (ready for email/attachment)
        report_path: Absolute path to the saved HTML report file
        email_body: Pre-rendered HTML email body content from email template
    """
    logger.info(f"HTML report ready at: {report_path}")
    logger.info(f"Report generated successfully")

    # Example: Send email with HTML report
    # Uncomment and configure SMTP settings to enable email notifications

    # from src.notifications.SendEmail import send_html_email
    #
    # subject = f"Test Report - {report_path}"
    # recipients = ["team@example.com"]
    #
    # send_html_email(
    #     subject=subject,
    #     html_content=email_body,
    #     recipients=recipients,
    #     attachment_path=report_path
    # )


# ============================================================================
# Report Summary Hook
# ============================================================================
