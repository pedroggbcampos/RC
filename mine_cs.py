import socket
import sys
import argparse
import string
	
HOST = socket.gethostbyname(socket.gethostname())
BUFFER_SIZE = 80
BACKLOG = 1

parser = argparse.ArgumentParser(description='Process invoking command.')
parser.add_argument('-p', '--CSport', default=58023, type=int, required=False, help='port where the CS server accepts requests')
args = parser.parse_args()
CSPORT = int(args.CSport)
users_dict = {}

ip_cs = (HOST, CSPORT)

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
				print "User logged in successefully: %s" % user
				reply += "OK\n"
			else:
				print "User entered wrong password: %s" % user
				reply += "NOK\n"
		else:
			users_dict[user] = password
			print "New user: %s" % user
			reply += "NEW\n"
	return reply
'''
	elif command == "DLU":

	elif command == "BCK":

	elif command == "RST":

	elif command == "LSD":

	elif command == "LSF":

	elif command == "DEL":'''



def client_tcp():
	s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	
	s_tcp.bind(ip_cs)
	s_tcp.listen(BACKLOG)
	connection_tcp, client_address = s_tcp.accept()
	msg = connection_tcp.recv(BUFFER_SIZE)
	connection_tcp.sendall(handle_user(msg))
	connection_tcp.close()

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

def server_udp():
	s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s_udp.bind(ip_cs)
	data, bs_address = s_udp.recvfrom(BUFFER_SIZE)
	#s_udp.sendto(handle_bs(data), ) #falta ip e port do bs

def main():
	client_tcp()

if __name__ == "__main__":
    main()
