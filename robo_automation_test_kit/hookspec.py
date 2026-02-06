"""
Hook specifications for robo_automation_test_kit plugin.
These hooks allow source projects to customize the reporting behavior.
"""

import pytest


@pytest.hookspec
def robo_modify_report_row(report_row, test_data):
    """
    Hook specification for source projects to provide custom test data attributes.

    Source projects can implement this hook in their conftest.py to:
    - Extract custom attributes from test_data (CSV/Excel row)
    - Add project-specific fields to test results
    - Transform or enrich test data using both report_row and test_data

    Args:
        report_row: Dictionary with base test result data (status, duration, error_log, etc.)
        test_data: Dictionary with parametrized test data from CSV/Excel

    Returns:
        Dictionary with custom attributes to merge into report_row.
        Keys in this dict will override or extend the default report_row fields.

    Example in source project's conftest.py:
        @pytest.hookimpl
        def robo_modify_report_row(report_row, test_data):
            return {
                'test_case_name': test_data.get('Test Case Name', ''),
                'custom_field': test_data.get('Custom Field', ''),
                'priority': test_data.get('Priority', 'Medium'),
            }
    """
    pass


@pytest.hookspec
def robo_html_content_ready(config, html_content, report_path):
    """
    Hook specification for source projects to receive generated HTML report content.

    This hook is called after the HTML report is successfully generated and saved.
    Source projects can implement this hook in their conftest.py to:
    - Send HTML report as email attachment
    - Send email body content via SMTP
    - Upload report to cloud storage
    - Post-process or transform the HTML content
    - Integrate with other reporting systems

    Args:
        config: Pytest config object with access to options and settings
        html_content: Complete HTML content as string (ready for email/attachment)
        report_path: Absolute path to the saved HTML report file

    Returns:
        None. This is a notification hook, return values are ignored.

    Example in source project's conftest.py:
        @pytest.hookimpl
        def robo_html_content_ready(config, html_content, report_path):
            '''Send HTML report via email after generation.'''
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Test Report - Test Execution Complete"
            msg['From'] = 'test@example.com'
            msg['To'] = 'team@example.com'

            # Attach email body as HTML
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP('smtp.example.com') as server:
                server.send_message(msg)
    """
    pass
