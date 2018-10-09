import socket
import sys
import argparse
import string
import os
from threading import Thread

parser = argparse.ArgumentParser(description='Process invoking command.')
parser.add_argument('-p', '--CSport', default=58023, type=int, required=False, help='port where the CS server accepts requests')

args = parser.parse_args()

HOST = ""
BUFFER_SIZE = 80
BACKLOG = 1
CSPORT = int(args.CSport)
HOME = os.getcwd()

cs_address = (HOST, CSPORT)

curr_user = None

available_bs = []

def utf8len(s):
	return len(s.encode('utf-8'))

def empty_dir(path):
	return len(os.listdir(path)) == 0

def read_file(file_path):
	file = open(file_path, mode="r")
	content = file.read()
	file.close()
	return content

def handle_bs(msg):
	data_list = msg.split()
	command = data_list[0]
	reply = ""

	if command == "REG":
		reply += "RGR "
		ip_bs = data_list[1]
		port_bs = data_list[2]
		available_bs.append((ip_bs, port_bs))
		reply += "OK\n"
	elif command == "UNR":
		reply += "UAR "
		ip_bs = data_list[1]
		port_bs = data_list[2]
		reply += "OK\n"
		available_bs.remove((ip_bs, port_bs))

	elif command == "LFD":
		bite = 4
		msg = msg[bite:]
		reply = msg

	elif command == "DBR":
		if data_list[1] == "OK\n":
			reply = "OK"
		elif data_list[1] == "NOK\n":
			reply = "NOK"
	elif command == "LUR":
		if data_list[1] == "OK\n":
			reply = "OK"
		elif data_list[1] == "NOK\n":
			reply = "NOK"
		elif data_list[1] == "ERR\n":
			reply = "ERR"
	return reply

def tcp_init():
	s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s_tcp.bind(cs_address)
	s_tcp.listen(BACKLOG)
	connection_tcp, client_address = s_tcp.accept()
	return connection_tcp

def tcp_receive(connection):
	msg = connection.recv(BUFFER_SIZE)
	if msg == 0 or msg == "":
		return None
	while msg[-1:] != "\n":
		msg += connection.recv(BUFFER_SIZE)
	return msg

def tcp_send(connection, msg):
	total = utf8len(msg)
	sent = 0
	while sent < total:
		sent += connection.send(msg)

def tcp_terminate(connection):
	connection.close()

