#!/usr/bin/env python
import socket
import sys
import argparse
import string
import os
import multiprocessing

#Faltam os timeouts

parser = argparse.ArgumentParser(description='Process invoking command.')
parser.add_argument('-p', '--CSport', default=58023, type=int, required=False, help='port where the CS server accepts requests')

args = parser.parse_args()

HOST = socket.gethostbyname(socket.gethostname())
BUFFER_SIZE = 80
BACKLOG = 1
CSPORT = int(args.CSport)
HOME = os.getcwd()

cs_address = (HOST, CSPORT)

lock = multiprocessing.Lock()

def empty_dir(path):
	'''empty_dir : string -> logico
	:: recebe um argumento do tipo string que representa o path para uma
	diretoria, devolve True caso ela esteja vazia e False caso contrario'''	
	return len(os.listdir(path)) == 0

def tcp_init():
	'''tcp_init : {} -> connection
	:: inicia uma ligacao tcp (servidor) e devolve uma connection'''
	try:
		s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s_tcp.bind(cs_address)
		s_tcp.listen(BACKLOG)
		connection_tcp, client_address = s_tcp.accept()
	except socket.error as e:
		print("Error initiating tcp connection: %s" % e)
	return connection_tcp

def udp_server_init():
	'''udp_server_init : {} -> connection
	:: inicia uma ligacao udp (servidor) e devolve uma connection'''
	try:
		c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		c.bind(cs_address)
	except socket.error as e:
		print("Error initiating udp server connection: %s" % e)
	return c

def udp_client_init():
	'''udp_client_init : {} -> connection
	:: inicia uma ligacao udp (cliente) e devolve uma connection'''
	try:
		c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	
	except socket.error as e:
		print("Error initiating udp client connection: %s" % e)
	return c

def tcp_receive(connection):
	'''tcp_receive : connection -> string
	:: recebe um argumento do tipo connection e recebe uma mensagem atraves
	de uma ligacao tcp e devolve-a'''
	try:
		msg = connection.recv(BUFFER_SIZE)
		if msg == "":
			return None
		while msg[-1:] != "\n":
			msg += connection.recv(BUFFER_SIZE)
	except socket.error as e:
		print("Error receiving message from tcp connection: %s" % e)
	return msg

def udp_receive(connection):
	'''udp_receive : connection -> string
	:: recebe um argumento do tipo connection e recebe uma mensagem atraves
	de uma ligacao udp e devolve-a'''
	try:
		msg, bs_address = connection.recvfrom(BUFFER_SIZE)
	except socket.error as e:
		print("Error receiving message from udp connection: %s" % e)
	return (msg, bs_address)

def udp_send(connection, msg, address):
	'''udp_send : connection x string x address -> {}
	:: envia uma mensagem atraves de uma ligacao udp'''
	total = len(msg.encode())
	try:
		sent = connection.sendto(msg, address)
		print address == ('192.168.1.2', 59000)
	except socket.error as e:
		print("Error sending message through udp connection: %s" % e)
	#if sent != total :
		#tratar erro udp

def tcp_send(connection, msg):
	'''tcp_send : connection x string -> {}
	:: recebe um argumento do tipo connection e uma string que representa a mensagem
	a enviar e envia a mensagem atraves de uma ligacao tcp'''
	total = len(msg.encode())
	sent = 0
	while sent < total:
		try:
			sent += connection.send(msg)
		except socket.error as e:
			print("Error sending message through tcp connection: %s" % e)

def udp_terminate(connection):
	'''udp_terminate : connection -> {}
	:: recebe um argumento do tipo connection e fecha-a'''
	try:
		connection.close()
	except socket.error as e:
		print("Error closing udp connection: %s" % e)

def tcp_terminate(connection):
	'''tcp_terminate : connection -> {}
	:: recebe um argumento do tipo connection e fecha-a'''
	try:
		connection.close()
	except socket.error as e:
		print("Error closing tcp connection: %s" % e)

def get_bs_address(user, d):
	'''get_bs_address : string x string -> list
	:: recebe um argumento do tipo string que representa um utilizador, uma string que
	representa uma diretoria e devolve uma lista com o ip e o porto do servidor BS que
	guardou essa diretoria'''
	path = HOME + "/user_" + user + "/" + d
	try:
		os.chdir(path)
		f = open("ip_port.txt", "r")
		line = f.read()
		line_info = line.split()
		os.chdir(HOME)
	except IOError as e:
		print("Error getting BS address: %s" % e)
	return line_info

