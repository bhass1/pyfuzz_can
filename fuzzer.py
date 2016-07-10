#!/usr/bin/env python

#### Copyright (c) 2016 Bill Hass {billhass@umich.edu}
#### Refer to Liscense.txt


import can
import getopt
import sys
import os, random
import time
import string
from datetime import datetime

valid_baud_rates = [
	1000000, 
	800000,
	500000,
	250000,
	125000,
	100000,
	95000,
	83000,
	50000,
	47000,
	33000,
	20000,
	10000,
	5000
]

def usage():
	print("Used to fuzz 29-bit CAN data frames (Particularly suited for J1939).")
	print("A typical usage is to try random data bytes for a given PGN and source")
	print("address at a given rate.")
	print("")
	print("fuzzer.py -p PGN -s SA -r RATE")
	print("")
	print("You may give an entire 29-bit CAN ID and use templated data bytes to ")
	print("provide a mix of known data and random data.")
	print("")
	print("fuzzer.py -r RATE -c 29bit_CANID -d DATA")
	print("")
	print("FLAGS")
	print("-b, --baud Baud rate integer in bits/second. (ex. 250000)") 
	print("-P, --priority Priority in hex. (ex. 18)") 
	print("-p, --pgn PGN in hex. (ex. fee1)") 
	print("-s, --source Source address in hex. (ex. 00)") 
	print("-d, --data Eight data bytes in hex. A single byte is two hex chars.")
	print("   	  Use x for random nibble. (ex. xx22xxxx556677xx)")
	print("   	  Use # for counter nibble. (ex. 11223344556677##)")
	print("   	  Only 1 counter allowed, and can be whole size of data.")
	print("   	  Use + for checksum nibble. (ex. 11223344556677++)")
	print("   	  Only 1 checksum allowed, and must be in final data byte.")
	print("-r, --rate An integer period that packets will be sent in ms in set {1, infinity}. (ex. 100)")
	print("-c, --canid Whole 29-bit CAN ID in hex. (ex. 18ef1200)")
	print("-O, --offline Used to flag that the CAN hardware is not connected")


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
	hex_chars = "0123456789abcdef" #ignore capitals so we don't have twice as many letters to randomly choose

	checksum = 0
	counter = 0
	has_counter = False

	while(True):
		can_str = can_template
		data_str = data_template
        	while 'x' in can_str:
			can_str = can_str.replace('x', random.choice(hex_chars), 1) #Replace x with random hex char

		while 'x' in data_str:
			data_str = data_str.replace('x', random.choice(hex_chars), 1)#Replace x with random hex char

		if '#' in data_str:
			#This is counter field
			has_counter = True
			count_count = data_str.count('#')
			start_pos = data_str.find('#')	
			for i in range(count_count - 1):
				if data_str[i+start_pos+1] != '#':
					print("Poor counter formatting. Only one field of consecutive # is allowed")
					sys.exit(2)
			cnt_str = "{0:0{1}x}".format(counter, count_count)
			for i in range(count_count):
				data_str = data_str.replace('#', cnt_str[i], 1)

		#Do checksum calculation last because we need to know all the bits and bytes
		if '+' in data_str:
			#This is checksum field
			count_check = data_str.count('+')
			if count_check > 2:
				print("Poor checksum formatting. A checksum greater than 1 byte is not allowed")
				sys.exit(2)
			start_pos = data_str.find('+')	
			if start_pos < 14:
				print("Poor checksum formatting. The checksum must be in the last data byte")
				sys.exit(2)
			for i in range(count_check - 1):
				if data_str[i+start_pos+1] != '+':
					print("Poor checksum formatting. Only one field of consecutive + is allowed")
					sys.exit(2)
			#checksum different depending on PGN
			checksum = int(can_str[0:2],16) + int(can_str[2:4],16) + int(can_str[4:6],16) + int(can_str[6:8],16)
			for i in range(7):
				checksum += int(data_str[i*2:i*2+2],16)
			checksum += counter
			if can_str[2:6] == "0000":
				checksum = (((checksum >> 6) & 0x3) + (checksum >> 0x3) + checksum) & 0x7
			elif count_check == 2:
				checksum = checksum & 0xff
			else:
				checksum = ((checksum >> 4) + checksum) & 0xf

			chk_str = "{0:0{1}x}".format(checksum, count_check)
			for i in range(count_check):
				data_str = data_str.replace('+', chk_str[i], 1)
			
		#Increment counter after checksum calc
		if has_counter:
			counter = (counter + 1) % 8

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
				print("{} : {}    {} {} {} {} {} {} {} {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), hex(can_id), 
					hex(data_lst[0]), hex(data_lst[1]), hex(data_lst[2]), hex(data_lst[3]), hex(data_lst[4]), hex(data_lst[5]), hex(data_lst[6]), hex(data_lst[7])))
                	except can.CanError:
                		print("Message NOT sent")
                		time.sleep(5000)
		else:
			print("{} : {}    {} {} {} {} {} {} {} {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), hex(can_id), 
				hex(data_lst[0]), hex(data_lst[1]), hex(data_lst[2]), hex(data_lst[3]), hex(data_lst[4]), hex(data_lst[5]), hex(data_lst[6]), hex(data_lst[7])))
		sys.stdout.flush()
		time.sleep(rate / float(1000))

