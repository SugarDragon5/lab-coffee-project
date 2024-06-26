import nfc

def on_connect(tag):
    print(tag)
    for line in tag.dump():
        print(line)
    print(tag.ndef)
    return True

try:
    with nfc.ContactlessFrontend("usb") as clf:
        while True:
            clf.connect(rdwr={"on-connect": on_connect})
except Exception as e:
    print(e)

