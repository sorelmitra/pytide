import datetime

from src.tide_model import NEAP_MAX
from src.tide_tables import reset_day, TideHeight, generate_tide_days, \
	compute_max_hw, compute_springs_mean, \
	compute_max_lw, compute_neaps_mean
from tests.libtest import systest_get_hw, systest_get_lw, \
	systest_get_mean_ht, check_water_levels


def test_generate_two_neaps_two_springs_with_variations():
	delta = datetime.timedelta(hours=6, minutes=20)
	tide_days = generate_tide_days(
		start_date=(reset_day() + datetime.timedelta(hours=3, minutes=10)),
		heights_count=0,
		days_count=30,
		cycle_length=8, time_delta=delta,
		go_towards_springs=False,
		start_days_after_neaps=6)
	assert len(tide_days) == 30

	first_neap_level = tide_days[0].neap_level

	# We start from the seventh day after neaps
	offset_neap_level = NEAP_MAX - 6 * (NEAP_MAX / 17)
	assert first_neap_level - offset_neap_level < 0.1

	# Tide height range should decrease until reaching first Neaps
	old_neap_level = first_neap_level - 1
	for index in range(0, 6):
		tide_day = tide_days[index]

		# check that neap levels are increasing
		print(
			f"Neap level for day {tide_day.date.day} is {tide_day.neap_level}")
		assert tide_day.neap_level > old_neap_level
		old_neap_level = tide_day.neap_level

		# check that high water levels are decreasing
		check_water_levels(tide_day=tide_day,
						   tide_life_cycle=TideHeight.HW,
						   predicate=lambda current, previous: current < previous - 0.04)

		# check that low water levels are increasing
		check_water_levels(tide_day=tide_day,
						   tide_life_cycle=TideHeight.LW,
						   predicate=lambda current, previous: current > previous + 0.01)

	# We have reached first Neaps
	# Above and below, we skip the tests for day 7 (tide_days[6])
	# because tide changes right in the middle of the day and our
	# check_water_levels function is not prepared to handle that
	middle_neap_level = tide_days[6].neap_level
	assert middle_neap_level == NEAP_MAX

	# From the first Neaps, tide height range should increase
	for index in range(7, 14):
		tide_day = tide_days[index]

		# check that neap levels are decreasing
		print(
			f"Neap level for day {tide_day.date.day} is {tide_day.neap_level}")
		assert tide_day.neap_level < old_neap_level
		old_neap_level = tide_day.neap_level

		# check that high water levels are increasing
		check_water_levels(tide_day=tide_day,
						   tide_life_cycle=TideHeight.HW,
						   predicate=lambda current, previous: current > previous + 0.04)

		# check that low water levels are decreasing
		check_water_levels(tide_day=tide_day,
						   tide_life_cycle=TideHeight.LW,
						   predicate=lambda current, previous: current < previous - 0.008)

	# We have reached first Springs
	middle_neap_level = tide_days[14].neap_level
	assert middle_neap_level == 0

	# Tide height range should again decrease until reaching second Neaps
	old_neap_level = first_neap_level - 1
	for index in range(15, 21):
		tide_day = tide_days[index]

		# check that neap levels are increasing
		print(
			f"Neap level for day {tide_day.date.day} is {tide_day.neap_level}")
		assert tide_day.neap_level > old_neap_level
		old_neap_level = tide_day.neap_level

		# check that high water levels are decreasing
		check_water_levels(tide_day=tide_day,
						   tide_life_cycle=TideHeight.HW,
						   predicate=lambda current, previous: current < previous - 0.04)

		# check that low water levels are increasing
		check_water_levels(tide_day=tide_day,
						   tide_life_cycle=TideHeight.LW,
						   predicate=lambda current, previous: current > previous + 0.01)

	# We have reached second Neaps
	middle_neap_level = tide_days[22].neap_level
	assert middle_neap_level == NEAP_MAX

	# From the second Neaps, tide height range should increase again
	for index in range(23, len(tide_days)):
		tide_day = tide_days[index]

		# check that neap levels are decreasing
		print(
			f"Neap level for day {tide_day.date.day} is {tide_day.neap_level}")
		assert tide_day.neap_level < old_neap_level
		old_neap_level = tide_day.neap_level

		# check that high water levels are increasing
		check_water_levels(tide_day=tide_day,
						   tide_life_cycle=TideHeight.HW,
						   predicate=lambda current, previous: current > previous + 0.04)

		# check that low water levels are decreasing
		check_water_levels(tide_day=tide_day,
						   tide_life_cycle=TideHeight.LW,
						   predicate=lambda current, previous: current < previous - 0.008)

	# We have reached second Springs, at the end of the month
	middle_neap_level = tide_days[29].neap_level
	assert middle_neap_level == 0

	assert compute_max_hw(tide_days) == systest_get_hw(
		tide_days=tide_days, day_number=15, first=True)
	assert compute_max_lw(tide_days) == systest_get_lw(
		tide_days=tide_days, day_number=7, first=False)

	expected_springs_height = systest_get_mean_ht(tide_days=tide_days, day_number=15)
	assert abs(compute_springs_mean(tide_days) - expected_springs_height) < 0.1

	expected_neaps_height = systest_get_mean_ht(tide_days=tide_days, day_number=7)
	assert abs(compute_neaps_mean(tide_days) - expected_neaps_height) < 0.1
