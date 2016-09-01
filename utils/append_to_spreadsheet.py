from itertools import count
from common import gc

def append_to_spreadsheet(key, new_row, sheet_ndx=0):
    sheet = gc.open_by_key(key).get_worksheet(sheet_ndx)

    for next_row in count(1):
        row = sheet.row_values(next_row)
        if all(not v for v in row):
            break

    for i, val in enumerate(new_row):
        sheet.update_cell(next_row, i + 1, val)