#!/usr/bin/env python
import socket
import sys
import os
import datetime

HOST = 'localhost'
PORT = 58023
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

server_address = (HOST, PORT)


def tcp_client(server_address, msg):
	try:
		fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error, e:
		print ("Error creating socket: %s" % e)
		fd = None

	try:
		fd.connect(server_address)
	except socket.error, e:
		print ("Error connecting to server address %s : %s" % (server_address, e))
		exit()

	try:
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

	return data


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

					msg = "AUT" + " " + user + " " + password 

					data = tcp_client(server_address, msg)

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
				

					break

			continue

		elif action == "deluser":
			if len(command) != 1:
				print ("Invalid number of arguments - Correct format is : deluser\n")
				break
			elif len(command) == 1:
				msg = "DLU"
				data = tcp_client(server_address, msg)
				status = data.split(" ")
				if status[0] != "DLR":
					print ("Error authenticating")
					break
				if status[1] == "OK":
					print("User successfully deleted.")
				elif status[1] == "NOK":
					print("Could not delete user. User still has information stored")
			continue

		elif action == "backup":
			if len(command) != 2:
				print ("Invalid number of arguments - Correct format is : backup [dir]\n")
				break
			elif len(command) == 2:
				curr_path = os.path.dirname(os.path.abspath(__file__))
				bck_dir = command[1]
				dir_path = curr_path + "/" + bck_dir
				if not os.path.exists(dir_path):
					print ("Backup Error - Directory provided does not exist")
					break
				else:
					files = os.listdir(dir_path)
					if not files:
						print ("Backup Error - There are no files in the directory provided")
						break
					else:
						msg = "BCK " + bck_dir + " " + str(len(files)) + " "
						for file in files:
							mtime = os.path.getmtime(dir_path + "/" + file)
							last_modified_date = datetime.datetime.fromtimestamp(mtime)
							file_size = os.path.getsize(dir_path + "/" + file)
							last_modified_date = str(last_modified_date)
							last_modified_date = last_modified_date.split(".")
							last_modified_date = last_modified_date[0].decode('utf-8').replace("-".decode('utf-8'), ".").encode('utf-8')
							msg = msg + file + " " + last_modified_date + " " + str(file_size) + " "
						data = tcp_client(server_address, msg)
						status = data.split(" ")
						if status[0] != "BKR":
							print ("Error in the response for backup request")
							break
						if len(status) < 3:
							print ("Error in the response for backup request")
							break
						Bs_ip = status[1]
						Bs_port = status[2]
						nr_files = status[3]
						if nr_files == 0:
							print ("Files already in backup")
							break
						else:
							tcp_client((Bs_ip, Bs_port), msg)

				break

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

if __name__ =='__main__':
	main()