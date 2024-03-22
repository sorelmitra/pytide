import datetime
import random

from src.tide_tables import TideHeight, TideDay


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


def timedelta_to_twelve_based_tide_hours(td):
	"""
	Converts a datetime.timedelta object to a floating point number representing tide hours.
	Tide hours run between 0 and 12, with 0 representing the first low water of the interval, 6 representing the high water, and 12 representing the second low water.

	Parameters:
	- td: datetime.timedelta object.

	Returns:
	- float: The number of tide 12-based hours represented by the timedelta, including fractional parts.
	"""
	total_seconds = td.total_seconds()
	hours = total_seconds / 3600  # Convert seconds to hours

	# Convert to 12-based tide hours
	hours += 6
	if hours < 0:
		hours += 6
	if hours > 12:
		hours -= 12
	return hours


class TideTimePosition:
	"""
	Represents the position of a tide time in relation to a given time.

	Attributes:
	- time: `datetime.time` object representing the tide time.
	- day_number: The day number in the tide_days array (1-based) of the tide time.
	- tide_number: The tide number within the day (1-based) of the tide time.
	"""

	def __init__(self, *, time, day_number, tide_number, hw_diff):
		self.time = time
		self.day_number = day_number
		self.tide_number = tide_number
		self.hw_diff = hw_diff

	def print(self):
		print(f"Closest HW is at {self.time.strftime('%H%M')}, tide hour {self.get_hw_hour_string()}, tide number: {self.tide_number}")

	def get_hw_hour_string(self):
		total_seconds = int(self.hw_diff.total_seconds())
		hours = total_seconds // 3600  # Divide by 3600 to get hours
		minutes = (total_seconds % 3600) // 60  # Use modulus by 3600 to get remaining seconds, then divide by 60 to get minutes
		if minutes > 30:
			hours += 1
		sign = ''
		if hours > 0:
			sign = '+'
		hours_str = f"{sign}{hours}"
		if hours == 0:
			hours_str = ''
		return f"HW{hours_str}"


def find_closest_high_water(*, tide_days, day_number, given_time):
	min_time_diff = datetime.timedelta.max
	closest_hw_time = TideTimePosition(
		time=None, day_number=None, tide_number=None, hw_diff=None)
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
		time_diff = given_datetime - candidate_datetime
		abs_time_diff = abs(time_diff)
		# print('[DEBUG]', f"Candidate: {candidate_datetime}, given: {given_datetime}, time diff: {abs_time_diff}")

		if abs_time_diff < min_time_diff:
			min_time_diff = abs_time_diff
			closest_hw_time.time = candidate_time
			closest_hw_time.day_number = candidate_day_number
			closest_hw_time.tide_number = candidate_tide_number
			closest_hw_time.hw_diff = time_diff
			# print('[DEBUG]', 'Chosen')

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
				# print('[DEBUG]')
				# tide_days[current_day_index].print()
				if tide.type == TideHeight.HW:
					update_closest_hw(
						candidate_time=tide.time, candidate_day_number=current_day_index + 1,
						candidate_tide_number=tide_days[current_day_index].heights.index(tide) + 1,
						day_step=index_offset)

	if closest_hw_time.time is not None:
		return closest_hw_time
	else:
		raise ValueError("No high water found in the provided data.")


class TideConstraints:
	MIN = 'minimum',
	MAX = 'maximum'

	def __init__(self, day_number=0, time=datetime.datetime.now()):
		self.day_number = day_number
		self.time = time

class TideInterval:
	def __init__(self, start=TideConstraints(), end=TideConstraints()):
		self.start = start
		self.end = end


def find_previous_tide(*, tide_days=[TideDay()], day_number, tide_number):
	"""
	Finds the previous high water (HW) or low water (LW) tide in a list of TideDay objects.

	Parameters:
	- tide_days: List of TideDay objects.
	- day_number: The day number (1-based index) to start the search from.
	- tide_number: The tide number (1-based index) within the start day to start the search from.

	Returns:
	- A tuple (day_number, tide_number, tide_type) indicating the day and tide number of the previous HW or LW,
	  and the type of tide (HW or LW), or None if not found.
	"""

	# Adjust to 0-based index for iteration
	day_index = day_number - 1
	tide_index = tide_number - 2  # Start search from the tide before the given tide_number

	while day_index >= 0:
		tide_day = tide_days[day_index]
		while tide_index >= 0:
			tide = tide_day.heights[tide_index]
			if tide.type in [TideHeight.HW, TideHeight.LW]:
				return tide, tide_index + 1  # Convert back to 1-based index for result
			tide_index -= 1
		# Move to the previous day and start from the last tide of that day
		day_index -= 1
		if day_index >= 0:  # Check to prevent index error on the last iteration
			tide_index = len(tide_days[day_index].heights) - 1

	return None  # Return None if no previous HW or LW is found


