from common import gc
from datetime import datetime
from itertools import islice, count, groupby
import sys

key = '1RzVbHFsIw6K9koiI9oGdWkhQmZrwUikfLIoNhvdlEs8'
sheet = gc.open_by_key(key).get_worksheet(1)

SEP = '\t'

def get_raw_rows():
    all_cols = [sheet.col_values(ndx) for ndx in (1, 2, 3)]

    for row in islice(zip(*all_cols), 1, None):
        if all(not v for v in row):
            raise StopIteration
        yield parse_timestamp(row[0], row[1]), float(row[2])

def get_rows_by_date():
    for date, weigh_ins in groupby(get_raw_rows(), key=lambda t: t[0].date()):
        weights = [w for ts, w in weigh_ins]
        yield date, min(weights), max(weights), len(weights)

def get_headers():
    return 'date', 'min_weight', 'max_weight', 'num_weights'

def parse_timestamp(date, time):
    return datetime.strptime('{0} {1}'.format(date, time), '%m/%d/%Y %H:%M')

def get_data():
    for t in get_rows_by_date():
        yield t

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
