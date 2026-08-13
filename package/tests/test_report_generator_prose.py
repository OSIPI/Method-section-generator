"""Unit tests for the Tier-1 report-prose helpers and small text fixes.

These lock the readability behavior introduced in the report-text rewrite:
missing-value handling, natural-language joining, duration-list collapsing,
internal-token display, and the bolus-cutoff-delay closing parenthesis.
"""

import pytest

from pyaslreport.modalities.asl.report_generator import ReportGenerator as R


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, True),
        ("", True),
        ("   ", True),
        ("N/A", True),
        (" N/A ", True),
        (0, False),
        (0.0, False),
        ("3D", False),
        (11.24, False),
    ],
)
def test_is_missing(value: object, expected: bool) -> None:
    """Missing-value helper treats None, blanks, and N/A as absent."""
    assert R._is_missing(value) is expected


def test_join_and() -> None:
    """Natural-language joining handles one, two, and many values."""
    assert R._join_and([]) == ""
    assert R._join_and(["a"]) == "a"
    assert R._join_and(["a", "b"]) == "a and b"
    assert R._join_and(["a", "b", "c"]) == "a, b, and c"
    # falsy parts are dropped
    assert R._join_and(["a", "", None, "c"]) == "a and c"


def test_format_duration_list_collapses_identical() -> None:
    """Identical duration arrays collapse to one displayed value."""
    assert R._format_duration_list([1166.67, 1166.67, 1166.67]) == "1166.67ms"


def test_format_duration_list_keeps_distinct() -> None:
    """Distinct duration arrays preserve all displayed values."""
    assert R._format_duration_list([1000, 2000]) == "1000ms, 2000ms"


def test_format_duration_list_scalar_and_missing() -> None:
    """Scalar values display with units while missing values disappear."""
    assert R._format_duration_list(1450) == "1450ms"
    assert R._format_duration_list("N/A") == ""
    assert R._format_duration_list(None) == ""


def test_pattern_words_display_tokens() -> None:
    """Every volume pattern is rendered in control-label pair terms."""
    assert R._pattern_words("deltam", plural=True) == ("control-label", "pairs")
    assert R._pattern_words("deltam", plural=False) == ("control-label", "pair")
    assert R._pattern_words("controllabel", plural=True) == ("control-label", "pairs")
    assert R._pattern_words("labelcontrol", plural=False) == ("label-control", "pair")


def test_bolus_cutoff_delay_inconsistent_closes_parenthesis() -> None:
    """Inconsistent bolus-cutoff delay prose closes its parenthesis."""
    values = {"BolusCutOffDelayTime": [["fileA", 800], ["fileB", 900]]}
    combined_errors = {
        "BolusCutOffDelayTime": ["INCONSISTENCY: differing bolus cutoff delay"]
    }
    out = R.handle_bolus_cutoff_delay_time(values, combined_errors)
    assert out.startswith("(inconsistent")
    assert out.endswith(")"), out
    assert out.count("(") == out.count(")")
