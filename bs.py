import sys
import socket
import argparse
import string
import os
import shutil
import signal
from threading import Thread

BUFFER_SIZE=80

parser= argparse.ArgumentParser(description='Process invoking command.')
parser.add_argument('-b', '--BSport', default=59000, type=int, required=False, help='port where the BS server accepts requests')
parser.add_argument('-n', '--CSname', default= socket.gethostname(), type=str, required=False, help='name of the machine where the CS runs')
parser.add_argument('-p', '--CSport', default=58023, type=int, required=False, help='port where the CS server accepts requests')

args = parser.parse_args()

BSPORT= int(args.BSport)
CSNAME= str(args.CSname)
CSPORT= int(args.CSport)

IPBS = socket.gethostbyname(socket.gethostname())

udp_connection = None
bs_addr = ("", BSPORT)


def tcp_thread():
	udp_server_register()
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
	global udp_connection
	udp_connection = s
	while(True):
		udp_server(s)
	return

def udp_server_register():
	ip_cs = socket.gethostbyname(CSNAME)

	cs_addr =(ip_cs, CSPORT)
	print cs_addr

	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	except socket.error:
		print 'Error creating socket [UDP]'
		sys.exit()
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


	msg = "REG " + str(IPBS) + " " + str(BSPORT) + "\n"
	n_bytes = len(msg)
	try:
		bytes_sent = s.sendto(msg, cs_addr)
		if bytes_sent != n_bytes or bytes_sent == -1:
			print 'Error sending data[UDP]'
	except socket.error:
		print 'Error sending data[UDP]'

	print "sent"
	print msg

	data, cs_address = s.recvfrom(BUFFER_SIZE)
	print (data)
	handler_CS(data)

	s.close()


def udp_server_init():

	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	except socket.error:
		print 'Error creating socket [UDP]'
		sys.exit()
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	try:
		s.bind(bs_addr)
	except socket.error:
		print 'Error binding socket to address[UDP]'
		sys.exit()

	return s

def udp_server(s):

	ip_cs = socket.gethostbyname(CSNAME)

	cs_addr =(ip_cs, CSPORT)

	try:
		data,addr=s.recvfrom(BUFFER_SIZE)
		if data==0:
			return None
		while data[-1] != "\n":
			data+= s.recvfrom(BUFFER_SIZE)
		print (data)
		msg = handler_CS(data)
		bytes = len(msg)
		try:
			bytes_sent = s.sendto(msg, cs_addr)
			if bytes_sent != bytes or bytes_sent == -1:
				print 'Error sending data[UDP]'
		except socket.error:
			print 'Error sending data[UDP]'
	except socket.error:
		print 'Error transmiting data[UDP]'

	return

def udp_unregister():

	ip_cs = socket.gethostbyname(CSNAME)

	cs_addr =(ip_cs, CSPORT)

	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	except socket.error:
		print 'Error creating socket [UDP]'
		sys.exit()
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	try:
		s.bind(bs_addr)
	except socket.error:
		print 'Error binding socket to address[UDP]'
		sys.exit()

	msg = "UNR " + IPBS + " " + str(BSPORT)
	bytes = len(msg)
	try:
		bytes_sent = s.sendto(msg, cs_addr)
		if bytes_sent != bytes or bytes_sent == -1:
			print 'Error sending data[UDP]'
	except socket.error:
		print 'Error sending data[UDP]'
	try:
		data, addr=s.recvfrom(BUFFER_SIZE)
		if data == 0:
			return None
		while data[-1] != "\n":
			data+= s.recvfrom(BUFFER_SIZE)
		msg = data.split(" ")
		if msg[1] == "UAR":
			if msg[2] == "OK\n":
				s.close()
				return "OK"
			elif msg[2] == "NOK\n":
				s.close()
				return "NOK" 
			else:
				s.close()
				return "ERR"
		else:
			s.close()
			return "ERR"
	except socket.error:
		s.close()
		return "ERR"

	s.close()
	return "ERR"


def handler_CS(msg):
	path="/BS/user"

	msg = msg.split(" ")
	n_msg = "ERR"

	if msg[0]=="RGR":
		if (msg[1]=="NOK\n" or msg[1]=="ERR\n"):
			os._exit(0)

	elif msg[0]=="UAR":
		if (msg[1]=="NOK\n" or msg[1]=="ERR\n"):
			os._exit(0)

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
		dir=msg[1]
		os.mkdir(dir)
		no_files=msg[2]
		bite=len(msg[1])+len(no_files)+2
		msg=msg[bite:]
		print dir+"\n"
		for i in range(0, int(no_files)):
			f_info=msg.split(" ")
			bite = len(f_info[0]) + len(f_info[1]) + len(f_info[2]) + 3
			msg=msg[bite:]
			f_name=f_info[0]
			f_date=f_info[1]
			f_size=f_info[2]
			
			file=open(dir + "/" + f_name, "wb")
			for c in range(int(f_size)):
				f_content+=file.write(msg[c])
			file.close()

			print f_name + f_size + " Bytes received" + "\n"

			bite = int(f_info[2]) + 1
			msg = msg[bite:]

		n_msg="UPR OK"
		#falta o NOK
				
	elif msg[0]=="RSB":
		if (len(msg)==2 and isinstance(msg[1], str)):
			if find_dir(msg[1]):
				n_msg = "RBR "
				path = "/" + msg[1] 
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

					file = open(path, mode="rb")
					content = read_file(path)
					n_msg += content +" "


				n_msg += "\n"
			else:
				n_msg="RBR EOF"
		else:
			n_msg="RBR ERR"

	else:
		n_msg="ERR"

	return n_msg


def read_file(file_path):
	file = open(file_path, mode="rb")
	content = file.read()
	file.close()
	return content

def transfer(dir, n, files):
	return

def find_dir(user, dir):
	return os.path.isdir("/user_" + user + "/" + dir)

def signal_handler(sig, frame):
	msg = udp_unregister()
	if msg == "OK":
		print("\n")
		sys.exit(0)
	elif msg =="NOK":
		signal.signal(signal.SIGINT, signal_handler)
		return


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
