#!/usr/bin/env python
import can
import getopt
import sys
import binascii
import os, random
import time
import pdb



def usage():
	print("Used to fuzz CAN data frames. A typical usage is to try random data bytes")
	print("for a given PGN and source address at a given rate.")
	print("")
	print("fuzzer.py -p PGN -s SA -r RATE")
	print("")
	print("You may give an entire 29-bit CAN ID and use templated data bytes to ")
	print("provide a mix of known data and random data.")
	print("")
	print("fuzzer.py -r RATE -c 29bit_CANID -d DATA")
	print("")
	print("FLAGS")
	print("-P, --priority priority in hex.(ex. 18)") 
	print("-p, --pgn PGN in hex. (ex. fee1)") 
	print("-s, --source source address in hex. (ex. 00)") 
	print("-d, --data Eight data bytes in hex. A single byte is two hex chars.")
	print("   	  Use xx for random byte. (ex. 1122334455667788 or xx22xxxx556677xx)")
	print("-r, --rate rate of the fuzzing packets in decimal ms in set {1, infinity}.(ex. 100)")
	print("-c, --canid whole 29-bit CAN ID in hex. (ex. 18ef1200)")
	print("-O, --offline used to flag that the PEAK tool is not connected")


"""
Fuzzes either id, data, or both

hasData: when true sends out random CAN ids with given data
hasId: when true sends out random data with given id
can_str: string with id to send, id must be in decimal form
data_str: string with data to send, eg. "0,25,0,1,3,1,4,3",
rate: integer number of ms to wait between sending
"""
def fuzzID(hasData, hasId, can_str, data_str, rate):
        global theBus, offline
	data_lst = [0, 0, 0, 0, 0, 0, 0, 0]
        can_id = 0x000000

        if data_str != " ":
                count = 0
                for element in data_str.split(","):
                        #data_lst[count](hex(int(element)))
                        data_lst[count] = hex(int(element))
                        count+=1

        if can_str != " ":
                can_id = hex(int(can_str))

        pdb.set_trace()

        #for i in range(0, amt):
	while(true):
                if hasData:
                        can_id = binascii.b2a_hex(os.urandom(3))
                if hasId:
                        for i in range(0, 8):
                                msg = can.Message(arbitration_id=can_id, data=data_list, extended_id=False)

                for i in range(0, 20):
                        try:
                                if(not offline): theBus.send(msg)
                                if(not offline): print("Message sent on {} for message {} with data {}".format(theBus.channel_info, can_id, data_lst))
				else: print("Generated message: {} with data {}".format(theBus.channel_info, can_id, data_lst))
                        except can.CanError:
                                print("Message NOT sent")
                        time.sleep(rate / 1000)
                time.sleep(0.3)

"""
Assumes prio, pgn, and source are properly formatted hex strings
Returns CAN ID string
"""
def makeCanId(prio, pgn, source):
	return prio + pgn + source


def main():
	global theBus, offline

	offline = False
        data = ""
        canid = ""
	prio = ""
	pgn = ""
	source = ""
	rate = 100

	#get args
        try:
                opts, args = getopt.getopt(sys.argv[1:], 'P:p:s:d:r:c:O:h', ['canid=', 'data=', 'rate=', 'priority=','pgn=','source=','offline=','help'])
        except getopt.GetoptError:
                usage()
                sys.exit(2)
        for opt, arg in opts:
                if opt in ('-h', '--help'):
                        usage()
                        sys.exit(2)
                elif opt in ('-P', '--priority'):
                        prio = arg;
                elif opt in ('-p', '--pgn'):
			pgn = arg;
                elif opt in ('-s', '--source'):
			source = arg
                elif opt in ('-d', '--data'):
                        data = arg
                elif opt in ('-r', '--rate'):
			rate = arg
                elif opt in ('-c', '--canid'):
                        canid = arg
                elif opt in ('-O', '--offline'):
                        offline = True
                else:
                        usage()
                        sys.exit(2)
	#check args
	data_chars = "0123456789abcdefABCDEFxX"
	hex_chars = "0123456789abcdefABCDEF"
	if(data != ""):
		if(len(data) != 16):
			usage()
			sys.exit(2)
		if(not all(elt in data for elt in data_chars)):
			usage()
			sys.exit(2)
	if(canid != "" and (pgn != "" or prio != "" or source != "")):
		usage()
		print("Please only provide either -c or [-P, -p, and -s]")
		sys.exit(2)
	if(canid != ""):
		if(len(canid) != 8):
			usage()
			sys.exit(2)
		if(not all(elt in canid for elt in hex_chars)):
			usage()
			sys.exit(2)
	if(pgn != ""):
		if(len(pgn) != 4):
			usage()
			sys.exit(2)
		if(not all(elt in pgn for elt in hex_chars)):
			usage()
			sys.exit(2)
	if(prio != ""):
		if(len(prio) != 2):
			usage()
			sys.exit(2)
		if(not all(elt in prio for elt in hex_chars)):
			usage()
			sys.exit(2)
	if(source != ""):
		if(len(source) != 2):
			usage()
			sys.exit(2)
		if(not all(elt in source for elt in hex_chars)):
			usage()
			sys.exit(2)
	if(rate != 100):
		try:
			rate = int(rate)
		except:
			usage()
			sys.exit(2)
		if(rate < 1):
			usage()
			sys.exit(2)
		if(rate > 1000):
			print("Did you really want > 1s period? Rate set to {}".format(rate))

	#good to go
	if(not offline): theBus = can.interface.Bus()


	if(canid == ""):
		print("Single empty canid")
		#use prio
		canid = makeCanId(prio, pgn, source)
	
	if(canid == ""):
		print("Double empty canid")
	else:
		print("Not dbl empty : {}".format(canid))

	print("data: {}".format(data))
	print("rate {}".format(rate))
        fuzzID(data != "", canid != "", canid, data, rate)

if __name__ == "__main__":
	main()
