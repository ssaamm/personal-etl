from utils.common import gc
from datetime import datetime
from itertools import islice, count, groupby
import sys
import pandas as pd
import numpy as np


key = '1RzVbHFsIw6K9koiI9oGdWkhQmZrwUikfLIoNhvdlEs8'
sheet = gc.open_by_key(key).get_worksheet(1)


CRIT_VAL_90 = 1.645
SEP = '\t'

def get_raw_rows():
    all_cols = [sheet.col_values(ndx) for ndx in (1, 2, 3)]

    for row in islice(zip(*all_cols), 1, None):
        if all(not v for v in row):
            raise StopIteration
        yield parse_timestamp(row[0], row[1]), float(row[2])

def get_data():
    rows = list(get_raw_rows())
    df = pd.DataFrame(data=[t[1] for t in rows], index=[t[0] for t in rows], columns=['weight'])
    df = df.groupby(pd.TimeGrouper('1w')).weight.agg([np.mean, np.std, len])

    ci = CRIT_VAL_90 * (df['std'] / np.sqrt(df['len']))
    df['low'] = df['mean'] + ci
    df['high'] = df['mean'] - ci

    df.dropna(inplace=True)
    df.index.name = 'date'
    return df[['mean', 'low', 'high']]

def parse_timestamp(date, time):
    return datetime.strptime('{0} {1}'.format(date, time), '%m/%d/%Y %H:%M')

if __name__ == '__main__':
    sep = SEP
    try:
        if sys.argv[1] == '-s':
            sep = sys.argv[2]
    except IndexError:
        pass

    df = get_data()
    df.to_csv(sys.stdout, sep=sep)
