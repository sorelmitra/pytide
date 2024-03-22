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


class TideTimePosition:
	"""
	Represents the position of a tide time in relation to a given time.

	Attributes:
	- time: `datetime.time` object representing the tide time.
	- day_number: The day number in the tide_days array (1-based) of the tide time.
	- tide_number: The tide number within the day (1-based) of the tide time.
	"""

	def __init__(self, *, time, day_number, tide_number):
		self.time = time
		self.day_number = day_number
		self.tide_number = tide_number


def find_closest_high_water(tide_days, day_number, given_time):
	min_time_diff = datetime.timedelta.max
	closest_hw_time = TideTimePosition(
		time=None, day_number=None, tide_number=None)
	day_index = day_number - 1

	# Helper function to update the closest HW tide based on a new candidate
	def update_closest_hw(*, candidate_time, candidate_day_number, candidate_tide_number, day_step):
		nonlocal closest_hw_time, min_time_diff
		day_of_reference = datetime.date.today()
		if day_step < 0:
			day_of_reference -= datetime.timedelta(days=1)
		elif day_step > 0:
			day_of_reference += datetime.timedelta(days=1)
		candidate_datetime = datetime.datetime.combine(day_of_reference, candidate_time)
		given_datetime = datetime.datetime.combine(datetime.date.today(), given_time)
		time_diff = abs(candidate_datetime - given_datetime)
		print(f"Candidate: {candidate_datetime}, given: {given_datetime}, time diff: {time_diff}")

		if time_diff < min_time_diff:
			min_time_diff = time_diff
			closest_hw_time.time = candidate_time
			closest_hw_time.day_number = candidate_day_number
			closest_hw_time.tide_number = candidate_tide_number
			print('Chosen')

	# Search for the closest HW tide in the current, previous, and next day
	for index_offset in (0, -1, 1):
		current_day_index = day_index + index_offset
		if 0 <= current_day_index < len(tide_days):
			n = len(tide_days[current_day_index].heights)
			if index_offset < 0:
				start = n - 1
				stop = -1
				step = -1
			else:
				start = 0
				stop = n
				step = 1
			for k in range(start, stop, step):
				tide = tide_days[current_day_index].heights[k]
				tide_days[current_day_index].print()
				if tide.type == TideHeight.HW:
					update_closest_hw(
						candidate_time=tide.time, candidate_day_number=current_day_index + 1,
						candidate_tide_number=tide_days[current_day_index].heights.index(tide) + 1,
						day_step=index_offset)

	if closest_hw_time.time is not None:
		return closest_hw_time
	else:
		raise ValueError("No high water found in the provided data.")
