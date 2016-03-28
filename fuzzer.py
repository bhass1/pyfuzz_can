#!/usr/bin/env python
import can
import getopt
import sys
import binascii
import os, random
import time
import pdb

"""
Fuzzes either ids, data, or both

fuzzCAN: when true sends out random CAN ids with given data
fuzzData: when true sends out random data with given id
can_str: string with id to send, id must be in decimal form
data_str: string with data to send, eg. "0,25,0,1,3,1,4,3",
amt: number of different IDs to send
"""
def fuzzID(fuzzCAN, fuzzData, can_str, data_str, amt):
        data_lst = [0, 0, 0, 0, 0, 0, 0, 0]
        can_id = 0x000000

        if data_str != " ":
                count = 0
                for element in data_str.split(","):
                        data_lst[count](int(element))
                        count+=1

        if can_str != " ":
                can_id = hex(int(can_str))

        pdb.set_trace()

        bus = can.interface.Bus()
        for i in range(0, amt):
                if fuzzCAN:
                        can_id = binascii.b2a_hex(os.urandom(3))
                if fuzzData:
                        for i in range(0, 8):
                                msg = can.Message(arbitration_id=can_id, data=data_list, extended_id=False)

                for i in range(0, 20):
                        try:
                                bus.send(msg)
                                print("Message sent on {} for message {} with data {}".format(bus.channel_info, can_id, data_lst))
                        except can.CanError:
                                print("Message NOT sent")
                        time.sleep(0.1)
                time.sleep(0.3)

def main():
        fuzzCAN = False
        fuzzData = False

        usedata = " "
        canid = " "
        amt = 0
        try:
                opts, args = getopt.getopt(sys.argv[1:], 'c:d:a:h', ['canid=', 'data=', 'amt=', 'help'])
        except getopt.GetoptError:
                usage()
                sys.exit(2)
        for opt, arg in opts:
                if opt in ('-h', '--help'):
                        usage()
                        sys.exit(2)
                elif opt in ('-c', '--canid'):
                        fuzzData = True
                        canid = arg
                elif opt in ('-d', '--data'):
                        fuzzCAN = True
                        usedata = arg
                elif opt in ('-a', '--amt'):
                        amt = int(arg)
                else:
                        usage()
                        sys.exit(2)

        fuzzID(fuzzCAN, fuzzData, canid, usedata, amt)

if __name__ == "__main__":
	main()
