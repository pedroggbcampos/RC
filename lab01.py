#!/usr/bin/env python
import socket
import sys

HOST = 'localhost'
PORT = 58000
BUFFER_SIZE = 80

if len(sys.argv) == 2:
	print ("Could not run - Correct format is : ./user [-n CSname] [-p CSport]\n")
	exit()
elif len(sys.argv) == 3:
	if sys.argv[1] == "-n":
		HOST = sys.argv[2]
	elif sys.argv[1] == "-p":
		PORT = sys.argv[2]
	else:
		print ("Could not run - Correct format is : ./user.py [-n CSname] [-p CSport]\n")
		exit()
elif len(sys.argv) == 5:
	if sys.argv[1] == "-n":
		HOST = sys.argv[2]
	else:
		print ("Could not run - Correct format is : ./user [-n CSname] [-p CSport]\n")
		exit()
	if sys.argv[3] == "-p":
		PORT = sys.argv[4]
	else:
		print ("Could not run - Correct format is : ./user [-n CSname] [-p CSport]\n")
		exit()
elif len(sys.argv) != 1:
	print ("Could not run - Correct format is : ./user [-n CSname] [-p CSport]\n")
	exit()


def main():
	while(True):
		command = raw_input()
		command = command.split(" ")
		action = command[0]
		if action == "login":
			while(True):
				if len(command) != 3:
					print ("Invalid number of arguments - Correct format is : login [user] [password]\n")
					break
				elif len(command) == 3:
					user = command[1]
					password = command[2]
					try:
						number = int(user)
					except ValueError:
						print ("Invalid user - Username must be a positive 5 digit number\n")
						break
					if number < 10000 or number > 99999:
						print ("Invalid user - Username must be a positive 5 digit number\n")
						break
					if not password.isalnum() or len(password) != 8 :
						print ("Invalid pass - Password must have 8 alphanumerical characters, restricted to letters and numbers\n")
						break
					try:
						fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					except socket.error, e:
						print ("Error creating socket: %s" % e)
						fd = None

					server_address = (HOST, PORT)
					try:
						fd.connect(server_address)
					except socket.error, e:
						print ("Error connecting to server address %s : %s" % (server_address, e))
						exit()

					try:
						msg = "AUT" + " " + user + " " + password 
						fd.sendall(msg)
					except socket.error, e:
						print ("Error sending message: '%s' : %s" % (msg, e))

					try:
						data = fd.recv(BUFFER_SIZE)
						print (data)
					except socket.error, e:
						print ("Error receiving message: %s" % e)

					status = data.split(" ")
					if status[0] != "AUR":
						print ("Error authenticating")
						break
					if status[1] == "OK":
						print("Logged in. Successful authentication")
					elif status[1] == "NOK":
						print("Authentication failed. Incorrect password")
					elif status[1] == "NEW":
						print("Logged in. New user created")
					try:
						fd.close
					except socket.error, e:
							print ("Error closing socket: %s" % e)


					break

			continue

		elif action == "deluser":
			print ("! Work in progress...\n")
			continue

		elif action == "backup":
			print ("! Work in progress...\n")
			continue

		elif action == "restore":
			print ("! Work in progress...\n")
			continue

		elif action == "dirlist":
			print ("! Work in progress...\n")
			continue

		elif action == "delete":
			print ("! Work in progress...\n")
			continue

		elif action == "logout":
			print ("! Work in progress...\n")
			continue

		elif action == "exit":
			print ("Bye, bye\n")
			exit()

		else:
			print ("Error - Unknown action : %s\n" % action)
			continue
	try:
		fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error, e:
		print ("Error creating socket: %s" % e)
		fd = None

	server_address = (HOST, PORT)

	try:
 		fd.connect(server_address)
	except socket.error, e:
		print ("Error connecting to server address %s : %s" % (server_address, e))
		exit()

	try:
		msg = "OLA"
		fd.sendall(msg)
	except socket.error, e:
		print ("Error sending message: '%s' : %s" % (msg, e))

	try:
		data = fd.recv(BUFFER_SIZE)
		print (data)
	except socket.error, e:
		print ("Error receiving message: %s" % e)

	try:
		fd.close
	except socket.error, e:
		print ("Error closing socket: %s" % e)

if __name__ =='__main__':
	main()
