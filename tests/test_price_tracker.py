"""Tests for the price parsing and threshold handling."""
import os
import sys

import pytest

# The module validates configuration at import time and exits if EMAIL_PASSWORD
# is absent, so it has to be present before the import below.
os.environ.setdefault('EMAIL_PASSWORD', 'test-password-not-used')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import price_tracker  # noqa: E402


class TestParsePrice:
    @pytest.mark.parametrize(
        ('raw', 'expected'),
        [
            ('1299', 1299.0),
            ('1,299', 1299.0),
            ('1,299.50', 1299.5),
            ('12,34,567', 1234567.0),          # Indian digit grouping
            ('₹1,299.00', 1299.0),
            ('1299.', 1299.0),
            ('  1,299.50  ', 1299.5),
        ],
    )
    def test_parses_real_price_strings(self, raw, expected):
        assert price_tracker.parse_price(raw) == expected

    @pytest.mark.parametrize('raw', ['', None, 'Currently unavailable', 'N/A', '---'])
    def test_returns_none_when_there_is_no_number(self, raw):
        assert price_tracker.parse_price(raw) is None


class TestResolveThreshold:
    @pytest.mark.parametrize(
        ('raw', 'expected'),
        [(500000.0, 500000.0), (500000, 500000.0), ('500000', 500000.0), (0, 0.0), (-5, -5.0)],
    )
    def test_accepts_numbers_and_numeric_strings(self, raw, expected):
        assert price_tracker.resolve_threshold(raw) == expected

    def test_a_missing_threshold_is_not_infinity(self):
        """Regression: the default was float('inf').

        `price < float('inf')` is true for every price, so a config without
        price_threshold emailed an alert on every run, with the message reading
        "below the threshold (Rs.inf)".
        """
        assert price_tracker.resolve_threshold(None) is None

    @pytest.mark.parametrize('raw', ['', 'cheap', [], {}, float('inf'), float('-inf'), float('nan')])
    def test_rejects_values_that_cannot_act_as_a_threshold(self, raw):
        assert price_tracker.resolve_threshold(raw) is None

    def test_a_resolved_threshold_does_not_fire_on_every_price(self):
        threshold = price_tracker.resolve_threshold(500000.0)
        assert 499.0 < threshold
        assert 600000.0 >= threshold
