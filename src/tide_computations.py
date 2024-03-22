import datetime
import random

from src.tide_tables import TideHeight


def generate_random_time_between_tides(*, tide_days, day_number, tide_number):
	day_index = day_number - 1
	tide_index = tide_number - 1

	# Retrieve the specific TideDay
	tide_day = tide_days[day_index]
	# Retrieve the tide height entry
	current_tide = tide_day.heights[tide_index]

	# Determine next tide
	if tide_index + 1 < len(tide_day.heights):
		# The next tide is later the same day
		next_tide = tide_day.heights[tide_index + 1]
		next_tide_day = tide_day
	elif day_index + 1 < len(tide_days):
		# The next tide is the first tide of the next day
		next_tide_day = tide_days[day_index + 1]
		next_tide = next_tide_day.heights[0]
	else:
		# If it's the last tide of the last day in the array, use a default end time (e.g., 23:59)
		next_tide_day = tide_day  # No next day, so default to the current day
		next_tide = TideHeight(time=datetime.time(23, 59))

	# Convert tide times to datetime.datetime objects for easy manipulation
	current_tide_datetime = datetime.datetime.combine(tide_day.date, current_tide.time)
	next_tide_datetime = datetime.datetime.combine(next_tide_day.date, next_tide.time)

	# Generate a random datetime between the current tide and the next
	if next_tide_datetime > current_tide_datetime:
		random_datetime = current_tide_datetime + (
					next_tide_datetime - current_tide_datetime) * random.random()
	else:
		# If next tide datetime is not greater (due to defaulting to 23:59), adjust logic as needed
		# For simplicity, we default to current_tide_datetime for now
		random_datetime = current_tide_datetime

	# Return the time part of the random datetime
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
