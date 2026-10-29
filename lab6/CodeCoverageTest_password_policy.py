"""Tests targeting at least 90% line coverage for password_policy.py."""
import pytest
from password_policy import check_password, strength, suggest_fix


@pytest.mark.parametrize(
    ("password", "expected"),
    [
        ("Abcdef1!", []),
        ("Abcdefghijkl1!", []),  # long enough to be strong
        ("abc", ["too short", "no uppercase", "no digit", "no special"]),
        ("A" * 65 + "a1!", ["too long"]),
        ("password", ["common", "no uppercase", "no digit", "no special"]),
        ("123456", ["too short", "common", "no uppercase", "no lowercase", "no special"]),
        ("qwerty", ["too short", "common", "no uppercase", "no digit", "no special"]),
        ("letmein", ["too short", "common", "no uppercase", "no digit", "no special"]),
        ("ABCDEFG1!", ["no lowercase"]),
        ("abcdefgh1!", ["no uppercase"]),
        ("Abcdefgh!", ["no digit"]),
        ("Abcdefgh1", ["no special"]),
        ("ABC123!!", ["no lowercase"]),
        ("abc123!!", ["no uppercase"]),
        ("Abcdef1!" * 9, ["too long"]),
    ],
)
def test_check_password_scenarios(password, expected):
    assert check_password(password) == expected


def test_strength_good():
    assert strength("Abcdef1!") == "good"


def test_strength_strong():
    assert strength("Abcdefghijk1!X") == "strong"


def test_strength_weak_with_one_issue():
    assert strength("Abcdefgh!") == "weak"


def test_strength_very_weak_with_multiple_issues():
    assert strength("abc") == "very weak"


def test_suggest_fix_empty_issues():
    assert suggest_fix([]) == "none needed"


def test_suggest_fix_too_short_first():
    assert suggest_fix(["too short", "no uppercase"]) == "add more characters"


def test_suggest_fix_common_first():
    assert suggest_fix(["common", "no digit"]) == "avoid common passwords"


def test_suggest_fix_missing_character_category():
    assert suggest_fix(["no uppercase"]) == "add uppercase"
    assert suggest_fix(["no lowercase"]) == "add lowercase"
    assert suggest_fix(["no digit"]) == "add digit"
    assert suggest_fix(["no special"]) == "add special"


def test_suggest_fix_other_issue_falls_back_to_shorten():
    assert suggest_fix(["too long"]) == "shorten it"
