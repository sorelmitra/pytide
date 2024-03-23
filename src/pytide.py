import argparse
import datetime
import random

from src.lib import set_log_level, LogLevel
from src.tide_computations import generate_random_time_between_tides, find_closest_high_water, \
	timedelta_to_twelve_based_tide_hours, determine_water_height_intervals, TideConstraints
from src.tide_model import semidiurnal_tide, NEAP_MAX
from src.tide_plot import plot_tide
from src.tide_tables import generate_tide_days, reset_day, compute_springs_mean, compute_max_hw, compute_neaps_mean, \
	compute_max_lw

if __name__ == '__main__':
	ap = argparse.ArgumentParser(
		description="PyTide: Generate realistic tide tables, curves.  "
					"Solve common tide problems")
	ap.add_argument("-v", help="Be more verbose, helps debugging problems")
	args = ap.parse_args()
	set_log_level(LogLevel.INFO)
	if args.v:
		set_log_level(LogLevel.DEBUG)

	cycle_length = random.randint(7, 9)
	start_date = reset_day() + datetime.timedelta(hours=3, minutes=10)
	tide_days = generate_tide_days(start_date=start_date, cycle_length=cycle_length,
								   time_delta=datetime.timedelta(hours=6, minutes=20), min_water_factor=2,
								   max_water_factor=5)

	print(f"Month: {start_date.strftime('%B')}, generating a full cycle of {cycle_length} days length")
	print()
	[tide.print() for tide in tide_days]

	day_number = 2
	given_time = generate_random_time_between_tides(
		tide_days=tide_days, day_number=day_number, tide_number=3)
	closest_hw = find_closest_high_water(
		tide_days=tide_days, day_number=day_number, given_time=given_time)
	tide_day = tide_days[day_number - 1]
	tide_value = tide_day.heights[closest_hw.tide_number - 1]
	twelve_based_time = timedelta_to_twelve_based_tide_hours(closest_hw.hw_diff)
	tide_height = tide_value.compute_height(twelve_based_time)
	tide_height_str = f"{tide_height:.1f} m"
	print(f"On {tide_day.date.strftime('%B %d')}, at {given_time.strftime('%H%M')}, tide height is {tide_height_str}, 12-based tide-hour {twelve_based_time:.1f}")
	closest_hw.print()

	intervals = determine_water_height_intervals(
		tide_days=tide_days, day_number=2, tide_number=3,
		constraint=TideConstraints.MIN, height_to_find=4.3)
	print(f"Intervals during which tide is at least 4.3 m:")
	[interval.print() for interval in intervals]

	plot_tide(
		springs_tide_func=(semidiurnal_tide()),
		springs_mean=compute_springs_mean(tide_days),
		max_high_water=compute_max_hw(tide_days) + 1,
		neaps_tide_func=(semidiurnal_tide(neap_factor=NEAP_MAX)),
		neaps_mean=compute_neaps_mean(tide_days),
		max_low_water=compute_max_lw(tide_days) + 1
	)

