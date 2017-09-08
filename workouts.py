import collections
import datetime
import sys
from itertools import islice, groupby

import pandas as pd

from utils.common import gc
from utils.duration import Duration

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
    first_day, last_day = min(chrono_dates), datetime.date.today()

    days = [first_day + datetime.timedelta(days=i) for i in range(1, (last_day - first_day).days + 1)]
    return pd.DataFrame(index=days, data=[d in workouts and any(workouts[d]) for d in days], columns=['worked_out_1d'])

def parse_timestamp(date, time):
    return datetime.datetime.strptime('{0} {1}'.format(date, time), '%Y-%m-%d %H:%M')

def get_data():
    did_workouts = get_daily_did_i_workout()
    did_workouts['worked_out_7d'] = did_workouts.worked_out_1d.rolling(window=7).mean()
    did_workouts['worked_out_28d'] = did_workouts.worked_out_1d.rolling(window=28).mean()
    del did_workouts['worked_out_1d']
    return did_workouts.reindex(did_workouts.index.rename('date'))

if __name__ == '__main__':
    sep = SEP
    try:
        if sys.argv[1] == '-s':
            sep = sys.argv[2]
    except IndexError:
        pass

    data = get_data()
    data.to_csv(sys.stdout, sep=sep)
