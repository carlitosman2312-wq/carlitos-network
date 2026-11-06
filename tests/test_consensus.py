import unittest

from src.carlitos_consensus import (
    COIN,
    DIFFICULTY_ADJUSTMENT_INTERVAL,
    HALVING_INTERVAL,
    INITIAL_SUBSIDY,
    POW_LIMIT,
    POW_LIMIT_COMPACT,
    TARGET_TIMESPAN,
    block_subsidy,
    calculate_next_work_required,
    decode_compact,
    encode_compact,
    get_next_work_required,
)


class IssuanceTests(unittest.TestCase):
    def test_genesis_has_no_reward(self):
        self.assertEqual(block_subsidy(0), 0)

    def test_first_era_boundaries(self):
        self.assertEqual(block_subsidy(1), 100 * COIN)
        self.assertEqual(block_subsidy(HALVING_INTERVAL), 100 * COIN)
        self.assertEqual(block_subsidy(HALVING_INTERVAL + 1), 50 * COIN)
        self.assertEqual(block_subsidy(2 * HALVING_INTERVAL), 50 * COIN)
        self.assertEqual(block_subsidy(2 * HALVING_INTERVAL + 1), 25 * COIN)

    def test_integer_dust_is_not_reissued(self):
        self.assertEqual(block_subsidy(34 * HALVING_INTERVAL + 1), 0)

    def test_invalid_height_is_rejected(self):
        for height in (-1, 1.5, True):
            with self.subTest(height=height):
                with self.assertRaises(ValueError):
                    block_subsidy(height)


class CompactTargetTests(unittest.TestCase):
    def test_bitcoin_mainnet_pow_limit_encoding(self):
        self.assertEqual(encode_compact(POW_LIMIT), POW_LIMIT_COMPACT)
        decoded = decode_compact(POW_LIMIT_COMPACT)
        self.assertEqual(decoded.value, POW_LIMIT)
        self.assertFalse(decoded.negative)
        self.assertFalse(decoded.overflow)

    def test_compact_sign_and_overflow_are_reported(self):
        self.assertTrue(decode_compact(0x1D80FFFF).negative)
        self.assertTrue(decode_compact(0x23010000).overflow)

    def test_zero_target_cannot_be_encoded(self):
        with self.assertRaises(ValueError):
            encode_compact(0)


class DifficultyTests(unittest.TestCase):
    def setUp(self):
        self.old_target = POW_LIMIT // 16
        self.old_bits = encode_compact(self.old_target)

    def test_no_change_between_adjustment_boundaries(self):
        got = get_next_work_required(
            last_height=2014,
            last_nbits=self.old_bits,
            first_block_time=0,
            last_block_time=TARGET_TIMESPAN,
        )
        self.assertEqual(got, self.old_bits)

    def test_boundary_with_exact_target_timespan_preserves_target(self):
        got = get_next_work_required(
            last_height=DIFFICULTY_ADJUSTMENT_INTERVAL - 1,
            last_nbits=self.old_bits,
            first_block_time=100,
            last_block_time=100 + TARGET_TIMESPAN,
        )
        self.assertEqual(got, self.old_bits)

    def test_fast_period_is_clamped_to_one_quarter(self):
        got = calculate_next_work_required(self.old_bits, 100, 101)
        expected = encode_compact(self.old_target // 4)
        self.assertEqual(got, expected)

    def test_slow_period_is_clamped_to_four_times(self):
        got = calculate_next_work_required(
            self.old_bits, 100, 100 + TARGET_TIMESPAN * 10
        )
        expected = encode_compact(self.old_target * 4)
        self.assertEqual(got, expected)

    def test_result_is_capped_at_pow_limit(self):
        got = calculate_next_work_required(POW_LIMIT_COMPACT, 100, 100 + TARGET_TIMESPAN * 4)
        self.assertEqual(got, POW_LIMIT_COMPACT)

    def test_non_boundary_does_not_retarget(self):
        # Height 2015 is a retarget boundary for the *next* block; height 2014 is not.
        self.assertEqual(
            get_next_work_required(2014, POW_LIMIT_COMPACT, 0, TARGET_TIMESPAN),
            POW_LIMIT_COMPACT,
        )


if __name__ == "__main__":
    unittest.main()
