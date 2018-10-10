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
	'''utf8len : string -> int
	:: recebe um argumento do tipo string e devolve o tamanho
	dessa string em bytes'''
	return len(string.encode('utf-8'))

def empty_dir(path):
	'''empty_dir : string -> logico
	:: recebe um argumento do tipo string que representa o path para uma
	diretoria, devolve True caso ela esteja vazia e False caso contrario'''	
	return len(os.listdir(path)) == 0

def tcp_init():
	'''tcp_init : {} -> connection
	:: inicia uma ligacao tcp (servidor) e devolve uma connection'''
	s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s_tcp.bind(cs_address)
	s_tcp.listen(BACKLOG)
	connection_tcp, client_address = s_tcp.accept()
	return connection_tcp

def udp_server_init():
	'''udp_server_init : {} -> connection
	:: inicia uma ligacao udp (servidor) e devolve uma connection'''
	c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	c.bind(cs_address)
	return c

def udp_client_init(address):
	'''udp_client_init : {} -> connection
	:: recebe um argumento do tipo address, inicia uma ligacao udp (cliente)
	e devolve uma connection'''
	c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	c.bind(address)
	return c

def tcp_receive(connection):
	'''tcp_receive : connection -> string
	:: recebe um argumento do tipo connection e recebe uma mensagem atraves
	de uma ligacao tcp e devolve-a'''
	msg = connection.recv(BUFFER_SIZE)
	if msg == "":
		return None
	while msg[-1:] != "\n":
		msg += connection.recv(BUFFER_SIZE)
	print msg
	return msg

def udp_receive(connection):
	'''udp_receive : connection -> string
	:: recebe um argumento do tipo connection e recebe uma mensagem atraves
	de uma ligacao udp e devolve-a'''
	print "vou receber"
	msg, bs_address = connection.recvfrom(BUFFER_SIZE)
	print "recebi"
	print msg
	'''if msg == "":
		return None
	while msg[-1:] != "\n":
		msg, bs_address += connection.recvfrom(BUFFER_SIZE)'''
	return msg

def udp_send(connection, msg, address):
	'''udp_send : connection x string x address -> {}
	:: envia uma mensagem atraves de uma ligacao udp'''
	total = len(msg.encode())
	sent = connection.sendto(msg, address)
	print sent
	while sent < total:
		sent += connection.sendto(msg, address)
		print "merda"

def tcp_send(connection, msg):
	total = utf8len(msg)
	sent = 0
	while sent < total:
		sent += connection.send(msg)

def udp_terminate(connection):
	connection.close()

def tcp_terminate(connection):
	connection.close()

def get_bs_address(user, d):
	path = HOME + "/user_" + user + "/" + d
	os.chdir(path)
	f = open("ip_port.txt", "r")
	line = f.read()
	line_info = line.split()
	os.chdir(HOME)
	return line_info

def get_available_bs():
	f = open("bs_list.txt", "r")
	bs = f.readline()
	f.close()
	if bs != "":
		bs_info = bs.split()
		ip_bs = bs_info[0]
		port_bs = bs_info[1]
		return (ip_bs, port_bs)
	else:
		return None

def registered_in_bs(user, bs):
	path = HOME + "/" + "user_" + user
	os.chdir(path)
	f = open("bss.txt", "r")
	bss = f.readlines()
	for l in bss:
		if l == bs:
			os.chdir(HOME)
			return True
	os.chdir(HOME)
	return False

def register_in_bs(user, bs):
	path = HOME + "/" + "user_" + user
	os.chdir(path)
	f = open("bss.txt", "a")
	f.write(bs)
	f.close()
	os.chdir(HOME)

'''def check_protocol(command, list):
	args = len(list)
	if command == "AUT":
		return args == 3
	elif command == "DLU":
		return args = 1
	elif command == "BCK":

	elif command == "RST":

	elif command == "LSD":

	elif command == "LSF":

	elif command == "DEL":

	elif command == "REG":

	elif command == "UNR":

	elif command == "LFD":

	elif command == "LUR":

	elif command == "DBR":'''		

def handle_bs(connection, msg):
	data_list = msg.split()
	command = data_list[0]
	reply = ""

	if command == "REG": #completo
		reply += "RGR "
		ip_bs = data_list[1]
		port_bs = data_list[2]
		bs_address = (ip_bs, int(port_bs))
		if len(data_list) != 3:
			print "Protocol (syntax) error"
			reply += "ERR\n"
			udp_send(connection, reply, bs_address)
			return
		bs = ip_bs + " " + port_bs + "\n"
		try:
			f = open("bs_list.txt", "a")
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
			f = open("bs_list.txt", "r")
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
			f.close()
			if data == password:
				print "User: %s" % user
				reply += "OK\n"
			else:
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
		tcp_send(connection, reply)

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
			bs_address = get_available_bs()
			if bs_address == None:
				print "No BS available"
				reply += " EOF\n"
				tcp_send(connection, reply)
			else:
				user_dir = data_list[1]
				n = data_list[2]
				files = data_list[3:]
				ip_bs = bs_address[0]
				port_bs = bs_address[1]
				reply += ip_bs + " " + port_bs
				if registered_in_bs(user, str(bs_address)):
					msg = "LSF " + user + " " + user_dir + "\n"
					c = udp_client_init(bs_address)
					udp_send(c, msg, bs_address)
					bs_msg = udp_receive(c)
					udp_terminate(c)
					bs_msg_list = bs_msg.split()
					response = bs_msg_list[0]
					n = bs_msg_list[1]
					bs_files = bs_msg_list[2:]
					if response == "LFD":
						reply += " " + n
						for i in bs_files:
							reply += " " + i
						reply += "\n"
					tcp_send(connection, reply)
				else:
					register_in_bs(user, str(bs_address))
					msg = "LSU " + user + " " + password + "\n"
					c = udp_client_init(bs_address)
					udp_send(c, msg, bs_address)
					bs_msg = udp_receive(c)
					udp_terminate(c)
					bs_msg_list = bs_msg.split()
					response = bs_msg_list[0]
					status = bs_msg_list[1]
					if response == "LUR":
						if status == "OK":
							reply += "OK\n"
						elif status == "NOK":
							reply += "NOK\n"
						elif status == "ERR":
							reply += "ERR\n"
					tcp_send(connection, reply)

		elif command == "RST": #completo
			reply += "RSR "
			rst_dir = data_list[1]
			bs_info = get_bs_address(user, rst_dir)
			ip_bs = bs_info[0]
			port_bs = bs_info[1]
			reply += ip_bs + " " + port_bs
			tcp_send(connection, reply)

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
			bs_info = get_bs_address(user, user_dir)
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
			bs_info = get_bs_address(user, user_dir)
			ip_bs = bs_info[0]
			port_bs = bs_info[1]
			bs_address = (ip_bs, port_bs)
			c = udp_client_init(bs_address)
			msg += user + " " + user_dir + "\n"
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
		print "Start tcp"
		c = tcp_init()
		print "Init check tcp"
		msg = tcp_receive(c)
		print "Receive check tcp"
		handle_user(c, msg)
		print "Handle check tcp"
		tcp_terminate(c)
		print "Terminate check tcp"
	

def bs_udp():
	print "Start udp"
	c = udp_server_init()
	print "Init check udp"
	while True:
		print "start while udp"
		msg = udp_receive(c)
		print "Receive check udp"
		handle_bs(c, msg)
		print "Handle check udp"

def main():
	print HOST
	print "\n"
	print CSPORT
	print "\n"
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