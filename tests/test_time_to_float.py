import datetime

import pytest

from src.tide_computations import time_to_float


def test_midnight():
	assert time_to_float(datetime.time(0, 0)) == 0.0


def test_noon():
	assert time_to_float(datetime.time(12, 0)) == 12.0


def test_half_past_midnight():
	assert time_to_float(datetime.time(0, 30)) == 0.5


def test_quarter_past_noon():
	assert time_to_float(datetime.time(12, 15)) == 12.25


def test_random_evening_time():
	assert time_to_float(datetime.time(18, 45)) == 18.75


def test_just_before_midnight():
	assert time_to_float(datetime.time(23, 59)) == pytest.approx(23.98, abs=0.1)


def test_boundary_minutes():
	# Tests minutes at lower and upper boundaries (0 and 59)
	assert time_to_float(datetime.time(5, 0)) == 5.0
	assert time_to_float(datetime.time(5, 59)) == pytest.approx(5.98, abs=0.1)


@pytest.mark.parametrize("hour,minute,expected", [
	(1, 0, 1.0),
	(2, 30, 2.5),
	(13, 45, 13.75),
	(23, 30, 23.5),
])
def test_various_times(hour, minute, expected):
	assert time_to_float(datetime.time(hour, minute)) == expected
