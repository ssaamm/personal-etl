from collections import namedtuple
from common import gc
from mileage import parse_timestamp

key = '1zZfwcBQkpjbGqk3jT67IdnCuVSbr-YTiMQQNRCw0m30'
sheet = gc.open_by_key(key).get_worksheet(0)

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

def averaged_missing(costs, nearest_n=None):
    costs = list(costs)

    for ndx, cost in enumerate(costs):
        if cost.cost:
            continue

        same_category = sorted((c for c in costs if c.category == cost.category and c.cost),
                               key=lambda c: abs((c.timestamp - cost.timestamp).seconds))
        costs_to_avg = [c.cost for c in same_category][:nearest_n]
        new_cost = float(sum(costs_to_avg)) / len(costs_to_avg)

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
    for i in averaged_missing(get_intermediate_data(), nearest_n=2):
        yield i

if __name__ == '__main__':
    for r in get_data():
        print(r)
