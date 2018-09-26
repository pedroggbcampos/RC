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

def handle(msg):
	data_list = msg.split()
	command = data_list[0]

	reply = ""

	if command == "AUT":

		reply += "AUR "
		user = data_list[1]
		password = data_list[2]
		if user in users_dict:
			if users_dict.get(user) == password:
				print "User logged in successefully: %s" % user
				reply += "OK\n"
			else:
				print "User entered wrong password: %s" % user
				reply += "NOK\n"
		else:
			users_dict[user] = password
			print "New user: %s" % user
			reply += "NEW\n"

	elif command == "DLU":

		reply += "DLR "


	elif command == "BCK":

	elif command == "RST":

	elif command == "LSD":

	elif command == "LSF":

	elif command == "DEL":

	return reply

def client_tcp():
	try:
		s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
		print "Error accepting: %s" % e

	try:
		msg = connection_tcp.recv(BUFFER_SIZE)
	except socket.error, e:
		print "Error receiving message: %s" % e

	try:
		connection_tcp.sendall(handle(msg))
	except socket.error, e:
		print "Error sending message: %s" % e

	try:
		connection_tcp.close()
	except socket.error, e:
		print "Error closing socket: %s" % e


while True:
	client_tcp()
	break
