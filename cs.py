import socket
import sys
import argparse
import string
import os

parser = argparse.ArgumentParser(description='Process invoking command.')
parser.add_argument('-p', '--CSport', default=58023, type=int, required=False, help='port where the CS server accepts requests')

args = parser.parse_args()

HOST = socket.gethostbyname(socket.gethostname())
BUFFER_SIZE = 80
BACKLOG = 1
CSPORT = int(args.CSport)
HOME = os.getcwd()

cs_address = (HOST, CSPORT)

def utf8len(string):
	return len(string.encode('utf-8'))

def empty_dir(path):
	return len(os.listdir(path)) == 0

def tcp_init():
	s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s_tcp.bind(cs_address)
	s_tcp.listen(BACKLOG)
	connection_tcp, client_address = s_tcp.accept()
	return connection_tcp

def udp_server_init():
	c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	c.bind(cs_address)
	return c

def udp_client_init(address):
	c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	c.bind(address)
	return c

def tcp_receive(connection):
	msg = connection.recv(BUFFER_SIZE)
	if msg == 0:
		return None
	while msg[-1] != "\n":
		msg += connection.recv(BUFFER_SIZE)
	return msg

def udp_receive(connection):
	msg = connection.recvfrom(BUFFER_SIZE)
	if msg == 0:
		return None
	while msg[-1] != "\n":
		msg += connection.recvfrom(BUFFER_SIZE)
	return msg

def udp_send(connection, msg, address):
	total = utf8len(msg)
	sent = 0
	while sent < total:
		sent += connection.sendto(msg, address)

def tcp_send(connection, msg):
	total = utf8len(msg)
	sent = 0
	while sent < total:
		sent += connection.send(msg)

def udp_terminate(connection):
	connection.close()

def tcp_terminate(connection):
	connection.close()

def get_bs_address(d):
	path = HOME + "/" + dirname + "/" + d
	os.chdir(path)
	f = open("ip_port.txt", "r")
	line = f.read()
	line_info = line.split()
	os.chdir(HOME)
	return line_info

def handle_bs(connection, msg):
	data_list = msg.split()
	command = data_list[0]
	reply = ""

	if command == "REG": #completo
		reply += "RGR "
		ip_bs = data_list[1]
		port_bs = data_list[2]
		bs_address = (ip_bs, port_bs)
		if len(data_list) != 3:
			print "Protocol (syntax) error"
			reply += "ERR\n"
			udp_send(connection, reply, bs_address)
			return
		bs = ip_bs + " " + port_bs + "\n"
		try:
			f = open("bs_list", "w")
			f.write(bs)
			f.close()
		except IOError as e:
			print ("Error registering BS: %s" % e)
			reply += "NOK\n"
			udp_send(connection, reply, bs_address)
		print "+BS: " + ip_bs + " " + port_bs
		reply += "OK\n"
		udp_send(connection, reply, bs_address)

	elif command == "UNR": #incompleto
		reply += "UAR "
		ip_bs = data_list[1]
		port_bs = data_list[2]
		bs_address = (ip_bs, port_bs)
		if len(data_list) != 3:
			print "Protocol (syntax) error"
			reply += "ERR\n"
			udp_send(connection, reply, bs_address)
			return
		bs = ip_bs + " " + port_bs + "\n"
		try:
			f = open("bs_list", "r")
			bs_list = f.readlines()
			f.close()
			f = open("bs_list", "w")
			for line in bs_list:
				if line != bs:
					f.write(line)
			f.close()
		except IOError as e:
			print ("Error deregistering BS: %s" % e)
			reply += "NOK\n"
			udp_send(connection, reply, bs_address)
		print "-BS: " + ip_bs + " " + port_bs
		reply += "OK\n"
		udp_send(connection, reply, bs_address)

def handle_user(connection, aut):
	aut_list = aut.split()
	aut_command = aut_list[0]
	reply = ""

	if aut_command == "AUT": #completo
		reply += "AUR "
		user = aut_list[1]
		password = aut_list[2]
		dirname = "user_" + user
		filename = dirname + ".txt"
		if os.path.exists(filename):
			f = open(filename, "r")
			data = f.read()
			if data == password:
				f.close()
				print "User: %s" % user
				reply += "OK\n"
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


		elif command == "RST": #incompleto
			reply += "RSR "
			rst_dir = data_list[1]
			path = HOME + "/" + dirname + "/" + rst_dir
			if os.path.exists(path):
				os.chdir(path)
				f = open("ip_port.txt", "r")
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

		elif command == "LSF": #incompleto
			reply += "LFD"
			user_dir = data_list[1]
			msg = "DLB "
			user_dir = data_list[1]
			bs_info = get_bs_address(user_dir)
			ip_bs = bs_info[0]
			port_bs = bs_info[1]
			bs_address = (ip_bs, port_bs)
			c = udp_client_init(bs_address)
			msg += user + " " + user_dir
			udp_send(c, msg, bs_address)
			bs_msg = udp_receive(c)
			udp_terminate(c)
			bs_msg_list = bs_msg.split()
			response = bs_msg_list[0]
			if response == "LFD":
				reply_list = [n]
				bs_msg_list[2:]
				reply_list += bs_msg_list
				for i in reply_list:
					reply += " " + i
				reply += "\n"
			tcp_send(connection, reply)

		elif command == "DEL": #incompleto
			reply += "DDR "
			msg = "DLB "
			user_dir = data_list[1]
			bs_info = get_bs_address(user_dir)
			ip_bs = bs_info[0]
			port_bs = bs_info[1]
			bs_address = (ip_bs, port_bs)
			c = udp_client_init(bs_address)
			msg += user + " " + user_dir
			udp_send(c, msg, bs_address)
			bs_msg = udp_receive(c)
			udp_terminate(c)
			bs_msg_list = bs_msg.split()
			response = bs_msg_list[0]
			status = bs_msg_list[1]
			if response == "DBR":
				if status == "OK":
					reply += "OK\n"
				elif status == "NOK":
					reply += "NOK\n"
				elif status == "ERR":
					reply += "ERR\n"
			tcp_send(connection, reply)

	return

def user_tcp():
	while True:
		c = tcp_init()
		msg = tcp_receive(c)
		handle_user(c, msg)
		tcp_terminate()
	

def bs_udp():
	c = udp_server_init()
	while True:
		msg = udp_receive(c)
		handle_bs(c, msg)

def main():
	try:
		pid = os.fork()
	except OSError as e:
		print ("Error creating child process: %s" % e)
	if pid == 0:
		bs_udp()
	else:
		user_tcp()

if __name__ == "__main__":
	main()
