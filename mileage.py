from collections import namedtuple
from datetime import datetime, timedelta
from itertools import islice
import sys

from oauth2client.service_account import ServiceAccountCredentials
import gspread

scope = ['https://spreadsheets.google.com/feeds']
filename = 'personal-etl-dba50f184134.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(filename, scope)

gc = gspread.authorize(credentials)
key = '1zZfwcBQkpjbGqk3jT67IdnCuVSbr-YTiMQQNRCw0m30'
sheet = gc.open_by_key(key).worksheets()[1]

MILEAGE_COL = 1
DATE_COL = 2
TIME_COL = 3

EMPTY_ROW = ('', '', '')

SEP = '\t'

def get_raw_rows():
    all_cols = [sheet.col_values(ndx) for ndx in (MILEAGE_COL, DATE_COL,
                TIME_COL)]

    for r in zip(*all_cols):
        if r == EMPTY_ROW:
            return
        yield r

def get_headers():
    return 'mileage', 'timestamp'

def parse_timestamp(date, time):
    return datetime.strptime('{0} {1}'.format(date, time), '%m/%d/%Y %H:%M')

def get_data():
    for mileage, date, time in islice(get_raw_rows(), 1, None):
        yield mileage, parse_timestamp(date, time)

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
