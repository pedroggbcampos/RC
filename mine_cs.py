import socket
import sys
import argparse
import string
	
HOST = ''
BUFFER_SIZE = 80
BACKLOG = 1

parser = argparse.ArgumentParser(description='Process invoking command.')
parser.add_argument('-p', '--CSport', default=58023, type=int, required=False, help='port where the CS server accepts requests')

args = parser.parse_args()

CSPORT = int(args.CSport)

users_dict = {}


def handle_user(msg):
	data_list = msg.split()
	command = data_list[0]
	reply = ""

	if command == "AUT":
		reply += "AUR "
		user = data_list[1]
		password = data_list[2]
		if user in users_dict:
			if users_dict.get(user) == password:
				print "User logged in successfully: %s" % user
				reply += "OK\n"
			else:
				print "User entered wrong password: %s" % user
				reply += "NOK\n"
		else:
			users_dict[user] = password
			print "New user: %s" % user
			reply += "NEW\n"

	else:
		reply = "LFD 123.456.567 50000 3 text.txt dd.mm.yyyy 56 text2.txt dd.mm.yyyy 49 text3.txt dd.mm.yyyy 1000\n"
	return reply
'''
	elif command == "DLU":
	elif command == "BCK":
	elif command == "RST":
	elif command == "LSD":
	elif command == "LSF":
	elif command == "DEL":'''


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

	return reply

	'''elif command == "LFD":
	elif command == "LUR":
	elif command == "DBR":

	return reply'''

def client_tcp():
	try:
		s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	except socket.error, e:
		print "Error creating socket: %s" % e

	server_address = (HOST, CSPORT)
	try:
		s_tcp.bind(server_address)
	except socket.error, e:
		print "Error binding socket: %s" % e

	try:
		s_tcp.listen(BACKLOG)
	except socket.error, e:
		print "Error listening: %s" % e

	try:
		connection_tcp, client_address = s_tcp.accept()
	except socket.error, e:
		return

	try:
		msg = connection_tcp.recv(BUFFER_SIZE)
	except socket.error, e:
		print "Error receiving message: %s" % e

	try:
		connection_tcp.sendall(handle_user(msg))
	except socket.error, e:
		print "Error sending message: %s" % e

	while(True):
		try:
			msg = connection_tcp.recv(BUFFER_SIZE)
			if msg == "":
				break
		except socket.error, e:
			print "Error receiving message: %s" % e

		try:
			connection_tcp.sendall(handle_user(msg))
		except socket.error, e:
			print "Error sending message: %s" % e

	try:
		connection_tcp.close()
	except socket.error, e:
		print "Error closing socket: %s" % e


def server_udp():
	s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s_udp.bind(ip_cs)
	data, bs_address = s_udp.recvfrom(BUFFER_SIZE)
#s_udp.sendto(handle_bs(data), ) #falta ip e port do bs


def main():
	while True:
		client_tcp()

if __name__ == "__main__":
	main()