def get_available_bs():
	'''get_available_bs : {} -> list
	:: consulta a lista de BS's registados caso haja um disponivel devolve uma lista com
	o seu ip e porto, caso contrario devolve None'''
	try:
		f = open("bs_list.txt", "r")
		bs = f.readline()
		f.close()
	except IOError as e:
		print("Error getting available BS: %s" % e)
	if bs != "":
		bs_info = bs.split()
		return bs_info
	else:
		return None

def register_in_bs(user, bs):
	'''register_in_bs : string x string -> {}
	:: recebe um argumento do tipo string que representa um utilizador e uma string que
	representa um servidor BS e regista esse BS no ficheiro de servidores BS onde esse
	utilizador esta registado'''
	filename = "bss_" + user + ".txt"
	try:
		f = open(filename, "a")
		f.write(bs)
		f.close()
	except IOError as e:
		print("Error registering in BS: %s" % e)

def registered_in_bs(user, bs):
	'''registered_in_bs : string x string -> logico
	:: recebe um argumento do tipo string que representa um utilizador e uma string que
	representa um servidor BS e devolve True caso esse utilizador ja se tenha registado
	nesse servidor BS'''
	filename = "bss_" + user + ".txt"
	try:
		f = open(filename, "r")
		bss = f.readlines()
		f.close()
	except IOError as e:
		print("Error checking for regist in BS: %s" % e)
	for l in bss:
		if l == bs:
			return True
	return False

def check_protocol(command, args):
	'''check_protocol : string x list -> logico
	:: recebe um argumento do tipo string que representa o tipo de mensagem recebida e uma
	lista com os restantes argumentos da mensagem, devolve True caso a mensagem esteja de
	acordo com o protocolo e False caso contrario'''
	n_args = len(args)
	#print "vou verificar uma mensagem com len " + str(n_args)
	if command == "AUT":
		return n_args == 3
	elif command == "DLU":
		return n_args == 1
	elif command == "BCK":
		n = int(args[2])
		return n_args == (3+n*4)
	elif command == "RST":
		return n_args == 2
	elif command == "LSD":
		return n_args == 1
	elif command == "LSF":
		return n_args == 2
	elif command == "DEL":
		return n_args == 2
	elif command == "REG":
		return n_args == 3
	elif command == "UNR":
		return n_args == 3
	elif command == "LFD":
		n = int(args[1])
		return n_args == (2+n*4)
	elif command == "LUR":
		return n_args == 2
	elif command == "DBR":
		return n_args == 2
	return False

def handle_bs(connection, msg, bs_address):
	reply = ""
	data_list = msg.split()
	command = data_list[0]
	ip_bs = data_list[1]
	port_bs = data_list[2]
	bs = ip_bs + " " + port_bs + "\n"

	if command == "REG": #completo
		reply += "RGR "
		if not check_protocol(command, data_list):
			print "Protocol (syntax) error"
			reply += "ERR\n"
		else:
			try:
				f = open("bs_list.txt", "a")
				f.write(bs)
				f.close()
			except IOError as e:
				print ("Error registering BS: %s" % e)
				reply += "NOK\n"

			print "+BS: " + ip_bs + " " + port_bs
			reply += "OK\n"

	elif command == "UNR": #incompleto falta saber se o bs pode mesmo ir embora
		reply += "UAR "
		if not check_protocol(command, data_list):
			print "Protocol (syntax) error"
			reply += "ERR\n"
		else:
			try:
				f = open("bs_list.txt", "r")
				bs_list = f.readlines()
				f.close()
				os.remove("bs_list.txt")
				f = open("bs_list.txt", "w")
				for line in bs_list:
					if line != bs:
						f.write(line)
				f.close()
			except IOError as e:
				print ("Error deregistering BS: %s" % e)
				reply += "NOK\n"
			print "-BS: " + ip_bs + " " + port_bs
			reply += "OK\n"
	udp_send(connection, reply, bs_address)