"""
Assumes prio, pgn, and source are properly formatted hex strings
Returns CAN ID string
"""
def makeCanId(prio, pgn, source):
	if prio == "" :
		prio = "08"
	if pgn == "" :
		pgn = "xxxx"
	if source == "" :
		source = "xx"
	return prio + pgn + source


def main():
	global theBus, offline

	prio = ""
	pgn = ""
	source = ""
        data = ""
	rate = 100
        canid = ""
	baud = 250000
	offline = False

	#get args
        try:
                opts, args = getopt.getopt(sys.argv[1:], 'P:p:s:d:r:c:b:Oh', ['priority=','pgn=','source=','data=','rate=','canid=','baud=','offline','help'])
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
                elif opt in ('-b', '--baud'):
                        baud = arg
                elif opt in ('-O', '--offline'):
                        offline = True
                else:
                        usage()
                        sys.exit(2)
	#check args
	data_chars = "0123456789abcdefABCDEFxX#+"
	can_chars = "0123456789abcdefABCDEFxX"
	if data != "" :
		if len(data) != 16 :
			usage()
			print("\nBAD DATA LENGTH {}".format(len(data)))
			sys.exit(2)
		if not all(elt in data_chars for elt in data) :
			usage()
			print("\nINVALID DATA CHARACTERS")
			sys.exit(2)
	if canid != "" and (pgn != "" or prio != "" or source != "") :
		usage()
		print("\nPlease only provide either -c or [-P, -p, and -s]")
		sys.exit(2)
	if canid != "" :
		if len(canid) != 8 :
			usage()
			print("\nBAD CAN ID LENGTH")
			sys.exit(2)
		if not all(elt in can_chars for elt in canid) :
			usage()
			print("\nINVALID CANID CHARACTERS")
			sys.exit(2)
	if pgn != "" :
		if len(pgn) != 4 :
			usage()
			print("\nBAD PGN LENGTH")
			sys.exit(2)
		if not all(elt in can_chars for elt in pgn) :
			usage()
			print("\nINVALID PGN CHARACTERS")
			sys.exit(2)
	if prio != "" :
		if len(prio) != 2 :
			usage()
			print("\nBAD PRIORITY LENGTH")
			sys.exit(2)
		if not all(elt in can_chars for elt in prio) :
			usage()
			print("\nINVALID PRIORITY CHARACTERS")
			sys.exit(2)
	if source != "" :
		if len(source) != 2 :
			usage()
			print("\nBAD SOURCE LENGTH")
			sys.exit(2)
		if not all(elt in can_chars for elt in source) :
			usage()
			print("\nINVALID SOURCE CHARACTERS")
			sys.exit(2)
	if rate != 100 :
		try:
			rate = int(rate)
		except:
			usage()
			sys.exit(2)
		if rate < 1 :
			usage()
			sys.exit(2)
		if rate > 1000 :
			print("Did you really want > 1s period? Rate set to {}".format(rate))
	if baud != 250000 :
		try:
			baud = int(baud)
		except:
			usage()
			sys.exit(2)
		if baud not in valid_baud_rates :
			usage()
			sys.exit(2)

	#good to go
	if not offline : theBus = can.interface.Bus(bitrate=baud)


	if canid == "" :
		#use prio
		canid = makeCanId(prio, pgn, source)
	
	if canid == "" :
		print("Must provide a canid or pgn")
		sys.exit(2)

	if data == "" :
		data = "xxxxxxxxxxxxxxxx"

	canid = canid.replace('X', 'x')
	data = data.replace('X', 'x')

	print("canid: {}".format(canid))
	print("data: {}".format(data))
	print("rate: {}".format(rate))
        fuzzID(canid, data, rate)

if __name__ == "__main__":
	main()
