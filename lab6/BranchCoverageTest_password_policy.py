"""Tests explicitly designed to exercise both outcomes of decisions."""
import pytest
from password_policy import check_password, strength, suggest_fix


@pytest.mark.parametrize(
    ("password", "expected"),
    [
        ("Abcdef1!", []),                # length 8 boundary: neither short nor long
        ("Abcdef1", ["too short", "no special"]),
        ("A" * 65 + "a1!", ["too long"]),
        ("password", ["common", "no uppercase", "no digit", "no special"]),
        ("PASSWORD", ["common", "no lowercase", "no digit", "no special"]),
        ("ABCDEF12", ["no lowercase", "no special"]),
        ("abcdef12", ["no uppercase", "no special"]),
        ("Abcdefgh", ["no digit", "no special"]),
        ("Abcdef12", ["no special"]),
        ("Abcdef1!", []),
    ],
)
def test_password_policy_branches(password, expected):
    assert check_password(password) == expected


def test_strength_no_issues_below_14():
    assert strength("Abcdef1!") == "good"


def test_strength_no_issues_at_least_14():
    assert strength("Abcdefghijk1!X") == "strong"


def test_strength_two_issues_or_fewer():
    assert strength("ABCDEF12") == "weak"


def test_strength_more_than_two_issues():
    assert strength("abc") == "very weak"


def test_suggest_fix_empty_list_branch():
    assert suggest_fix([]) == "none needed"


def test_suggest_fix_too_short_branch():
    assert suggest_fix(["too short"]) == "add more characters"


def test_suggest_fix_common_branch():
    assert suggest_fix(["common"]) == "avoid common passwords"


@pytest.mark.parametrize("issue, expected", [
    ("no uppercase", "add uppercase"),
    ("no lowercase", "add lowercase"),
    ("no digit", "add digit"),
    ("no special", "add special"),
])
def test_suggest_fix_starts_with_no(issue, expected):
    assert suggest_fix([issue]) == expected


def test_suggest_fix_fallback_branch():
    assert suggest_fix(["too long"]) == "shorten it"
