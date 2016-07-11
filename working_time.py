from __future__ import print_function
import sys
from worklog import get_day_stats

SEP = '\t'

def get_hours_worked(day_stats):
    for day, stats in day_stats.items():
        time_at_lunch = hours_diff(stats['lunch_end'], stats['lunch_start'])
        if stats['is_lunch_business']:
            time_at_lunch = 0
        time_at_office = hours_diff(stats['end'], stats['start'])
        time_at_office += hours_diff(stats['extra_end'], stats['extra_start'])

        yield day, time_at_office - time_at_lunch

def hours_diff(end, start):
    if not end or not start:
        return 0
    diff = end - start
    return diff.total_seconds() / 3600

def get_headers():
    return ['date', 'hours']

def get_data(fn):
    day_stats = get_day_stats(fn)
    day_hours = get_hours_worked(day_stats)

    for day, hours in day_hours:
        yield day.strftime('%Y-%m-%d'), hours

if __name__ == '__main__':
    sep = SEP
    worklog = sys.argv[1]
    try:
        if sys.argv[1] == '-s':
            sep = sys.argv[2]
        worklog = sys.argv[3]
    except IndexError:
        pass

    print(sep.join(get_headers()))
    for data in get_data(worklog):
        print(sep.join(str(i) for i in data))
