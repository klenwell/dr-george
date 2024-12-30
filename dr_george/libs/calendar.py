from datetime import datetime, date, timedelta


LEAP_DAY_NUM = 60


def date_str_to_date(date_str, date_format):
    return datetime.strptime(date_str, date_format).date()


def abs_day_nums_in_year():
    return range(1, 367)


def abs_day_num_to_date(year, abs_day_num):
    # Leap Year
    if year_has_leap_day(year):
        return day_of_year_to_date(year, abs_day_num)

    # Non-Leap Year
    if abs_day_num < LEAP_DAY_NUM:
        day_num = abs_day_num
    elif abs_day_num == LEAP_DAY_NUM:
        return None
    else:
        day_num = abs_day_num - 1

    return day_of_year_to_date(year, day_num)


def days_in_year(year):
    return 366 if year_has_leap_day(year) else 365


def year_has_leap_day(year):
    leap_day_date = day_of_year_to_date(year, LEAP_DAY_NUM)
    return leap_day_date.month == 2


def day_of_year_to_date(year, day_num):
    return date(year, 1, 1) + timedelta(days=day_num - 1)


def date_to_abs_day_num(date):
    rel_day_num = int(date.strftime('%j'))

    if year_has_leap_day(date.year):
        return rel_day_num

    if rel_day_num < LEAP_DAY_NUM:
        return rel_day_num
    else:
        return rel_day_num + 1