def find_next_tide(*, tide_days=[TideDay()], day_number, tide_number):
	"""
	Finds the next high water (HW) or low water (LW) tide in a list of TideDay objects.

	Parameters:
	- tide_days: List of TideDay objects.
	- day_number: The day number (1-based index) to start the search from.
	- tide_number: The tide number (1-based index) within the start day to start the search from.

	Returns:
	- A tuple (day_number, tide_number, tide_type) indicating the day and tide number of the next HW or LW,
	  and the type of tide (HW or LW), or None if not found.
	"""
	day_index = day_number - 1  # Convert to 0-based index for iteration
	tide_index = tide_number  # Start search from the tide immediately after the given tide_number

	while day_index < len(tide_days):
		tide_day = tide_days[day_index]
		while tide_index < len(tide_day.heights):
			tide = tide_day.heights[tide_index]
			if tide.type in [TideHeight.HW, TideHeight.LW]:
				return tide, tide_index + 1  # Convert back to 1-based index for result
			tide_index += 1
		# Move to the next day and start from the first tide of that day
		day_index += 1
		tide_index = 0

	return None, 0  # Return None if no next HW or LW is found


def find_height_time_between_tides(*, height_to_find,
								   first_tide=TideHeight(), second_tide=TideHeight(),
								   hw_is_first):
	start_time = datetime.datetime.combine(datetime.date.today(), first_tide.time)
	end_time = datetime.datetime.combine(datetime.date.today(), second_tide.time)

	tide_diff = end_time - start_time

	start_time_12_hours = timedelta_to_twelve_based_tide_hours(tide_diff)
	end_time_12_hours = 6
	if hw_is_first:
		start_time_12_hours = 6
		end_time_12_hours = timedelta_to_twelve_based_tide_hours(tide_diff)

	hw = second_tide
	if hw_is_first:
		hw = first_tide

	start_height = hw.compute_height(start_time_12_hours)
	end_height = hw.compute_height(end_time_12_hours)

	print('[DEBUG]', f"First tide")
	first_tide.print()
	print('[DEBUG]', f"Second tide")
	second_tide.print()

	print('[DEBUG]', f"Start time: {start_time}, end time: {end_time}")
	print('[DEBUG]',
		  f"12-hours-based: Start time: {start_time_12_hours:.1f}, end time: {end_time_12_hours:.1f}")
	print('[DEBUG]', f"Start height: {start_height:.1f}, end height: {end_height:.1f}")

	while (end_time - start_time) > datetime.timedelta(minutes=1):  # Precision threshold
		mid_time = start_time + (end_time - start_time) / 2
		mid_time_12_hours = start_time_12_hours + (end_time_12_hours - start_time_12_hours) / 2
		print('[DEBUG]',
			  f"Start time: {start_time}, end time: {end_time}, mid time: {mid_time}")
		print('[DEBUG]',
			  f"12-hours-based start time: {start_time_12_hours:.1f}, end time: {end_time_12_hours:.1f}, mid time: {mid_time_12_hours:.1f}")
		mid_height = hw.compute_height(mid_time_12_hours)
		print('[DEBUG]',
			  f"Start height: {start_height:.1f}, end height: {end_height:.1f}, mid height: {mid_height:.1f}")

		if (mid_height < height_to_find and start_height < end_height) or (
				mid_height > height_to_find and start_height > end_height):
			start_time = mid_time
			start_time_12_hours = mid_time_12_hours
		else:
			end_time = mid_time
			end_time_12_hours = mid_time_12_hours

	# Reset precision to minutes
	start_time = start_time.replace(second=0, microsecond=0)

	return start_time


def determine_water_height_intervals(constraint=TideConstraints.MIN,
									 tide_days=[TideDay()], day_number=0,
									 height_to_find=0.0):
	hw, hw_tide_number = find_next_tide(
		tide_days=tide_days, day_number=day_number, tide_number=1)
	previous_tide, _ = find_previous_tide(
		tide_days=tide_days, day_number=day_number, tide_number=hw_tide_number)
	next_tide, _ = find_next_tide(
		tide_days=tide_days, day_number=day_number, tide_number=hw_tide_number)

	if hw is None:
		raise ValueError("No high water found in the provided data.")
	if previous_tide is None and next_tide is None:
		raise ValueError("No previous or next tide found in the provided data.")

	if next_tide is None:
		next_tide = hw
	if previous_tide is None:
		previous_tide = hw

	# Find the first time corresponding to the given height
	start_time = find_height_time_between_tides(
		height_to_find=height_to_find, first_tide=previous_tide, second_tide=hw,
		hw_is_first=False)

	# Find the second time corresponding to the given height
	end_time = find_height_time_between_tides(
		height_to_find=height_to_find, first_tide=hw, second_tide=next_tide,
		hw_is_first=True)

	return [
		TideInterval(
			start=TideConstraints(day_number=day_number, time=start_time),
			end=TideConstraints(day_number=day_number, time=end_time)
		)
	]


