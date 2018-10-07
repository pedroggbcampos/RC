import sys
import socket
import argparse
import string
import os
import shutil
from threading import Thread

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


def tcp_thread():
	while True:
		tcp_server()
	return

def tcp_server():
	tcp_addr=("", BSPORT)

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
	while (True):
		try:
			data = connection.recv(BUFFER_SIZE)
			if data == "":
				break
			elif data == 0:
				print 'Error transmiting data[TCP]'
				break
			while(data[-1]!="\n"):
				data += connection.recv(BUFFER_SIZE)
			print data
			msg = handler_USER(data)
			connection.send(msg)
			break
		except socket.error:
			print 'Error transmiting data[TCP]'
			break
	connection.close()

	return

def udp_thread():
	s = udp_server_init()
	while(True):
		udp_server(s)
	return


def udp_server_init():

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
	bytes = len(msg)
	try:
		bytes_sent = s.sendto(msg, cs_addr)
		if bytes_sent != bytes or bytes_sent ≃= -1:
			print 'Error sending data[UDP]'
	except socket.error:
		print 'Error sending data[UDP]'

	return s

def udp_server(s):

	try:
		data,addr=s.recvfrom(BUFFER_SIZE)
		if data==0:
			return None
		while data[-1] != "\n":
			data+= s.recvfrom(BUFFER_SIZE)
		#print data
		msg = handler_CS(data)
		bytes = len(msg)
		try:
			bytes_sent = s.sendto(msg, cs_addr)
			if bytes_sent != bytes or bytes_sent ≃= -1:
				print 'Error sending data[UDP]'
		except socket.error:
			print 'Error sending data[UDP]'
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
		if (len(msg)==3 and isinstance(int(msg[1]), int) and len(msg[1])==5 and msg[2].isalnum() and len(msg[2])==8):
			if find_dir(msg[1],msg[2]):
				n_msg = "LFD "
				dir_path = "/user_" + msg[1] + "/" + msg[2]
				files = os.listdir(dir_path)
				n_msg = n_msg + len(files) + " "
				for file in files:
					mtime = os.path.getmtime(dir_path + "/" + file)
					last_modified_date = datetime.datetime.fromtimestamp(mtime)
					file_size = os.path.getsize(dir_path + "/" + file)
					last_modified_date = str(last_modified_date)
					last_modified_date = last_modified_date.split(".")
					last_modified_date = last_modified_date[0].decode('utf-8').replace("-".decode('utf-8'), ".").encode('utf-8')
					n_msg = n_msg + file + " " + last_modified_date + " " + str(file_size) + " "
				n_msg += "\n"
			else:
				n_msg = "ERR"
		else:
			n_msg = "ERR"

	elif msg[0]=="LSU":
		try:
			if (len(msg)==3 and isinstance(int(msg[1]), int) and len(msg[1])==5 and msg[2].isalnum() and len(msg[2])==8):
				if is_user(msg[1], msg[2]):
					n_msg = "LUR NOK"
				else:
					add_user_bs(msg[1], msg[2])
					n_msg = "LUR OK"
					print "New user: %d", msg[1]
			else:
				n_msg="LUR ERR"
		except ValueError:
			n_msg="LUR ERR"

	elif msg[0]=="DLB":
		if (len(msg)==3 and isinstance(int(msg[1]), int) and len(msg[1])==5):
			if find_dir(msg[1],msg[2]):
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
	path="/user_" + nid + "/" + dir
	shutil.rmtree(path)
	return

def is_user_dir(ud, dir):

	return

def is_user(id, p):
	try:
		f = open("user_" + id + ".txt", "r")
		if p in f.read():
			f.close()
			return True
		else:
			f.close()
			return False
	except IOError:
		return False


def add_user_bs(id, p):
	path="user_"+ id
	file=open(path + ".txt", "w")
	file.write(p)
	file.close()
	os.mkdir(path)
	return

def handler_USER(msg):
	path="/BS/user"
	msg = msg.split(" ")

	if msg[0]=="AUT":
		if is_user(msg[1], msg[2]):
			print "User: %s", msg[1]
			n_msg="AUR OK\n"
		else:
			n_msg="AUR NOK\n"

	elif msg[0]=="UPL":
		if transfer(msg[1], msg[2], msg[3]):
			n_msg="UPR OK\n"
		else:
			n_msg="UPR NOK\n"

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

def find_dir(user, dir):
	return os.path.isdir("/user_" + user + "/" + dir)

def signal_handler(sig, frame):
	###
	sys.exit(0)

def main():
	t1 = Thread(target=udp_thread)
	t2 = Thread(target=tcp_thread)
	t1.daemon = True
	t2.daemon = True
	t1.start()
	t2.start()
	signal.signal(signal.SIGINT, signal_handler)
	signal.pause()


if __name__ =='__main__':
	main()
