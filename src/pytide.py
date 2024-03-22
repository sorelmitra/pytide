import datetime
import random

from src.tide_computations import generate_random_time_between_tides, find_closest_high_water, \
	timedelta_to_twelve_based_tide_hours
from src.tide_model import semidiurnal_tide, NEAP_MAX
from src.tide_plot import plot_tide
from src.tide_tables import generate_tide_days, reset_day, compute_springs_mean, compute_max_hw, compute_neaps_mean, \
	compute_max_lw

if __name__ == '__main__':
	cycle_length = random.randint(7, 9)
	start_date = reset_day() + datetime.timedelta(hours=3, minutes=10)
	tide_days = generate_tide_days(start_date=start_date, cycle_length=cycle_length,
								   time_delta=datetime.timedelta(hours=6, minutes=20), min_water_factor=2,
								   max_water_factor=5)

	print(f"Month: {start_date.strftime('%B')}, generating a full cycle of {cycle_length} days length")
	print()
	[tide.print() for tide in tide_days]

	given_time = generate_random_time_between_tides(
		tide_days=tide_days, day_number=4, tide_number=2)
	closest_hw = find_closest_high_water(
		tide_days=tide_days, day_number=4, given_time=given_time)
	tide_day = tide_days[3]
	tide_value = tide_day.heights[closest_hw.tide_number - 1]
	twelve_based_time = timedelta_to_twelve_based_tide_hours(closest_hw.hw_diff)
	tide_height = tide_value.compute_height(twelve_based_time)
	tide_height_str = f"{tide_height:.1f} m"
	print(f"On {tide_day.date.strftime('%B %d')}, at {given_time.strftime('%H%M')}, tide height is {tide_height_str}, 12-based tide-hour {twelve_based_time:.1f}")
	closest_hw.print()

	plot_tide(
		springs_tide_func=(semidiurnal_tide()),
		springs_mean=compute_springs_mean(tide_days),
		max_high_water=compute_max_hw(tide_days) + 1,
		neaps_tide_func=(semidiurnal_tide(neap_factor=NEAP_MAX)),
		neaps_mean=compute_neaps_mean(tide_days),
		max_low_water=compute_max_lw(tide_days) + 1
	)

