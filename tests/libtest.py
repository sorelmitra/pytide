from src.tide_tables import TideHeight


def systest_get_hw(*, tide_days, day_number, first):
	index = day_number - 1
	high_waters = [t for t in tide_days[index].heights if t.type == TideHeight.HW]
	if first:
		return high_waters[0].height
	return high_waters[len(high_waters) - 1].height


def systest_get_lw(*, tide_days, day_number, first):
	index = day_number - 1
	low_waters = [t for t in tide_days[index].heights if t.type == TideHeight.LW]
	if first:
		return low_waters[0].height
	return low_waters[len(low_waters) - 1].height


def systest_get_first_ht(*, tide_days, day_number):
	index = day_number - 1
	hw = [t for t in tide_days[index].heights if t.type == TideHeight.HW][0]
	lw = [t for t in tide_days[index].heights if t.type == TideHeight.LW][0]
	return hw.height - lw.height


def systest_get_last_ht(*, tide_days, day_number):
	index = day_number - 1
	high_waters = [t for t in tide_days[index].heights if t.type == TideHeight.HW]
	hw = high_waters[len(high_waters) - 1]
	low_waters = [t for t in tide_days[index].heights if t.type == TideHeight.LW]
	lw = low_waters[len(low_waters) - 1]
	return hw.height - lw.height


def systest_get_mean_ht(*, tide_days, day_number):
	first_springs_height = systest_get_first_ht(tide_days=tide_days, day_number=day_number)
	last_springs_height = systest_get_last_ht(tide_days=tide_days, day_number=day_number)
	return (first_springs_height + last_springs_height) / 2
