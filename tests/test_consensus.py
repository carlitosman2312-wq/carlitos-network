import pytest

from carlitos.consensus import COIN, format_amount, parse_amount, subsidy


def test_subsidy_schedule_and_genesis():
    assert subsidy(0) == 0
    assert subsidy(1) == 100 * COIN
    assert subsidy(500_000) == 100 * COIN
    assert subsidy(500_001) == 50 * COIN
    assert subsidy(1_000_000) == 50 * COIN
    assert subsidy(1_000_001) == 25 * COIN


def test_subsidy_eventually_reaches_zero_without_negative_values():
    assert subsidy(64 * 500_000 + 1) == 0
    assert subsidy(10_000_000_000) == 0


def test_amount_conversion_never_uses_float_rounding():
    assert parse_amount("1.00000001") == 100_000_001
    assert format_amount(100_000_001) == "1.00000001"
    with pytest.raises(ValueError):
        parse_amount("0.000000001")
    with pytest.raises(ValueError):
        parse_amount("NaN")
