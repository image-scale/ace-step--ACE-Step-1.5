"""Parse unittest verbose output into per-test results."""

from __future__ import annotations

import re


def parse_log(log: str) -> dict[str, str]:
    """Parse test runner output into per-test results.

    Args:
        log: Full stdout+stderr output of ``bash run_test.sh 2>&1``.

    Returns:
        Dict mapping test_id to status.
        - test_id: unittest native format, e.g.
          ``module.Class.test_name``
        - status: one of ``"PASSED"``, ``"FAILED"``, ``"SKIPPED"``, ``"ERROR"``
    """
    results: dict[str, str] = {}
    lines = log.split("\n")

    current_test_id: str | None = None
    waiting_for_status = False

    # Regex for test declaration line. The parenthesized path must contain
    # at least one dot (dotted module path) to avoid false positives from
    # Python tracebacks like "Traceback (most recent call last):".
    decl_re = re.compile(r"^(\S+)\s+\(([a-zA-Z_][\w]*(?:\.[a-zA-Z_][\w]*)+)\)")

    # Regex for inline status: "... ok", "... FAIL", "... ERROR", "... skipped"
    inline_status_re = re.compile(r"\.\.\.\s+(ok|FAIL|ERROR|skipped\b)")

    # Regex for "... " appearing on a line (marks pending status)
    dots_re = re.compile(r"\.\.\.\s")

    # Regex for standalone status on its own line
    standalone_status_re = re.compile(r"^(ok|FAIL|ERROR|skipped\b)")

    for line in lines:
        # Check for test declaration
        decl_match = decl_re.match(line)
        if decl_match:
            full_path = decl_match.group(2)
            current_test_id = full_path
            waiting_for_status = False

            # Check if status is on the same line
            status_match = inline_status_re.search(line)
            if status_match:
                results[current_test_id] = _map_status(status_match.group(1))
                current_test_id = None
                continue

            # Check if "... " appears (status may come on later line)
            if dots_re.search(line):
                waiting_for_status = True
            continue

        # If we have a current test, check for status
        if current_test_id is not None:
            # Check for inline status on description/output line
            status_match = inline_status_re.search(line)
            if status_match:
                results[current_test_id] = _map_status(status_match.group(1))
                current_test_id = None
                waiting_for_status = False
                continue

            # Check if "... " appears (description line)
            if not waiting_for_status and dots_re.search(line):
                waiting_for_status = True
                continue

            # Check for standalone status (ok/FAIL/ERROR on own line)
            if waiting_for_status:
                standalone_match = standalone_status_re.match(line)
                if standalone_match:
                    results[current_test_id] = _map_status(
                        standalone_match.group(1)
                    )
                    current_test_id = None
                    waiting_for_status = False
                    continue

    # Also parse FAIL/ERROR sections at the bottom of unittest output:
    #   FAIL: test_name (module.Class.test_name)
    #   ERROR: test_name (module.Class.test_name)
    fail_error_re = re.compile(
        r"^(FAIL|ERROR): \S+\s+\(([a-zA-Z_][\w]*(?:\.[a-zA-Z_][\w]*)+)\)"
    )
    for line in lines:
        m = fail_error_re.match(line)
        if m:
            status_str = m.group(1)
            test_id = m.group(2)
            mapped = "FAILED" if status_str == "FAIL" else "ERROR"
            if test_id not in results:
                results[test_id] = mapped

    return results


def _map_status(raw: str) -> str:
    if raw == "ok":
        return "PASSED"
    elif raw == "FAIL":
        return "FAILED"
    elif raw == "ERROR":
        return "ERROR"
    elif raw.startswith("skipped"):
        return "SKIPPED"
    return "ERROR"

