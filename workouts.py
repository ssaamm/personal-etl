import collections
import datetime
import sys
from itertools import islice, groupby

from utils.common import gc
from utils.duration import Duration

from utils.math_utils import rolling_average

key = '1RzVbHFsIw6K9koiI9oGdWkhQmZrwUikfLIoNhvdlEs8'
sheet = gc.open_by_key(key).get_worksheet(0)

SEP = '\t'

Exercise = collections.namedtuple('Exercise', ['timestamp', 'exercise', 'duration', 'distance', 'sets', 'reps', 'weight'])

def get_raw_rows():
    all_cols = [sheet.col_values(ndx) for ndx in range(1, 9)]

    for row in islice(zip(*all_cols), 1, None):
        if all(not v for v in row):
            raise StopIteration

        try:
            latest_timestamp = parse_timestamp(row[0], row[1])
        except ValueError:
            pass

        float_values = [float(row[i]) if row[i] else 0.0 for i in range(4, 8)]
        try:
            duration = Duration.from_string(row[3])
        except ValueError:
            duration = Duration(0, 0, 0)
        yield Exercise(latest_timestamp, row[2], duration, *float_values)

def get_daily_summary():
    for date, exercises_grouped in groupby(get_raw_rows(), key=lambda t: t[0].date()):
        exercises = list(exercises_grouped)
        duration = sum(e.duration for e in exercises)
        distance = sum(e.distance for e in exercises)
        reps = sum(e.sets * e.reps for e in exercises)
        yield date, len(exercises), duration, distance, reps

def get_daily_did_i_workout():
    workouts = {date: (num_exercises, duration, distance, reps)
                for date, num_exercises, duration, distance, reps in get_daily_summary()}

    chrono_dates = list(sorted(workouts.keys()))
    first_day, last_day = min(chrono_dates), max(chrono_dates)

    days = (first_day + datetime.timedelta(days=i) for i in range(1, (last_day - first_day).days + 1))
    return [(d, d in workouts and any(workouts[d])) for d in days]

def get_workout_rolling_avg(days=7):
    did_workouts = get_daily_did_i_workout()
    numbers = [int(b) for d, b in did_workouts]
    for date_did_workout, avg in zip(did_workouts[days - 1:], rolling_average(numbers, window=days)):
        yield date_did_workout[0], avg


def get_headers():
    return 'date', 'pct_last_wk_worked_out'

def parse_timestamp(date, time):
    return datetime.datetime.strptime('{0} {1}'.format(date, time), '%Y-%m-%d %H:%M')

def get_data():
    for i in get_workout_rolling_avg():
        yield i

if __name__ == '__main__':
    sep = SEP
    try:
        if sys.argv[1] == '-s':
            sep = sys.argv[2]
    except IndexError:
        pass

    print(sep.join(get_headers()))
    for data in get_data():
        print(sep.join(str(i) for i in data))
