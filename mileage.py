from __future__ import print_function
from utils.common import gc, pairwise
from datetime import datetime, timedelta
from itertools import islice
import sys
import pandas as pd

key = '1zZfwcBQkpjbGqk3jT67IdnCuVSbr-YTiMQQNRCw0m30'
sheet = gc.open_by_key(key).worksheets()[1]

MILEAGE_COL = 1
DATE_COL = 2
TIME_COL = 3

EMPTY_ROW = ('', '', '')

SEP = '\t'

def get_rows():
    all_cols = [sheet.col_values(ndx) for ndx in (MILEAGE_COL, DATE_COL,
                TIME_COL)]

    for mileage, date, time in islice(zip(*all_cols), 1, None):
        if (mileage, date, time) == EMPTY_ROW:
            raise StopIteration
        yield parse_timestamp(date, time), int(mileage)

def parse_timestamp(date, time):
    return datetime.strptime('{0} {1}'.format(date, time), '%m/%d/%Y %H:%M')

def get_weekly_miles():
    rows = list(get_rows())
    df = pd.DataFrame(data=[t[1] for t in rows], index=[t[0] for t in rows], columns=['mileage'])
    df = df.groupby(pd.TimeGrouper('1W')).max().interpolate()

    for wk1, wk2 in pairwise(df.iterrows()):
        week = wk2[0].date().strftime('%Y-%m-%d')
        miles_driven = wk2[1]['mileage'] - wk1[1]['mileage']
        yield (week, miles_driven)

if __name__ == '__main__':
    sep = SEP
    try:
        if sys.argv[1] == '-s':
            sep = sys.argv[2]
    except IndexError:
        pass

    print(sep.join(('week_ending', 'miles_driven')))
    for week, miles_driven in get_weekly_miles():
        print('{}{}{}'.format(week, sep, miles_driven))
