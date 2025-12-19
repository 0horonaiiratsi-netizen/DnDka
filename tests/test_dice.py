import pytest

from app.dice import DiceError, roll


def test_basic_roll_structure():
    result = roll("2d6+1")
    assert result.expression == "2d6+1"
    assert len(result.rolls) == 2
    assert result.modifier == 1
    assert result.total == sum(result.rolls) + 1


def test_reject_bad_expression():
    with pytest.raises(DiceError):
        roll("bad")


def test_limits():
    with pytest.raises(DiceError):
        roll("0d6")
    with pytest.raises(DiceError):
        roll("51d6")
