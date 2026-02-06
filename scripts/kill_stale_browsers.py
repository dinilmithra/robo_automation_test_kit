#!/usr/bin/env python3
"""Thin wrapper for the library kill-stale-browsers utility."""
import sys

from robo_automation_test_kit.utils.kill_stale_browsers import main


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(130)
