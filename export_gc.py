from utils.secrets import GARMIN_PASS, GARMIN_USER
from utils.common import gc
from utils.duration import Duration

import logging
import requests
import re
from dateutil.parser import parse

logging.basicConfig(level=logging.INFO)
key = '1RzVbHFsIw6K9koiI9oGdWkhQmZrwUikfLIoNhvdlEs8'
sheet = gc.open_by_key(key).get_worksheet(0)

KM_TO_MI = 0.62137
WEBHOST = "https://connect.garmin.com"
REDIRECT = "https://connect.garmin.com/post-auth/login"
BASE_URL = "http://connect.garmin.com/en-US/signin"
SSO = "https://sso.garmin.com/sso"
CSS = "https://static.garmincdn.com/com.garmin.connect/ui/css/gauth-custom-v1.2-min.css"
LOGIN_URL = 'https://sso.garmin.com/sso/login'


class GarminConnectClient(object):
    def __init__(self):
        self._session = requests.Session()

    def auth(self, username, password):
        login_params = {
            'service': REDIRECT,
            'webhost': WEBHOST,
            'source': BASE_URL,
            'redirectAfterAccountLoginUrl': REDIRECT,
            'redirectAfterAccountCreationUrl': REDIRECT,
            'gauthHost': SSO,
            'locale': 'en_US',
            'id': 'gauth-widget',
            'cssUrl': CSS,
            'clientId': 'GarminConnect',
            'rememberMeShown': 'true',
            'rememberMeChecked': 'false',
            'createAccountShown': 'true',
            'openCreateAccount': 'false',
            'usernameShown': 'false',
            'displayNameShown': 'false',
            'consumeServiceTicket': 'false',
            'initialFocus': 'true',
            'embedWidget': 'false',
            'generateExtraServiceTicket': 'false'
        }
        r = self._session.get(LOGIN_URL, params=login_params)
        if r.status_code != 200:
            raise RuntimeError('Trouble logging in')
        logging.debug('%s %s', r.status_code, r.url)

        login_data = {
            'username': username,
            'password': password,
            'embed': 'true',
            'lt': 'e1s1',
            '_eventId': 'submit',
            'displayNameRequired': 'false'
        }
        r = self._session.post(LOGIN_URL, params=login_params, data=login_data)
        if r.status_code != 200:
            raise RuntimeError('Trouble logging in')

        match = re.match(r'.*\?ticket=([-\w]+)\";.*', r.text, flags=re.MULTILINE | re.DOTALL)
        if not match:
            raise RuntimeError('No ticket in login response')
        ticket = match.group(1)
        logging.debug('Login ticket: %s', ticket)

        r = self._session.get('https://connect.garmin.com/modern/activities', params={'ticket': ticket})
        if r.status_code != 200:
            raise RuntimeError('Trouble logging in')

    def fetch_activities(self, start=0, limit=1):
        url = 'https://connect.garmin.com/modern/proxy/activitylist-service/activities/search/activities'
        r = self._session.get(url, params={'start': start, 'limit': limit})
        if r.status_code != 200:
            raise RuntimeError(r.text)
        return r.json()

def get_recorded_activities():
    activity_col = sheet.col_values(11)
    return {int(v) for v in activity_col[1:] if v}


def add_to_sheet(date, name, distance_km, duration, activity_id):
    distance_mi = distance_km * KM_TO_MI

    exercise_names = sheet.col_values(3)
    first_blank_row = next(ndx for ndx, name in enumerate(exercise_names) if name == '') + 1

    sheet.update_cell(first_blank_row, 1, date.strftime('%Y-%m-%d'))
    sheet.update_cell(first_blank_row, 2, date.strftime('%H:%M:%S'))
    sheet.update_cell(first_blank_row, 3, name)
    sheet.update_cell(first_blank_row, 4, repr(duration))
    sheet.update_cell(first_blank_row, 5, distance_mi)
    sheet.update_cell(first_blank_row, 11, activity_id)


if __name__ == '__main__':
    client = GarminConnectClient()
    client.auth(GARMIN_USER, GARMIN_PASS)
    activities = client.fetch_activities(0, 15)

    existing_ids = get_recorded_activities()

    for activity in (a for a in reversed(activities) if a['activityId'] not in existing_ids):
        exercise_name = activity['activityType']['typeKey']
        dur_sec = activity['duration']
        distance_km = activity['distance'] / 1000
        date_str = activity['startTimeLocal']
        add_to_sheet(parse(date_str), exercise_name, distance_km,
                     Duration(hours=0, minutes=0, seconds=int(round(dur_sec))), activity['activityId'])
