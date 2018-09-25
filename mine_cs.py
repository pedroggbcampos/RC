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

try:
	s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error, e:
	print "Error creating socket: %s" % e

server_address = (HOST, CSPORT)
s_tcp.bind(server_address)
s_tcp.listen(BACKLOG)
connection_tcp, client_address = s_tcp.accept()

try:
	data = connection_tcp.recv(BUFFER_SIZE)
except  , e:
	print "Error receiving message: %s" % e

login_check(data)



while True:
	pass


def login_check(data):
	data_list = data.split()
	if data_list[0] != "AUT" or len(data_list[1]) != 5 or not data_list[1].isdigit():
		return False
	for c in data_list[2]:
		if not c.isdigit() and not c.isalpha():
			return False
	return True

while True:
	data_list = receive_message().split()
	command = data_list[0]

	if command == "DLU":

	elif command == "BCK":

	elif command == "RST":

	elif command == "LSD":

	elif command == "LSF":

	elif command == "DEL":
