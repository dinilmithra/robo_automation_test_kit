#!/usr/bin/env python3
"""
Library utility to kill stale Chrome and ChromeDriver processes created by
robo_automation_test_kit automation (identified by a CLI flag).
"""
from __future__ import annotations

import sys
from typing import Iterable

import psutil

AUTOMATION_FLAG = "--robo-automation"


def _print_header() -> None:
    print("\n=========================================")
    print("  Stale Browser Process Killer")
    print("=========================================\n")


def _normalize_name(name: str) -> str:
    n = name.lower()
    if n.endswith(".exe"):
        n = n[:-4]
    return n


def _kill_with_psutil() -> tuple[int, int]:
    if psutil is None:
        return (-1, -1)  # indicate psutil not available

    chrome_killed = 0
    driver_killed = 0

    # Collect PIDs by target name and automation flag
    chrome_pids: list[int] = []
    driver_pids: set[int] = set()

    for p in psutil.process_iter(attrs=["pid", "name", "cmdline", "ppid"]):
        try:
            name = p.info.get("name") or ""
            n = _normalize_name(name)
            if n == "chrome":
                cmdline = p.info.get("cmdline") or []
                cmdline_text = (
                    " ".join(cmdline) if isinstance(cmdline, list) else str(cmdline)
                )
                if AUTOMATION_FLAG in cmdline_text:
                    chrome_pids.append(int(p.info["pid"]))
                    # Walk parent chain to find chromedriver
                    try:
                        parent = psutil.Process(int(p.info.get("ppid") or 0))
                        for _ in range(5):
                            parent_name = _normalize_name(parent.name())
                            if parent_name == "chromedriver":
                                driver_pids.add(parent.pid)
                                break
                            parent = parent.parent()  # type: ignore[assignment]
                            if parent is None:
                                break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Terminate then kill remaining
    def terminate_group(pids: Iterable[int]) -> int:
        count = 0
        processes = []
        for pid in pids:
            try:
                processes.append(psutil.Process(pid))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        for proc in processes:
            try:
                proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        gone, alive = psutil.wait_procs(processes, timeout=2)
        count += len(gone)
        for proc in alive:
            try:
                proc.kill()
                count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return count

    print("Searching for automation Chrome processes...", flush=True)
    if chrome_pids:
        chrome_killed = terminate_group(chrome_pids)
        print(f"OK: Terminated {chrome_killed} Chrome process(es)")
    else:
        print("INFO: No Chrome processes found")

    print("Searching for automation ChromeDriver processes...", flush=True)
    if driver_pids:
        driver_killed = terminate_group(sorted(driver_pids))
        print(f"OK: Terminated {driver_killed} ChromeDriver process(es)")
    else:
        print("INFO: No ChromeDriver processes found")

    return (chrome_killed, driver_killed)


def _kill_with_system() -> tuple[int, int]:
    """Fallback using OS-native commands when psutil is unavailable."""
    print("WARN: psutil not available; refusing to kill all Chrome instances.")
    print("INFO: Install psutil to target automation-only processes.")
    return (0, 0)


def kill_browser_instance() -> int:
    _print_header()

    # Prefer psutil for accuracy; fall back to system tools
    chrome_killed, driver_killed = _kill_with_psutil()
    if chrome_killed == -1 and driver_killed == -1:
        chrome_killed, driver_killed = _kill_with_system()

    total = max(0, chrome_killed) + max(0, driver_killed)

    print("\n=========================================")
    if total > 0:
        print(f"OK: Successfully terminated {total} process(es)")
        print(f"   - Chrome: {max(0, chrome_killed)}")
        print(f"   - ChromeDriver: {max(0, driver_killed)}")
    else:
        print("OK: No stale browser processes found")
    print("=========================================\n")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(kill_browser_instance())
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(130)
