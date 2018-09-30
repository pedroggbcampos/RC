#!/usr/bin/env python
import socket
import sys
import os
import datetime

HOST = 'localhost'
PORT = 58023
BUFFER_SIZE = 80

USER = None
PASS = None

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


def tcp_client(server_address, msg, authentication):
	if authentication == True:
		(validation, fd) = authenticate_user_bool()
		if not validation:
			if fd != None:
				close_socket(fd)
			data = "NOK"
			return data

	elif authentication == False:
		try:
			fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error, e:
			print ("Error creating socket: %s" % e)
			fd = None

	fd.settimeout(4)

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
	except socket.timeout, i:
		data = "TMO"
	except socket.error, e:
		print ("Error receiving message: %s" % e)

	close_socket(fd)

	return data

def tcp_client_aut(server_address, msg):
	try:
		fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error, e:
		print ("Error creating socket: %s" % e)
		fd = None

	fd.settimeout(4)

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
	except socket.timeout, i:
		data = "TMO"
	except socket.error, e:
		print ("Error receiving message: %s" % e)

	return (data, fd)

def authenticate_user_bool():
	validation = False
	if not logged_in_bool():
		print ("To execute any command you must login first: login [user] [password]")
		fd = None
		return (validation, fd)
	msg = "AUT" + " " + USER + " " + PASS
	(data, fd)= tcp_client_aut(server_address, msg)
	if socket_timeout(data):
		print ("Error authenticating. Connection timeout. Operation cancelled")
		return (validation, fd)

	status = data.split(" ")
	if status[0] != "AUR":
		print ("Error authenticating. Operation cancelled")
		return (validation, fd)
	if status[1] == "OK":
		validation = True
		return (validation, fd)
	elif status[1] == "NOK":
		print("Authentication failed. Operation cancelled")
		return (validation, fd)
	else:
		print ("Error authenticating. Operation cancelled")
		return (validation, fd)

def close_socket(fd):
	try:
		fd.close
	except socket.error, e:
		print ("Error closing socket: %s" % e)
	return

def socket_timeout(data):
	if data == "TMO":
		return True
	else:
		return False

def aut_failed(data):
	if data == "NOK":
		return True
	else:
		return False

