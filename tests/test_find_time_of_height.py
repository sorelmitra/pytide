import datetime

import pytest

from src.tide_computations import determine_water_height_intervals, TideConstraints
from src.tide_model import semidiurnal_tide
from src.tide_tables import TideDay, TideHeight


@pytest.fixture
def sample_tide_days():
	compute_height = semidiurnal_tide(
		min_water_factor=2,
		max_water_factor=5,
		neap_factor=3.82
	)
	return [
		TideDay(
			tide_date=datetime.date(2024, 1, 1),
			heights=[
				TideHeight(
					time=datetime.time(3, 40), height=2.6,
					life_cycle=TideHeight.LW,
				),
				TideHeight(
					time=datetime.time(10, 0), height=6.4,
					life_cycle=TideHeight.HW, compute_height=compute_height,
				),
				TideHeight(
					time=datetime.time(16, 20), height=2.7,
					life_cycle=TideHeight.LW,
				),
				TideHeight(
					time=datetime.time(22, 40), height=6.4,
					life_cycle=TideHeight.HW, compute_height=compute_height
				),
			],
		),
		TideDay(
			tide_date=datetime.date(2024, 1, 2),
			heights=[
				TideHeight(
					time=datetime.time(4, 50), height=2.6,
					life_cycle=TideHeight.LW,
				),
				TideHeight(
					time=datetime.time(11, 10), height=6.4,
					life_cycle=TideHeight.HW, compute_height=compute_height,
				),
				TideHeight(
					time=datetime.time(17, 30), height=2.7,
					life_cycle=TideHeight.LW,
				),
				TideHeight(
					time=datetime.time(23, 50), height=6.4,
					life_cycle=TideHeight.HW, compute_height=compute_height
				),
			],
		),
	]


def test_find_interval_of_minimum_water_height(sample_tide_days):
	intervals = determine_water_height_intervals(
		tide_days=sample_tide_days, day_number=2, tide_number=1,
		constraint=TideConstraints.MIN, height_to_find=4.3)
	assert len(intervals) == 1
	interval = intervals[0]
	assert interval.start.day_number == 2
	assert interval.start.time.time() == datetime.time(7, 28)
	assert interval.end.day_number == 2
	assert interval.end.time.time() == datetime.time(14, 51)


def test_find_interval_of_minimum_water_height_span_next_day(sample_tide_days):
	intervals = determine_water_height_intervals(
		tide_days=sample_tide_days, day_number=1, tide_number=3,
		constraint=TideConstraints.MIN, height_to_find=4.3)
	assert len(intervals) == 1
	interval = intervals[0]
	assert interval.start.day_number == 1
	assert interval.start.time.time() == datetime.time(18, 58)
	assert interval.end.day_number == 2
	assert interval.end.time.time() == datetime.time(2, 8)


def test_find_interval_of_minimum_water_height_hw_is_last(sample_tide_days):
	intervals = determine_water_height_intervals(
		tide_days=sample_tide_days, day_number=2, tide_number=3,
		constraint=TideConstraints.MIN, height_to_find=4.3)
	assert len(intervals) == 1
	interval = intervals[0]
	assert interval.start.day_number == 2
	assert interval.start.time.time() == datetime.time(20, 8)
	assert interval.end.day_number == 3
	assert interval.end.time.time() == datetime.time(3, 31)
