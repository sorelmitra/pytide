import datetime

import pytest

from src.tide_computations import generate_random_time_between_tides
from src.tide_tables import TideHeight, TideDay


@pytest.fixture
def tide_days_setup():
	tide_day1 = TideDay(
		tide_date=datetime.date(2024, 1, 1),
		heights=[
			TideHeight(time=datetime.time(6, 0), height=1.0, life_cycle=TideHeight.LW),
			TideHeight(time=datetime.time(12, 0), height=2.0, life_cycle=TideHeight.HW),
			TideHeight(time=datetime.time(18, 0), height=1.5, life_cycle=TideHeight.LW)
		]
	)
	tide_day2 = TideDay(
		tide_date=datetime.date(2024, 1, 2),
		heights=[
			TideHeight(time=datetime.time(0, 30), height=2.5, life_cycle=TideHeight.HW),
			TideHeight(time=datetime.time(6, 30), height=1.0, life_cycle=TideHeight.LW)
		]
	)
	return [tide_day1, tide_day2]


def test_normal_operation(tide_days_setup):
	generated_time = generate_random_time_between_tides(tide_days=tide_days_setup, day_number=1, tide_number=1)
	assert datetime.time(6, 0) < generated_time < datetime.time(12, 0)


def test_transition_to_next_day(tide_days_setup):
	generated_time = generate_random_time_between_tides(tide_days=tide_days_setup, day_number=1, tide_number=3)
	assert datetime.time(18, 0) < generated_time or generated_time < datetime.time(0, 30)


def test_last_tide_of_last_day(tide_days_setup):
	generated_time = generate_random_time_between_tides(tide_days=tide_days_setup, day_number=2, tide_number=2)
	assert datetime.time(6, 30) < generated_time <= datetime.time(23, 59)
