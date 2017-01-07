from __future__ import print_function

import collections
import sys
from datetime import datetime

import requests

import mileage
from utils import car_costs, secrets
from utils.append_to_spreadsheet import append_to_spreadsheet

SEP = '\t'

EDMUNDS_TMV_URL = 'https://api.edmunds.com/v1/api/tmv/tmvservice/calculateusedtmv'
EDMUNDS_VEHICLE_URL = 'https://api.edmunds.com/api/vehicle/v2/{make}/{model}/{year}/styles?fmt=json&api_key={api_key}'
EDMUNDS_COLORS_URL = 'https://api.edmunds.com/api/vehicle/v2/styles/{style_id}/colors'

key = '1zZfwcBQkpjbGqk3jT67IdnCuVSbr-YTiMQQNRCw0m30'
def get_current_car_value(*args, **kwargs):
    value = _get_current_car_value(*args, **kwargs)
    append_to_spreadsheet(key, [datetime.now(), value], sheet_ndx=3)
    return value

def _get_current_car_value(mileage, condition='Clean'):
    '''
    Edmunds docs: http://developer.edmunds.com/api-documentation/vehicle/price_tmv/v1/04_calculateusedtmv/api-description
    '''
    url = EDMUNDS_TMV_URL
    payload = dict(styleid=101426246, api_key=secrets.EDMUNDS_KEY, fmt='json',
                   condition=condition, mileage=mileage, zip=78757,
                   colorid=200417024)
    r = requests.get(url, params=payload)
    return float(r.json()['tmv']['totalWithOptions']['usedPrivateParty'])

def get_style_id(make, model, year, trim):
    '''
    This is to make it easy if I get a new car or something
    '''
    url = EDMUNDS_VEHICLE_URL.format(api_key=secrets.EDMUNDS_KEY, make=make,
                                     model=model, year=year)
    r = requests.get(url)
    gls = next(s for s in r.json()['styles'] if s['trim'] == trim)
    return int(gls['id'])

def _get_colors(make, model, year, trim):
    url = EDMUNDS_COLORS_URL.format(style_id=get_style_id(make, model, year, trim))
    payload = dict(api_key=secrets.EDMUNDS_KEY, fmt='json')
    r = requests.get(url, params=payload)
    resp = r.json()
    return resp['colors']

def get_color_id(make, model, year, trim, name):
    '''
    This is to make it easy if I need to look up a color again
    '''
    colors = _get_colors(make, model, year, trim)
    return int(next(c['id'] for c in colors if c['name'] == name))

def get_headers():
    return ['category', 'cost_all', 'cost_noreimburse']

def get_data(per_mile=False):
    mileage_history = list(sorted(mileage.get_rows(), key=lambda t: t[0]))

    costs = collections.defaultdict(lambda: collections.defaultdict(float))
    cost_data = car_costs.get_data()
    for c in cost_data:
        costs[c.category]['all'] += c.cost
        if not c.reimbursable:
            costs[c.category]['noreimburse'] += c.cost

    current_mileage = int(mileage_history[-1][1])
    current_value = get_current_car_value(current_mileage)
    costs['Depreciation']['all'] = costs['Purchase']['all'] - current_value
    costs['Depreciation']['noreimburse'] = costs['Purchase']['noreimburse'] - current_value

    my_mileage = current_mileage - int(mileage_history[0][1])
    for k, v in costs.iteritems():
        if k == 'Purchase':
            continue
        if per_mile:
            yield k, v['all'] / my_mileage, v['noreimburse'] / my_mileage
        else:
            yield k, v['all'], v['noreimburse']


if __name__ == '__main__':
    sep = SEP
    try:
        if sys.argv[1] == '-s':
            sep = sys.argv[2]
    except IndexError:
        pass

    print(sep.join(get_headers()))
    total_all, total_noreimburse = 0.0, 0.0
    for data in get_data(per_mile=True):
        print(sep.join(str(i) for i in data))
        total_all += data[1]
        total_noreimburse += data[2]
    print('Total{s}{0}{s}{1}'.format(total_all, total_noreimburse, s=sep))
