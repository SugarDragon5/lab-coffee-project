from google.oauth2.service_account import Credentials
import gspread
import datetime
import nfc
from binascii import hexlify
import config
import asyncio
import gpio
import gcp
import gen_cardkey
import gen_mac
import secrets


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
        master = config.MASTER_KEY
        sc_read = nfc.tag.tt3.ServiceCode(0, 0x0b)
        sc_write = nfc.tag.tt3.ServiceCode(0, 0x09)
        RC = secrets.token_bytes(16)
        bc80 = nfc.tag.tt3.BlockCode(0x80, service=0)
        tag.write_without_encryption([sc_write], [bc80], RC)
        bc82 = nfc.tag.tt3.BlockCode(0x82, service=0) # ID
        bc86 = nfc.tag.tt3.BlockCode(0x86, service=0) # CKV
        bc91 = nfc.tag.tt3.BlockCode(0x91, service=0) # MAC_A

        ret = tag.read_without_encryption([sc_read], [bc82, bc86, bc91])
        ID = bytes(ret[:16])
        CKV = ret[16:32]
        MAC_A_Card = ret[32:40]

        CK = gen_cardkey.gen_key(ID, master)
        MAC_A = gen_mac.mac_a(RC, CK, ID, CKV)

        if MAC_A_Card == MAC_A:
            date = datetime.datetime.now()
            # idm = hexlify(tag.identifier).decode().upper()
            idm = tag.idm
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
        else:
            print("The card is invalid\n")


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
