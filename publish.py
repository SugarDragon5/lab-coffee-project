import binascii
import nfc
import os
import secrets
import argparse

import config
import gen_mac
import gen_cardkey

class MyCardReader(object):
    def __init__(self):
        self.master = config.MASTER_KEY

    def on_connect_1(self, tag):
        sc_read = nfc.tag.tt3.ServiceCode(0, 0x0b)
        sc_write = nfc.tag.tt3.ServiceCode(0, 0x09)

        if args.id:
            ID_six = os.urandom(6) # かぶる可能性あるかも
            ID = b"\x00"*10 + ID_six # write_without_encryptionに使います。
            bc82 = nfc.tag.tt3.BlockCode(0x82, service=0)
            tag.write_without_encryption([sc_write], [bc82], ID)
        else:
            bc82 = nfc.tag.tt3.BlockCode(0x82, service=0)
            ID_six = tag.read_without_encryption([sc_read], [bc82])[-6:]

        if args.ck:
            CK = gen_cardkey.gen_key(bytes(tag.idm) + b"\x00\x00" + ID_six, self.master) # IDmとIDdは同じです。
            bc87 = nfc.tag.tt3.BlockCode(0x87, service=0)
            tag.write_without_encryption([sc_write], [bc87], CK)

            CKV = b"\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            bc86 = nfc.tag.tt3.BlockCode(0x86, service=0)
            tag.write_without_encryption([sc_write], [bc86], CKV)

        if args.mc:
            MC = bytes.fromhex(args.mc)
        else:
            MC = b"\xFF\xFF\x00\x01\x07\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        bc88 = nfc.tag.tt3.BlockCode(0x88, service=0)
        tag.write_without_encryption([sc_write], [bc88], MC)

        return True

    def on_connect_2(self, tag):
        sc_read = nfc.tag.tt3.ServiceCode(0, 0x0b)
        sc_write = nfc.tag.tt3.ServiceCode(0, 0x09)

        if args.user:      
            user = args.user.encode()
            if len(user) > 16:
                print('userID must be < 16')
            else:
                bc00 = nfc.tag.tt3.BlockCode(0x00, service=0)
                tag.write_without_encryption([sc_write], [bc00], user)
        
        if args.mc:
            MC = bytes.fromhex(args.mc)
        else:
            MC = b"\xFF\xFF\xFF\x01\x07\x01\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00"
        bc88 = nfc.tag.tt3.BlockCode(0x88, service=0)
        tag.write_without_encryption([sc_write], [bc88], MC)
        
        return True

    def read_id(self):
        clf = nfc.ContactlessFrontend('usb')
        if args.stage == 1:
            try:
                clf.connect(rdwr={'on-connect': self.on_connect_1})
            finally:
                clf.close()
        if args.stage == 2:
            try:
                clf.connect(rdwr={'on-connect': self.on_connect_2})
            finally:
                clf.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='this program supports publishing felica lite S cards')
    parser.add_argument('stage', help='the stage of issuance you want to perform (1or2)', choices=[1, 2])
    parser.add_argument('--id', help='If specified, ID will not be changed (at 1st issuance)', action='store_false')
    parser.add_argument('--ck', help='If specified, CK will not be changed (at 1st issuance)', action='store_false')
    parser.add_argument('--user', help='the user name to be stored in S_PAD0 (16 characters or less)')
    parser.add_argument('--mc', help='specify commands to be stored in MC', type=str)
    args = parser.parse_args()
    cr = MyCardReader()
    while True:
        cr.read_id()