def logged_in_bool():
	if USER == None or PASS == None:
		return False
	else:
		return True





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

					msg = "AUT" + " " + user + " " + password

					data = tcp_client(server_address, msg, False)

					if socket_timeout(data):
						print ("Error connecting to CS for authentication. Connection timeout")

					status = data.split(" ")
					if status[0] != "AUR":
						print ("Error authenticating")
						break
					if status[1] == "OK":
						print("Logged in. Successful authentication")
						global USER
						global PASS
						USER = user
						PASS = password
						break
					elif status[1] == "NOK":
						print("Authentication failed. Incorrect password")
						break
					elif status[1] == "NEW":
						print("Logged in. New user created")
						USER = user
						PASS = password
						break
					else:
						print ("Error authenticating")
						break
					break
				break
			continue

		elif action == "deluser":
			while(True):
				if len(command) != 1:
					print ("Invalid number of arguments - Correct format is : deluser\n")
					break
				elif len(command) == 1:
					msg = "DLU"
					data = tcp_client(server_address, msg, True)
					if aut_failed(data):
						break
					if socket_timeout(data):
						print ("Error connecting to CS for user deletion. Connection timeout")
						break
					status = data.split(" ")
					if status[0] != "DLR":
						print ("Error in message received by user deletion request")
						break
					if status[1] == "OK":
						print("User successfully deleted.")
					elif status[1] == "NOK":
						print("Could not delete user. User still has information stored")
				break
			continue

		elif action == "backup":
			while(True):
				if len(command) != 2:
					print ("Invalid number of arguments - Correct format is : backup [dir]\n")
					break
				elif len(command) == 2:
					if not logged_in_bool():
						print ("To execute any command you must login first: login [user] [password]")
						break

					curr_path = os.path.dirname(os.path.abspath(__file__))
					bck_dir = command[1]
					dir_path = curr_path + "/" + bck_dir
					if not os.path.exists(dir_path):
						print ("Backup Error - Directory provided does not exist")
						break
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
						data = tcp_client(server_address, msg, True)
						if aut_failed(data):
							break
						if socket_timeout(data):
							print ("Error connecting to CS for backup request. Connection timeout")
							break
						status = data.split(" ")
						print (data)
						if status[0] != "BKR":
							print ("Error in the response for backup request")
							break
						if len(status) < 4:
							print ("Error in the response for backup request")
							break
						Bs_ip = status[1]
						Bs_port = status[2]
						nr_files = status[3]
						if nr_files == 0:
							print ("Files already backed up")
							break
						else:

							data = tcp_client((Bs_ip, Bs_port), msg)
							if aut_failed(data):
								break
							if socket_timeout(data):
								print ("Error connecting to BS to send backup files. Connection timeout")
								break
							status = data.split(" ")

							
								#
								#
								#
								#
								#
								#
								#
				break

			continue

		elif action == "restore":
			while(True):
				if len(command) != 2:
					print ("Invalid number of arguments - Correct format is : restore [dir]\n")
					break
				elif len(command) == 2:
					directory = command[1]
					msg = "RST" + " " + directory
					data = tcp_client(server_address, msg, True)
					if aut_failed(data):
						break
					if socket_timeout(data):
						print ("Error connecting to CS for restore request. Connection timeout")
						break
					status = data.split(" ")
					if status[0] != "RSR":
						print ("Error in the response for restore request")
						break
					if len(status) < 3:
						print ("Error in the response for restore request")
						break
					Bs_ip = status[1]
					Bs_port = status[2]
					msg = "RSB" + " " + directory
					data = tcp_client((Bs_ip, Bs_port), msg, True)
					if aut_failed(data):
						break
					if socket_timeout(data):
						print ("Error connecting to BS for restore request. Connection timeout")
						break
					status = data.split(" ")
						#
						#
						#
						#
						#	
						#
						#
				break
			continue

		elif action == "dirlist":
			while(True):
				if len(command) != 1:
					print ("Invalid number of arguments - Correct command is : dirlist\n")
					break
				elif len(command) == 1:
					msg = "LSD"
					data = tcp_client(server_address, msg, True)
					if aut_failed(data):
						break
					if socket_timeout(data):
						print ("Error connecting to CS for listing backed up directories. Connection timeout")
						break
					status = data.split(" ")
					if status[0] != "LDR":
						print ("Error listing directories")
						break
					if status[1] == "0":
						print ("No directories backed up")
						break
					else:
						print("List of backed up directories:\n")
						for i in range(2, len(status)):
							print (status[i])
				break
			continue

		elif action == "delete":
			while(True):
				if len(command) != 2:
					print ("Invalid number of arguments - Correct format is : delete [dir]\n")
					break
				elif len(command) == 2:
					msg = "DEL" + " " + command[1]
					data = tcp_client(server_address, msg)
					if aut_failed(data):
						break
					if socket_timeout(data):
						print ("Error connecting to CS for directory deletion. Connection timeout")
						break
					status = data.split(" ")
					if status[0] != "DDR":
						print ("Error receiving response to delete directory")
						break
					if status[1] == "OK":
						print ("Directory deleted successfully")
						break
					elif status[1] == "NOK":
						print ("Directory not found in backup server")
						break
					else:
						print("Error deleting user\n")
						for i in range(2, len(status)):
							print (status[i])
				break
			continue

		elif action == "logout":
			while(True):
				if logged_in_bool():
					USER = None
					PASS = None
					print ("Logged out\n")
				elif not logged_in_bool():
					print ("Error - No user logged in\n")
				break
			continue

		elif action == "exit":
			exit()

		else:
			if logged_in_bool():
				print ("Error - Unknown action : %s\n" % action)
			else:
				print ("To execute any command you must login first: login [user] [password]")
			continue

if __name__ =='__main__':
	main()