def handle_user(connection, aut, lock):
	aut_list = aut.split()
	aut_command = aut_list[0]
	reply = ""

	if aut_command == "AUT": #completo
		reply += "AUR "
		if not check_protocol(aut_command, aut_list):
			print "Protocol (syntax) error"
			reply += "ERR\n"
		else:
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
				f=open("bss_" + user + ".txt", "w")
				f.close()
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
			if not check_protocol(command, data_list):
				print "Protocol (syntax) error"
				reply += "ERR\n"
			else:
				print "   Delete user request"
				path = HOME + "/" + dirname
				if empty_dir(path):
					os.rmdir(dirname)
					os.remove(filename)
					os.remove("bss_" + user + ".txt")
					print "User deleted: %s" % user
					reply += "OK\n"
				else:
					print "Failed to delete user: %s" % user
					reply += "NOK\n"

		elif command == "BCK": #incompleto
			reply += "BKR "
			if not check_protocol(command, data_list):
				print "Protocol (syntax) error"
				reply += "ERR\n"
			else:
				bs_info = get_available_bs()
				if bs_info == None:
					print "No BS available"
					reply += " EOF\n"
					tcp_send(connection, reply)
				else:
					user_dir = data_list[1]
					n = data_list[2]
					files = data_list[3:]
					ip_bs = bs_info[0]
					port_bs = bs_info[1]
					bs_address = (ip_bs, int(port_bs))
					reply += ip_bs + " " + port_bs
					test_bs = ip_bs + " " + port_bs + "\n"
					print "   "+command+" "+user+" "+user_dir+" "+ip_bs+" "+port_bs
					if registered_in_bs(user, test_bs):
						msg = "LSF " + user + " " + user_dir + "\n"
						lock.acquire()
						c = udp_client_init()
						udp_send(c, msg, bs_address)
						bs_msg, bs_aux_addr = udp_receive(c)
						udp_terminate(c)
						lock.release()
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
						register_in_bs(user, test_bs)
						msg = "LSU " + user + " " + password + "\n"
						lock.acquire()
						c = udp_client_init()
						udp_send(c, msg, bs_address)
						bs_msg, bs_aux_addr = udp_receive(c)
						udp_terminate(c)
						lock.release()
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

		elif command == "RST": #completo
			reply += "RSR "
			if not check_protocol(command, data_list):
				print "Protocol (syntax) error"
				reply += "ERR\n"
			else:
				rst_dir = data_list[1]
				bs_info = get_bs_address(user, rst_dir)
				ip_bs = bs_info[0]
				port_bs = bs_info[1]
				reply += ip_bs + " " + port_bs
				print "   Restore " + rst_dir

		elif command == "LSD": #completo
			reply += "LDR "
			if not check_protocol(command, data_list):
				print "Protocol (syntax) error"
				reply += "ERR\n"
			else:
				print "   List request"
				path = HOME + "/" + dirname
				dirs = os.listdir(path)
				n = len(dirs)
				reply += str(n) 
				for d in dirs:
					reply += " " + d
				reply += "\n"

		elif command == "LSF": #incompleto
			reply += "LFD"
			if not check_protocol(command, data_list):
				print "Protocol (syntax) error"
				reply += " ERR\n"
			else:
				user_dir = data_list[1]
				msg = "DLB "
				user_dir = data_list[1]
				bs_info = get_bs_address(user, user_dir)
				ip_bs = bs_info[0]
				port_bs = bs_info[1]
				bs_address = (ip_bs, int(port_bs))
				lock.acquire()
				c = udp_client_init()
				msg += user + " " + user_dir
				udp_send(c, msg, bs_address)
				bs_msg, bs_aux_addr = udp_receive(c)
				udp_terminate(c)
				lock.release()
				bs_msg_list = bs_msg.split()
				response = bs_msg_list[0]
				if response == "LFD":
					reply_list = [n]
					bs_msg_list[2:]
					reply_list += bs_msg_list
					for i in reply_list:
						reply += " " + i
					reply += "\n"

		elif command == "DEL": #incompleto
			reply += "DDR "
			if not check_protocol(command, data_list):
				print "Protocol (syntax) error"
				reply += "ERR\n"
			else:
				msg = "DLB "
				user_dir = data_list[1]
				bs_info = get_bs_address(user, user_dir)
				ip_bs = bs_info[0]
				port_bs = bs_info[1]
				bs_address = (ip_bs, int(port_bs))
				lock.acquire()
				c = udp_client_init()
				msg += user + " " + user_dir + "\n"
				udp_send(c, msg, bs_address)
				bs_msg, bs_aux_addr = udp_receive(c)
				udp_terminate(c)
				lock.release()
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

def user_tcp(lock):
	while True:
		#print "Start tcp"
		c = tcp_init()
		#print "Init check tcp"
		msg = tcp_receive(c)
		#print "Receive check tcp"
		handle_user(c, msg, lock)
		#print "Handle check tcp"
		tcp_terminate(c)
		#print "Terminate check tcp"
	

def bs_udp(lock):
	#print "Start udp"
	c = udp_server_init()
	#print "Init check udp"
	while True:
		#print "start while udp"
		msg, bs_address = udp_receive(c)
		#print "Receive check udp"
		handle_bs(c, msg, bs_address)
		#print "Handle check udp"

def main():
	try:
		pid = os.fork()
	except OSError as e:
		print ("Error creating child process: %s" % e)
	if pid == 0:
		bs_udp(lock)
	else:
		user_tcp(lock)

if __name__ == "__main__":
	main()
