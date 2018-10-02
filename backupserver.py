import sys
import socket
import argparse
import string
import os

BUFFER_SIZE=80

parser= argparse.ArgumentParser(description='Process invoking command.')
parser.add_argument('-b', '--BSport', default=59000, type=int, required=False, help='port where the BS server accepts requests')
parser.add_argument('-n', '--CSname', default='localhost', type=str, required=False, help='name of the machine where the CS runs')
parser.add_argument('-p', '--CSport', default=58023, type=int, required=False, help='port where the CS server accepts requests')

args = parser.parse_args()

BSPORT= int(args.BSport)
CSNAME= str(args.CSname)
CSPORT= int(args.CSport)

def child():
   print('\nA new child ',  os.getpid())
   os._exit(0)  

def parent():
   while True:
      newpid = os.fork()
      if newpid == 0:
         child()
      else:
         pids = (os.getpid(), newpid)
         print("parent: %d, child: %d\n" % pids)
      reply = input("q for quit / c for new fork")
      if reply == 'c': 
          continue
      else:
          break

parent()

def tcp_server():
	server_addr=("localhost", BSPORT)

	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error:
		print 'Error creating socket [TCP]'
		sys.exit()

	try:
		s.bind(server_addr)
	except socket.error:
		print 'Error binding socket to address[TCP]'
		sys.exit()

	try:
		s.listen(1)
	except socket.error:
		print 'Error enabling server[TCP]'

	try:
		connection, client_address = s.accept()
	except socket.error:
		print 'Error accepting connection'

	while 1:
		try:
			data=connection.recv(BUFFER_SIZE)
			if not data: break
			print data
			connection.send(data)
		except socket.error:
			print 'Error transmiting data[TCP]'
			break

	connection.close()

	return


def udp_server():
	server_addr=(CSNAME, BSPORT)

	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	except socket.error:
		print 'Error creating socket [UDP]'
		sys.exit()

	try:
		s.bind(server_addr)
	except socket.error:
		print 'Error binding socket to address[UDP]'
		sys.exit()

	while 1:
		try:
			data,addr=s.recvfrom(BUFFER_SIZE)
			if not data: break
			print data
			s.sendto(addr)
		except socket.error:
			print 'Error transmiting data[UDP]'
			break
	
	return
