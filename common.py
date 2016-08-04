from oauth2client.service_account import ServiceAccountCredentials
import gspread

scope = ['https://spreadsheets.google.com/feeds']
filename = 'personal-etl-dba50f184134.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(filename, scope)

gc = gspread.authorize(credentials)
