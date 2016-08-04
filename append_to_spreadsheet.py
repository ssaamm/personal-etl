from itertools import count

from oauth2client.service_account import ServiceAccountCredentials
import gspread

def append_to_spreadsheet(key, new_row, sheet_ndx=0):
    scope = ['https://spreadsheets.google.com/feeds']
    filename = 'personal-etl-dba50f184134.json'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(filename, scope)

    gc = gspread.authorize(credentials)
    sheet = gc.open_by_key(key).get_worksheet(sheet_ndx)

    for next_row in count(1):
        row = sheet.row_values(next_row)
        if all(not v for v in row):
            break

    for i, val in enumerate(new_row):
        sheet.update_cell(next_row, i + 1, val)
