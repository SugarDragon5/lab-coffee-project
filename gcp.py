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
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
credentials = Credentials.from_service_account_file(
    config.CREDENTIAL_FILE, scopes=scopes
)
gc = gspread.authorize(credentials)
spreadsheet_url = config.SPREADSHEET_URL
spreadsheet = gc.open_by_url(spreadsheet_url)
sheet_ic_log = spreadsheet.worksheet("IC Touch Log")
sheet_program_log = spreadsheet.worksheet("Program Log")
print(f"{datetime.datetime.now().isoformat()} Connected to Google Sheets")
sheet_program_log.append_row([datetime.datetime.now().isoformat(), "Start Program"])

last_use = {}


def on_connect(tag):
    print(tag)
    if tag.type == "Type3Tag":
        date = datetime.datetime.now()
        idm = hexlify(tag.identifier).decode().upper()
        print(f"Date:{date.isoformat()} IDm:{idm}")
        if idm not in last_use or (
            datetime.datetime.now() - last_use[idm]
        ) > datetime.timedelta(seconds=10):
            sheet_ic_log.append_row([date.isoformat(), idm])
            last_use[idm] = date
            print("-> Data saved")
            asyncio.run(led_blink(auth_led, 0.05, 5))
        else:
            print("-> Interval too short")
    return True


print(f"{datetime.datetime.now().isoformat()} Start NFC")
try:
    with nfc.ContactlessFrontend("usb") as clf:
        while True:
            clf.connect(rdwr={"on-connect": on_connect})
except Exception as e:
    print(f"{datetime.datetime.now().isoformat()} Error: {e}")
    sheet_program_log.append_row([datetime.datetime.now().isoformat(), f"Error: {e}"])
    asyncio.run(led_blink(state_led, 0.3, 3))
    asyncio.run(led_blink(auth_led, 0.3, 3))
