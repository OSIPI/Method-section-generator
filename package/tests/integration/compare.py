"""Readable comparison for integration goldens.

Used by ``tests/test_integration.py``. Reports EVERY differing key at once
(not just the first), and renders a unified line diff for report prose so a
single changed sentence shows as one ``-``/``+`` pair instead of a wall of text.
The same output appears locally under ``pytest -v`` and in the CI log.
"""

from __future__ import annotations

import difflib
import json
from typing import Any

_TEXT_KEYS = frozenset({"basic_report", "extended_report"})


def _is_text_key(key: str, expected: Any, actual: Any) -> bool:
    """Return True when a key's values should be diffed as text lines."""
    if key in _TEXT_KEYS or key.endswith("_text"):
        return True
    return isinstance(expected, str) and isinstance(actual, str)


def _text_diff(key: str, expected: Any, actual: Any) -> str:
    """Return a unified line diff (old vs new) for two string values."""
    return "\n".join(
        difflib.unified_diff(
            str(expected).splitlines(),
            str(actual).splitlines(),
            fromfile=f"{key} (expected)",
            tofile=f"{key} (actual)",
            lineterm="",
        )
    )


def _struct_diff(expected: Any, actual: Any) -> str:
    """Return an expected/actual block for a differing structured value."""
    exp = json.dumps(expected, indent=2, sort_keys=True, default=str)
    act = json.dumps(actual, indent=2, sort_keys=True, default=str)
    return f"  expected: {exp}\n  actual:   {act}"


def assert_report_matches(
    expected: dict[str, Any], actual: dict[str, Any], case: str
) -> None:
    """Assert two reports are equal, reporting all differences at once.

    Args:
        expected: The committed golden (``expected_output.json``), JSON-normalized.
        actual: The freshly generated report, JSON-normalized.
        case: The example name, used to label the failure message.

    Raises:
        AssertionError: If the key sets differ or any value differs. The message
            lists key-set drift first, then one block per differing key: a
            unified line diff for report prose (and any string value), or an
            expected/actual dump for structured values.
    """
    blocks: list[str] = []

    only_expected = sorted(set(expected) - set(actual))
    only_actual = sorted(set(actual) - set(expected))
    if only_expected:
        blocks.append(f"keys only in expected: {only_expected}")
    if only_actual:
        blocks.append(f"keys only in actual: {only_actual}")

    for key in sorted(set(expected) & set(actual)):
        if expected[key] == actual[key]:
            continue
        if _is_text_key(key, expected[key], actual[key]):
            body = _text_diff(key, expected[key], actual[key])
        else:
            body = _struct_diff(expected[key], actual[key])
        blocks.append(f"[{key}] differs:\n{body}")

    if blocks:
        raise AssertionError(
            f"{case}: {len(blocks)} difference(s)\n\n" + "\n\n".join(blocks)
        )
