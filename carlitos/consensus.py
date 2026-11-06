"""Monetary constants shared by the development-chain implementation."""

from decimal import Decimal, InvalidOperation

COIN = 100_000_000
MAX_MONEY = 100_000_000 * COIN
INITIAL_SUBSIDY = 100 * COIN
HALVING_INTERVAL = 500_000
COINBASE_MATURITY = 100
TARGET_BLOCK_SECONDS = 600
DIFFICULTY_ADJUSTMENT_INTERVAL = 2_016
TARGET_TIMESPAN_SECONDS = 1_209_600
NETWORK_ID = "carlitos-devnet-v1"


def subsidy(height: int) -> int:
    """Return the consensus subsidy in base units; genesis has no reward."""
    if not isinstance(height, int) or height < 0:
        raise ValueError("height must be a non-negative integer")
    if height == 0:
        return 0
    halvings = (height - 1) // HALVING_INTERVAL
    if halvings >= 64:
        return 0
    return INITIAL_SUBSIDY >> halvings


def parse_amount(value: str) -> int:
    """Parse a decimal CRLTS amount without using binary floating point."""
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError):
        raise ValueError("amount must be a decimal number") from None
    if not amount.is_finite() or amount <= 0:
        raise ValueError("amount must be greater than zero")
    scaled = amount * COIN
    if scaled != scaled.to_integral_value():
        raise ValueError("amount supports at most 8 decimal places")
    base_units = int(scaled)
    if base_units > MAX_MONEY:
        raise ValueError("amount exceeds the maximum monetary supply")
    return base_units


def format_amount(base_units: int) -> str:
    if not isinstance(base_units, int):
        raise TypeError("base_units must be an integer")
    sign = "-" if base_units < 0 else ""
    value = abs(base_units)
    whole, fraction = divmod(value, COIN)
    return f"{sign}{whole}.{fraction:08d}"
