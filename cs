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
	return len(s.encode('utf-8'))

def empty_dir(path):
	return len(os.listdir(path)) == 0

def handle_bs(msg):
	data_list = msg.split()
	command = data_list[0]
	reply = ""

	if command == "REG":
		reply += "RGR "
		ip_bs = data_list[1]
		port_bs = data_list[2]

	elif command == "UNR":
		reply += "UAR "
		ip_bs = data_list[1]
		port_bs = data_list[2]
	'''elif command == "LFD":
	elif command == "LUR":
	elif command == "DBR":'''
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
	if msg == 0:
		return None
	while msg[-1] != "\n":
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
			reply += "LFD "

		elif command == "DEL": #incompleto
			reply += "DDR "

	return

def user_tcp():
	c = tcp_init()
	msg = tcp_receive(c)
	handle_user(c, msg)
	tcp_terminate()

def bs_udp():
	s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s_udp.bind(ip_cs)
	data, bs_address = s_udp.recvfrom(BUFFER_SIZE)
#s_udp.sendto(handle_bs(data), ) #falta ip e port do bs


def main():
	while True:
		user_tcp()

if __name__ == "__main__":
	main()
