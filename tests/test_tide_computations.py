import datetime

import pytest

from src.tide_computations import generate_random_time_between_tides
from src.tide_tables import TideHeight, TideDay


@pytest.fixture
def setup_tide_day():
	# Create 4 tide heights, 1 or 2 minutes apart
	tide_heights = [
		TideHeight(time=datetime.time(12, 0), height=1.0, life_cycle=TideHeight.LW),
		TideHeight(time=datetime.time(12, 1), height=2.0, life_cycle=TideHeight.HW),
		TideHeight(time=datetime.time(12, 3), height=1.5, life_cycle=TideHeight.LW),
		TideHeight(time=datetime.time(12, 4), height=2.5, life_cycle=TideHeight.HW),
	]
	tide_day = TideDay(tide_date=datetime.date.today(), heights=tide_heights)
	return [tide_day]


def test_random_time_generation(setup_tide_day):
	tide_days = setup_tide_day
	day_number = 1
	tide_number = 1  # Testing between the first and second tide

	generated_time = generate_random_time_between_tides(
		tide_days=tide_days,
		day_number=day_number,
		tide_number=tide_number
	)

	# The expected time range is between 12:00 and 12:01
	start_time = datetime.datetime.combine(datetime.date.today(), datetime.time(12, 0))
	end_time = datetime.datetime.combine(datetime.date.today(), datetime.time(12, 1))
	generated_datetime = datetime.datetime.combine(datetime.date.today(), generated_time)

	assert start_time < generated_datetime < end_time, "Generated time is not within the expected range."