def handle_user(connection, aut):
	aut_list = aut.split()
	aut_command = aut_list[0]
	reply = ""

	if aut_command == "AUT": #completo
		reply += "AUR "
		user = aut_list[1]
		password = aut_list[2]
		global curr_user
		dirname = "user_" + user
		filename = dirname + ".txt"
		if os.path.exists(filename):
			f = open(filename, "r")
			data = f.read()
			if data == password:
				f.close()
				print "User: %s" % user
				reply += "OK\n"
				curr_user = user
				tcp_send(connection, reply)
			else:
				f.close()
				print "User entered wrong password: %s" % user
				reply += "NOK\n"
				tcp_send(connection, reply)
				return
		else:
			f = open(filename, "w")
			f.write(password)
			f.close()
			os.mkdir(dirname)
			print "New user: %s" % user
			reply += "NEW\n"
			curr_user = user
			tcp_send(connection, reply)
			return

	msg = tcp_receive(connection)

	if msg != None:
		data_list = msg.split()
		command = data_list[0]
		reply = ""

		if command == "DLU": #completo
			reply += "DLR "
			path = HOME + "/" + dirname
			if empty_dir(path):
				os.rmdir(dirname)
				os.remove(filename)
				print "User deleted: %s" % user
				reply += "OK\n"
				tcp_send(connection, reply)
			else:
				print "Failed to delete user: %s" % user
				reply += "NOK\n"
				tcp_send(connection, reply)

		elif command == "BCK": #incompleto
			reply += "BKR "
			if len(available_bs) == 0:
				reply += "EOF\n"
			else:
				p = ""
				path = HOME + "/" + dirname

				bs = available_bs[0]
				has_done_backup = False
				for x in os.listdir(path):
					if os.path.isdir(x):
						content = read_file(path + "/" + x + "/IP_port.txt")
						ip_port = content.split(" ")
						if (ip_port[0] == bs[0] and ip_port[1] == bs[1]):
							has_done_backup = True
							break
				if not has_done_backup:
					mens = "LSU " + user + " " + password + "\n"
					data = bs_udp_s_r(mens)
					if data == "OK":
						bite = 3 + len(dirname) + 2
						mens = msg[bite:]
						reply += bs[0] + " " + bs[1] + " " + mens +"\n"
					else:
						reply += "ERR"

				elif has_done_backup:
					mens = "LSF" + user + " " + directory + "\n"
					data = bs_udp_s_r(mens)
					reply += bs[0] + " " + bs[1] + " " + data +"\n"

			tcp_send(connection, reply)


		elif command == "RST": #incompleto
			reply += "RSR "
			rst_dir = data_list[1]
			path = HOME + "/" + dirname + "/" + rst_dir
			if os.path.exists(path):
				os.chdir(path)
				f = open("IP_port.txt", "r")
				ip_port = f.read()

		elif command == "LSD": #completo
			print "List request"
			reply += "LDR "
			path = HOME + "/" + dirname
			dirs = os.listdir(path)
			n = len(dirs)
			reply += n 
			for d in dirs:
				reply += " " + d
			reply += "\n"
			tcp_send(connection, reply)

		elif command == "LSF":
			user = aut_list[1]
			directory = data_list[1]
			mens = "LSF" + user + " " + directory + "\n"
			data = bs_udp_s_r(mens)
			reply += "LFD "
			path = HOME + "/" + dirname + "/" + directory + "/IP_port.txt"
			try:
				ip_port = read_file(path)
				ip_port = ip_port.split(" ")
				reply += ip_port[0] + " " + ip_port[1] + " " + data
			except e:
				reply += "NOK"
			tcp_send(connection, reply)

		elif command == "DEL":
			reply += "DDR "
			user = aut_list[1]
			directory = data_list[1]
			mens = "DLB " + user + " " + directory + "\n"
			data = bs_udp_s_r(mens)
			if data == "OK":
				reply += "OK\n"
			else:
				reply += "NOK\n"
			tcp_send(connection, reply)

	return

def user_tcp():
	c = tcp_init()
	msg = tcp_receive(c)
	handle_user(c, msg)
	tcp_terminate(c)

def bs_udp_r_s():
	try:
		s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	except socket.error:
		print 'Error creating socket [UDP]'
	try:
		s_udp.bind(cs_address)
	except socket.error:
		print 'Error binding socket to address[UDP]'
	print(cs_address)

	data, bs_address = s_udp.recvfrom(BUFFER_SIZE)
	if data == "":
		return
	else:
		print(data)
		s_udp.sendto(handle_bs(data), bs_address)
		print(bs_address)
		s_udp.close()

def bs_udp_s_r(msg):
	try:
		s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	except socket.error:
		print 'Error creating socket [UDP]'

	s_udp.sendto(msg, bs_address)
	print(bs_address)
	try:
		s_udp.bind(cs_address)
	except socket.error:
		print 'Error binding socket to address[UDP]'
	print(cs_address)

	data, bs_address = s_udp.recvfrom(BUFFER_SIZE)
	if data == "":
		return ""
	else:
		s_udp.close()
		return handle_bs(data)

def tcp_thread():
	while True:
		user_tcp()

def udp_thread():
	while True:
		bs_udp_r_s()

def main():
	t1 = Thread(target=udp_thread)
	t2 = Thread(target=tcp_thread)
	t1.daemon = True
	t2.daemon = True
	t1.start()
	t2.start()
	while(True):
		pass

if __name__ == "__main__":
	main()
