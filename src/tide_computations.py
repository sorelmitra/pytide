import datetime
import random

from src.tide_tables import TideHeight


def generate_random_time_between_tides(*, tide_days, day_number, tide_number):
	day_index = day_number - 1
	tide_index = tide_number - 1

	# Validate inputs
	if day_index >= len(tide_days) or day_index < 0:
		raise ValueError(f"day_number {day_number} is out of range.")
	tide_day = tide_days[day_index]

	if tide_index >= len(tide_day.heights) or tide_index < 0:
		raise ValueError(f"tide_number {tide_number} is out of range.")

	current_tide = tide_day.heights[tide_index]

	# Handle the last tide of the day
	if tide_index + 1 < len(tide_day.heights):
		next_tide = tide_day.heights[tide_index + 1]
	else:
		next_tide = TideHeight(time=datetime.time(23, 59))

	current_tide_datetime = datetime.datetime.combine(
		tide_day.date, current_tide.time)  # Assuming tide_day.date exists
	next_tide_datetime = datetime.datetime.combine(
		tide_day.date, next_tide.time)  # Adjust accordingly

	random_datetime = current_tide_datetime + (
				next_tide_datetime - current_tide_datetime) * random.random()
	return random_datetime.time()


def time_to_float(t):
	"""
	Converts a `datetime.time` object to a floating point number representing the hour since midnight.
	Seconds and microseconds are ignored.

	Parameters:
	- t: `datetime.time` object.

	Returns:
	- float: The hour since midnight as a floating point number.
	"""
	# Extract hours and minutes
	hours = t.hour
	minutes = t.minute

	# Convert the time to a floating point number
	# Hours + (Minutes / 60) to convert minutes to a fraction of an hour
	return hours + minutes / 60.0
