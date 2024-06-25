from google.oauth2.service_account import Credentials
import gspread
import datetime
import nfc
from binascii import hexlify
import config
import gpiozero
import asyncio

try:
    state_led = gpiozero.LED(17)
    auth_led = gpiozero.LED(27)
    state_led.on()
    auth_led.off()
except gpiozero.BadPinFactory as e:
    state_led = None
    auth_led = None
    print(e)

async def led_blink(led, interval, count):
    if led is None:
        return
    for i in range(count):
        led.on()
        await asyncio.sleep(interval)
        led.off()
        await asyncio.sleep(interval)

print(f"{datetime.datetime.now().isoformat()} Start Program")
print(f"{datetime.datetime.now().isoformat()} Connecting to Google Sheets")
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
sheet_ic_log = spreadsheet.worksheet('IC Touch Log')
sheet_program_log = spreadsheet.worksheet('Program Log')
print(f"{datetime.datetime.now().isoformat()} Connected to Google Sheets")
sheet_program_log.append_row([datetime.datetime.now().isoformat(), 'Start Program'])

last_use = {}
def on_connect(tag):
    print(tag)
    if tag.type == 'Type3Tag':
        date = datetime.datetime.now().isoformat()
        idm = hexlify(tag.identifier).decode().upper()
        if idm not in last_use or last_use[idm] < datetime.datetime.now() - datetime.timedelta(seconds=10):
            print(f'Date:{date} IDm:{idm}')
            sheet_ic_log.append_row([date, idm])
            last_use[idm] = date
            asyncio.run(led_blink(auth_led, 0.3, 5))
    return True

print(f"{datetime.datetime.now().isoformat()} Start NFC")
with nfc.ContactlessFrontend("usb") as clf:
    while True:
        clf.connect(rdwr={"on-connect": on_connect})
