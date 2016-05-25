#!/usr/bin/env python
import can
import getopt
import sys
import binascii
import os, random
import time
import pdb
import string
from datetime import datetime



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

can_str: string with id to send in hex with 'x' to represent random char
data_str: formatted data string in hex with 'x' to represent random char
rate: integer number of ms to wait between sending
"""
def fuzzID(can_str, data_str, rate):
        global theBus, offline
	data_lst = [0, 0, 0, 0, 0, 0, 0, 0]
        can_id = 0x000000
	can_template = can_str
	data_template = data_str
	while(True):
		can_str = can_template
		data_str = data_template
        	while 'x' in can_str:
			can_str = can_str.replace('x', random.choice(string.hexdigits), 1) #Replace x with random hex char

		while 'x' in data_str:
			data_str = data_str.replace('x', random.choice(string.hexdigits), 1)#Replace x with random hex char

		try:
			can_id = int(can_str, 16)
			for i in range(8):
				data_lst[i] = int(data_str[i*2]+data_str[i*2+1], 16)
		except:
			print("can_str {} and data_str {} \ncan_id {} and data {}\nEXCEPTION THROWN".format(can_str, data_str, can_id, data_lst))
			sys.exit(2)

                msg = can.Message(arbitration_id=can_id, data=data_lst, extended_id=True)
		if not offline:
                	try:
                		theBus.send(msg)
				print("{} : 0x{}    {} {} {} {} {} {} {} {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), hex(can_id), 
					hex(data_lst[0]), hex(data_lst[1]), hex(data_lst[2]), hex(data_lst[3]), hex(data_lst[4]), hex(data_lst[5]), hex(data_lst[6]), hex(data_lst[7])))
                	except can.CanError:
                		print("Message NOT sent")
                		time.sleep(5000)
		else:
			print("{} : 0x{}    {} {} {} {} {} {} {} {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), hex(can_id), 
				hex(data_lst[0]), hex(data_lst[1]), hex(data_lst[2]), hex(data_lst[3]), hex(data_lst[4]), hex(data_lst[5]), hex(data_lst[6]), hex(data_lst[7])))
		sys.stdout.flush()
		time.sleep(rate / float(1000))

"""
Assumes prio, pgn, and source are properly formatted hex strings
Returns CAN ID string
"""
def makeCanId(prio, pgn, source):
	if(prio == ""):
		prio = "18"
	if(pgn == ""):
		pgn = "xxxx"
	if(source == ""):
		source = "xx"
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
                opts, args = getopt.getopt(sys.argv[1:], 'P:p:s:d:r:c:Oh', ['canid=', 'data=', 'rate=', 'priority=','pgn=','source=','offline','help'])
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
			print("\nBAD DATA LENGTH")
			sys.exit(2)
		if(not all(elt in data_chars for elt in data)):
			usage()
			print("\nINVALID DATA CHARACTERS")
			sys.exit(2)
	if(canid != "" and (pgn != "" or prio != "" or source != "")):
		usage()
		print("\nPlease only provide either -c or [-P, -p, and -s]")
		sys.exit(2)
	if(canid != ""):
		if(len(canid) != 8):
			usage()
			print("\nBAD CAN ID LENGTH")
			sys.exit(2)
		if(not all(elt in data_chars for elt in canid)):
			usage()
			print("\nINVALID CANID CHARACTERS")
			sys.exit(2)
	if(pgn != ""):
		if(len(pgn) != 4):
			usage()
			print("\nBAD PGN LENGTH")
			sys.exit(2)
		if(not all(elt in data_chars for elt in pgn)):
			usage()
			print("\nINVALID PGN CHARACTERS")
			sys.exit(2)
	if(prio != ""):
		if(len(prio) != 2):
			usage()
			print("\nBAD PRIORITY LENGTH")
			sys.exit(2)
		if(not all(elt in data_chars for elt in prio)):
			usage()
			print("\nINVALID PRIORITY CHARACTERS")
			sys.exit(2)
	if(source != ""):
		if(len(source) != 2):
			usage()
			print("\nBAD SOURCE LENGTH")
			sys.exit(2)
		if(not all(elt in data_chars for elt in source)):
			usage()
			print("\nINVALID SOURCE CHARACTERS")
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
		#use prio
		canid = makeCanId(prio, pgn, source)
	
	if(canid == ""):
		print("Must provide a canid or pgn")
		sys.exit(2)

	if(data == ""):
		data = "xxxxxxxxxxxxxxxx"

	canid = canid.replace('X', 'x')
	data = data.replace('X', 'x')

	print("canid: {}".format(canid))
	print("data: {}".format(data))
	print("rate: {}".format(rate))
        fuzzID(canid, data, rate)

if __name__ == "__main__":
	main()
