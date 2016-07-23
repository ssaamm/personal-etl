from collections import namedtuple
from datetime import datetime, timedelta
from itertools import islice
from mileage import parse_timestamp
import sys

from oauth2client.service_account import ServiceAccountCredentials
import gspread

scope = ['https://spreadsheets.google.com/feeds']
filename = 'personal-etl-dba50f184134.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(filename, scope)

gc = gspread.authorize(credentials)
key = '1zZfwcBQkpjbGqk3jT67IdnCuVSbr-YTiMQQNRCw0m30'
sheet = gc.open_by_key(key).worksheets()[0]

Cost = namedtuple('Cost', ['name', 'timestamp', 'category', 'cost', 'reimbursable'])

def get_raw_rows():
    all_cols = [sheet.col_values(ndx) for ndx in range(1, 7)]

    for r in zip(*all_cols):
        if all(not f for f in r):
            return
        yield r

def get_raw_objects():
    raw_rows = get_raw_rows()
    headers = [h.lower().strip() for h in next(raw_rows)]

    for r in raw_rows:
        yield dict(zip(headers, r))

def averaged_missing(costs):
    costs = list(costs)

    for ndx, cost in enumerate(costs):
        if cost.cost:
            continue

        same_category = [c.cost for c in costs
                         if c.category == cost.category and c.cost]
        new_cost = float(sum(same_category)) / len(same_category)

        costs[ndx] = Cost(cost.name, cost.timestamp, cost.category, new_cost,
                          cost.reimbursable)

    return costs

def get_intermediate_data():
    for elem in get_raw_objects():
        elem['reimbursable'] = elem['reimbursable'] == '1'

        elem['timestamp'] = parse_timestamp(elem['date'], elem['time'])
        del elem['date']
        del elem['time']

        try:
            elem['cost'] = float(elem['cost'])
        except ValueError:
            elem['cost'] = None

        yield Cost(**elem)

def get_data():
    for i in averaged_missing(get_intermediate_data()):
        yield i

if __name__ == '__main__':
    for r in get_data():
        print(r)
