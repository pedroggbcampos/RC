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

def receive_message(client_address)
	try:
		s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error, e:
		print "Error creating socket: %s" % e

	client_address = (HOST, CSPORT)
	try:
		s_tcp.bind(client_address)
	except socket.error, e:
		print "Error binding socket: %s" % e

	try:
		s_tcp.listen(BACKLOG)
	except socket.error, e:
		print "Error listening: %s" % e
	try:
		connection_tcp, client_address = s_tcp.accept()
	except socket.error, e:
		print "Error accepting connection: %s" % e

	try:
		data = connection_tcp.recv(BUFFER_SIZE)
	except  , e:
		print "Error receiving message: %s" % e

	return data


while True:
	data_list = receive_message(client_address).split()
	command = data_list[0]

	if command == "AUT":
		

	elif command == "DLU":

	elif command == "BCK":

	elif command == "RST":

	elif command == "LSD":

	elif command == "LSF":

	elif command == "DEL":
