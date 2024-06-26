from google.oauth2.service_account import Credentials
import gspread
import datetime
import nfc
from binascii import hexlify
import config
import asyncio
import gpio
import gcp


# Initialize the program
print(f"{datetime.datetime.now().isoformat()} Start Program")
print(f"{datetime.datetime.now().isoformat()} Initializing GPIO")
try:
    state_led, auth_led = gpio.led_init()
except Exception as e:
    print(f"{datetime.datetime.now().isoformat()} Error: {e}")
    state_led = None
    auth_led = None
print(f"{datetime.datetime.now().isoformat()} Connecting to Google Sheets")
try:
    sheet_ic_log, sheet_program_log = gcp.gcp_init()
except Exception as e:
    print(f"{datetime.datetime.now().isoformat()} Error: {e}")
    exit()
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
            asyncio.run(gpio.led_blink(auth_led, 0.05, 5))
        else:
            print("-> Interval too short")


print(f"{datetime.datetime.now().isoformat()} Start NFC")
try:
    with nfc.ContactlessFrontend("usb") as clf:
        while True:
            clf.connect(rdwr={"on-connect": on_connect})
except Exception as e:
    print(f"{datetime.datetime.now().isoformat()} Error: {e}")
    sheet_program_log.append_row([datetime.datetime.now().isoformat(), f"Error: {e}"])
    asyncio.run(gpio.led_blink(state_led, 0.3, 3))
    asyncio.run(gpio.led_blink(auth_led, 0.3, 3))
