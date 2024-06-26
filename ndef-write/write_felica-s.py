import nfc

def on_connect(tag):
    print(tag)
    if tag.type == "Type3Tag":
        sc_read = nfc.tag.tt3.ServiceCode(0, 0x0B)
        sc_write = nfc.tag.tt3.ServiceCode(0, 0x09)
        bc00 = nfc.tag.tt3.BlockCode(0x00)
        bc01 = nfc.tag.tt3.BlockCode(0x01)
        bc88 = nfc.tag.tt3.BlockCode(0x88)
        tag.write_without_encryption([sc_write], [bc00], b"Hello\00\00\00\00\00\00\00\00\00\00\00")
        tag.write_without_encryption([sc_write], [bc01], b"Mlab\00\00\00\00\00\00\00\00\00\00\00\00")

        # 1次書き込み！
        mc_value = b"\xFF\xFF\x00\x01\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        tag.write_without_encryption([sc_write], [bc88], mc_value)

    else:
        print("Only Felica is supported")

    return True

try:
    with nfc.ContactlessFrontend("usb") as clf:
        while True:
            clf.connect(rdwr={"on-connect": on_connect})
except Exception as e:
    print(e)
