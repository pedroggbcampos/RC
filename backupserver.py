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

IPBS = socket.gethostbyname(socket.gethostname())


def tcp_server():
	tcp_addr=("localhost", BSPORT)

	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error:
		print 'Error creating socket [TCP]'
		sys.exit()

	try:
		s.bind(tcp_addr)
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

	try:
		data=connection.recv(BUFFER_SIZE)
		if len(data)==0:
			return None
		while(data[-1]!="\n"):
			data+=recv(BUFFER_SIZE)
		#print data
		msg=handler_USER(data)
		connection.send(msg)
	except socket.error:
		print 'Error transmiting data[TCP]'

	connection.close()

	return


def udp_server():

	ip_cs = socket.gethostbyname(CSNAME)

	cs_addr =(ip_cs, CSPORT)

	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	except socket.error:
		print 'Error creating socket [UDP]'
		sys.exit()

	try:
		s.bind(cs_addr)
	except socket.error:
		print 'Error binding socket to address[UDP]'
		sys.exit()

	msg = "REG " + IPBS + " " + BSPORT + "\n"
	s.sendto(msg, cs_addr)
	try:
		data,addr=s.recvfrom(BUFFER_SIZE)
		if data==0:
			return None
		while data[-1] != "\n":
			data+= s.recvfrom(BUFFER_SIZE)
		#print data
		msg=handler_CS(data)
		s.sendto(msg, cs_addr)
	except socket.error:
		print 'Error transmiting data[UDP]'
	
	return


def handler_CS(msg):
	path="/BS/user"

	msg = msg.split(" ")

	if msg[0]=="RGR":
		if (msg[1]=="NOK" or msg[1]=="RGR ERR"):
			sys.exit()

	elif msg[0]=="UAR":
		if (msg[1]=="NOK" or msg[1]=="RGR ERR"):
			sys.exit()

	elif msg[0]=="LSF":
		if (len(msg)==3 and isinstance(msg[1], int) and len(str(msg[1]))==5 and msg[2].isalnum() and len(msg[2])==8):
			if is_user_dir(msg[1],msg[2]):
				files=find_dir(message[1], message[2])
				n_msg = "LFD " + len(files) + " " + files
			else:
				n_msg = "LFD NOK"
		else:
			n_msg = "LFD ERR"

	elif msg[0]=="LSU":
		if (len(msg)==3 and isinstance(msg[1], int) and len(str(msg[1]))==5 and msg[2].isalnum() and len(msg[2])==8):
			if is_user(msg[1]):
				n_msg = "LUR OK"
			else:
				add_user_bs(msg[1], msg[2])
				n_msg = "LUR NOK"
				print "New user: %d", msg[1]
		else:
			n_msg="LUR ERR"

	elif msg[0]=="DLB":
		if (len(msg)==3 and isinstance(msg[1], int) and len(str(msg[1]))==5 and isinstance(msg[2], str)):
			if is_user_dir(msg[1],msg[2]):
				remove_dir(msg[1], msg[2])
				n_msg = "DBR OK"
			else:
				n_msg = "DBR NOK"
		else:
			n_msg = "DBR ERR"

	else:
		n_msg="ERR"

	return n_msg

def remove_dir(nid, dir):
	path="/BS/user%d/", nid
	path+=dir
	try:
		os.rmdir(path)
	except OSError:
		print("Deletion failed")
	return

def is_user_dir(ud, dir):
	return

def is_user(id, p):
	try:
		f= open("user_"+id+".txt", "r")
		if p in f.read():
			return True
		else:
			return False
	except IOError:
		return False
	

def add_user_bs(nid, p):
	path="/BS/user"+ nid
	file=open(path + ".txt", "w")
	file.write(p)
	file.close()
	os.mkdir(path)
	return

def handler_USER(msg):
	path="/BS/user"
	msg = msg.split( )

	if msg[0]=="AUT":
		if is_user(msg[1], msg[2]):
			print "User:%i", msg[1]
			n_msg="AUR OK"
		else:
			n_msg="AUR NOK"

	elif msg[0]=="UPL":
		if transfer(msg[1], msg[2], msg[3]):
			n_msg="UPR OK"
		else:
			n_msg="UPR NOK"

	elif msg[0]=="RSB":
		if (len(msg)==2 and isinstance(msg[1], str)):
			if find_dir(msg[1]):
				#:::esta mal
				d=get_dir(msg[1])
				#:::
				n_msg="RBR" + len(d) + " " + d
			else:
				n_msg="RBR EOF"
		else:
			n_msg="RBR ERR"

	else:
		n_msg="ERR"

	return n_msg
			

def transfer(dir, n, files):
	return

def find_dir(dir):
	return os.path.isdir("/"+dir)