import itertools
import sys
from collections import namedtuple
from datetime import datetime, timedelta

from utils.common import gc

key = '1xjRLMoirdEOUr9bHHGzDU2qgdAJXl0sby5LMd9sGF8Q'
locations = gc.open_by_key(key).sheet1

DATE_COL = 1
LAT_COL = 3
LON_COL = 4

MIN_COMMUTE_TIME = timedelta(minutes=10)
MAX_COMMUTE_TIME = timedelta(minutes=60)

EMPTY_ROW = ('', '', '')

WORK = 'WORK'
HOME = 'HOME'

SEP = '\t'

Row = namedtuple('Row', ['date', 'location'])

# https://docs.python.org/3/library/itertools.html
def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

def get_raw_rows():
    all_cols = [locations.col_values(ndx) for ndx in (DATE_COL, LAT_COL,
                LON_COL)]

    for r in zip(*all_cols):
        if r == EMPTY_ROW:
            return
        yield r

def parse_date(date_str):
    return datetime.strptime(date_str, '%B %d, %Y at %I:%M%p')

def get_location(lat, lon):
    if lat.startswith('30.27') and lon.startswith('-97.76'):
        return WORK
    elif lat.startswith('30.34') and lon.startswith('-97.73'):
        return HOME
    return None

def cleaned_rows(rows):
    for date_str, lat, lon in rows:
        yield Row(date=parse_date(date_str), location=get_location(lat, lon))

def get_headers():
    return 'start_time', 'duration', 'destination'

def get_data():
    for row1, row2 in pairwise(cleaned_rows(get_raw_rows())):
        duration = row2.date - row1.date
        if duration > MAX_COMMUTE_TIME or duration < MIN_COMMUTE_TIME:
            continue
        
        yield row1.date, duration.seconds, row2.location

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
