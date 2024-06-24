from google.oauth2.service_account import Credentials
import gspread
import datetime
import nfc
from binascii import hexlify
import config

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
credentials = Credentials.from_service_account_file(
    config.CREDENTIAL_FILE,
    scopes=scopes
)
gc = gspread.authorize(credentials)
spreadsheet_url = config.SPREADSHEET_URL
spreadsheet = gc.open_by_url(spreadsheet_url)
print("Connected to Google Sheets")

last_use = {}

def on_connect(tag):
    print(tag)
    if tag.type == 'Type3Tag':
        date = datetime.datetime.now().isoformat()
        idm = hexlify(tag.identifier).decode().upper()
        if idm not in last_use or last_use[idm] < datetime.datetime.now() - datetime.timedelta(seconds=10):
            print(f'Date:{date} IDm:{idm}')
            spreadsheet.sheet1.append_row([date, idm])
            last_use[idm] = date
    return True

if __name__ == '__main__':
    with nfc.ContactlessFrontend("usb") as clf:
        while True:
            clf.connect(rdwr={"on-connect": on_connect})