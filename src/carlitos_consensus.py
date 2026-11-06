"""Reference-only model of Carlitos issuance and Bitcoin-style difficulty retargeting.

This module is a specification aid. It is NOT wired into a node and MUST NOT be
treated as production consensus code until ported to Bitcoin Core and tested there.
All monetary and target arithmetic uses Python integers (no floating point).
"""

from __future__ import annotations

from dataclasses import dataclass


COIN = 100_000_000
INITIAL_SUBSIDY = 100 * COIN
HALVING_INTERVAL = 500_000
TARGET_SPACING = 600
TARGET_TIMESPAN = 1_209_600
DIFFICULTY_ADJUSTMENT_INTERVAL = TARGET_TIMESPAN // TARGET_SPACING
POW_LIMIT = int("00000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffff", 16)
POW_LIMIT_COMPACT = 0x1D00FFFF


@dataclass(frozen=True)
class CompactTarget:
    value: int
    negative: bool
    overflow: bool


def block_subsidy(height: int) -> int:
    """Return block subsidy in base units; genesis (height 0) has no subsidy.

    The first reward-bearing block is height 1. Each era contains exactly
    HALVING_INTERVAL reward-bearing blocks. Integer right shifts intentionally
    discard fractional base units; there is no later make-up issuance.
    """
    if not isinstance(height, int) or isinstance(height, bool) or height < 0:
        raise ValueError("height must be a non-negative integer")
    if height == 0:
        return 0
    halvings = (height - 1) // HALVING_INTERVAL
    if halvings >= INITIAL_SUBSIDY.bit_length():
        return 0
    return INITIAL_SUBSIDY >> halvings


def decode_compact(compact: int) -> CompactTarget:
    """Decode Bitcoin's compact nBits target format, including sign/overflow flags."""
    if not isinstance(compact, int) or isinstance(compact, bool) or not 0 <= compact <= 0xFFFFFFFF:
        raise ValueError("compact must be an unsigned 32-bit integer")

    size = compact >> 24
    word = compact & 0x007FFFFF
    if size <= 3:
        value = word >> (8 * (3 - size))
    else:
        value = word << (8 * (size - 3))

    negative = word != 0 and (compact & 0x00800000) != 0
    overflow = word != 0 and (
        size > 34 or (word > 0xFF and size > 33) or (word > 0xFFFF and size > 32)
    )
    return CompactTarget(value=value, negative=negative, overflow=overflow)


def encode_compact(target: int) -> int:
    """Encode a positive target as Bitcoin compact nBits."""
    if not isinstance(target, int) or isinstance(target, bool) or target <= 0:
        raise ValueError("target must be a positive integer")
    if target.bit_length() > 256:
        raise ValueError("target must fit in 256 bits")

    size = (target.bit_length() + 7) // 8
    if size <= 3:
        compact = target << (8 * (3 - size))
    else:
        compact = target >> (8 * (size - 3))

    if compact & 0x00800000:
        compact >>= 8
        size += 1

    compact &= 0x007FFFFF
    compact |= size << 24
    return compact


def _validated_target(nbits: int, pow_limit: int) -> int:
    decoded = decode_compact(nbits)
    if decoded.negative or decoded.overflow or decoded.value == 0:
        raise ValueError("previous nBits is not a valid positive target")
    if decoded.value > pow_limit:
        raise ValueError("previous target exceeds proof-of-work limit")
    return decoded.value


def calculate_next_work_required(
    last_nbits: int,
    first_block_time: int,
    last_block_time: int,
    *,
    target_timespan: int = TARGET_TIMESPAN,
    pow_limit: int = POW_LIMIT,
) -> int:
    """Bitcoin-mainnet-style retarget calculation (no min-difficulty exception)."""
    if target_timespan <= 0:
        raise ValueError("target_timespan must be positive")
    if pow_limit <= 0:
        raise ValueError("pow_limit must be positive")
    if not all(isinstance(t, int) and not isinstance(t, bool) for t in (first_block_time, last_block_time)):
        raise ValueError("block timestamps must be integers")

    actual_timespan = last_block_time - first_block_time
    actual_timespan = max(target_timespan // 4, min(actual_timespan, target_timespan * 4))

    old_target = _validated_target(last_nbits, pow_limit)
    new_target = (old_target * actual_timespan) // target_timespan
    new_target = min(new_target, pow_limit)
    return encode_compact(new_target)


def get_next_work_required(
    last_height: int,
    last_nbits: int,
    first_block_time: int,
    last_block_time: int,
    *,
    adjustment_interval: int = DIFFICULTY_ADJUSTMENT_INTERVAL,
    target_timespan: int = TARGET_TIMESPAN,
    pow_limit: int = POW_LIMIT,
) -> int:
    """Return required nBits for the block after last_height.

    The caller supplies the timestamp at height
    last_height - (adjustment_interval - 1), matching Bitcoin Core's retarget
    window. Non-boundary blocks must preserve the previous block's nBits.
    """
    if not isinstance(last_height, int) or isinstance(last_height, bool) or last_height < 0:
        raise ValueError("last_height must be a non-negative integer")
    if adjustment_interval <= 0:
        raise ValueError("adjustment_interval must be positive")
    if target_timespan <= 0 or target_timespan // adjustment_interval <= 0:
        raise ValueError("target_timespan / adjustment_interval must be positive")

    next_height = last_height + 1
    if next_height % adjustment_interval != 0:
        return last_nbits

    return calculate_next_work_required(
        last_nbits,
        first_block_time,
        last_block_time,
        target_timespan=target_timespan,
        pow_limit=pow_limit,
    )
