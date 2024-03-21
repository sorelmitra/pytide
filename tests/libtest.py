from src.tide_tables import TideHeight


def get_last_hw(*, tide_days, day_number):
	index = day_number - 1
	high_waters = [t for t in tide_days[index].heights if t.type == TideHeight.HW]
	return high_waters[len(high_waters) - 1].height


def get_first_lw(*, tide_days, day_number):
	index = day_number - 1
	low_waters = [t for t in tide_days[index].heights if t.type == TideHeight.LW]
	return low_waters[0].height


def get_first_height(*, tide_days, day_number):
	index = day_number - 1
	hw = [t for t in tide_days[index].heights if t.type == TideHeight.HW][0]
	lw = [t for t in tide_days[index].heights if t.type == TideHeight.LW][0]
	return hw.height - lw.height


def get_last_height(*, tide_days, day_number):
	index = day_number - 1
	high_waters = [t for t in tide_days[index].heights if t.type == TideHeight.HW]
	hw = high_waters[len(high_waters) - 1]
	low_waters = [t for t in tide_days[index].heights if t.type == TideHeight.LW]
	lw = low_waters[len(low_waters) - 1]
	return hw.height - lw.height

