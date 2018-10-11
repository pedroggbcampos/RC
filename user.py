#!/usr/bin/env python
import socket
import sys
import os
import datetime

HOST = ''
PORT = 58023
BUFFER_SIZE = 500

USER = None
PASS = None

if len(sys.argv) == 2:
	print ("Could not run - Correct format is : ./user [-n CSname] [-p CSport]")
	exit()
elif len(sys.argv) == 3:
	if sys.argv[1] == "-n":
		HOST = sys.argv[2]
	elif sys.argv[1] == "-p":
		PORT = sys.argv[2]
	else:
		print ("Could not run - Correct format is : ./user.py [-n CSname] [-p CSport]")
		exit()
elif len(sys.argv) == 5:
	if sys.argv[1] == "-n":
		HOST = sys.argv[2]
	else:
		print ("Could not run - Correct format is : ./user [-n CSname] [-p CSport]")
		exit()
	if sys.argv[3] == "-p":
		PORT = sys.argv[4]
	else:
		print ("Could not run - Correct format is : ./user [-n CSname] [-p CSport]")
                exit()
elif len(sys.argv) != 1:
	print ("Could not run - Correct format is : ./user [-n CSname] [-p CSport]")
	exit()

HOST = socket.gethostbyname(HOST)
server_address = (HOST, int(PORT))
print(socket.gethostname())
print(socket.gethostbyname(socket.gethostname()))
def tcp_client(server_address, msg, authentication):
	data = ""
        if authentication == True:
                validation = False
                if not logged_in_bool():
		    print ("To execute any command you must login first: login [user] [password]")
		    return "NOK\n"

                message = "AUT" + " " + USER + " " + PASS + "\n" 

                try:
			fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		except socket.error, e:
			print ("Error creating socket: %s" % e)
			fd = None
	        try:
	                fd.connect(server_address)
	        except socket.error, e:
		        print ("Error connecting to server address %s : %s" % (server_address, e))
	        	exit()
                
                fd.settimeout(4)

                try:
		    fd.sendall(message)
	        except socket.error, e:
		    print ("Error sending message: '%s' : %s" % (message, e))

            	try:
		    data = fd.recv(BUFFER_SIZE)
	            print (data)
	        except socket.timeout, i:
		        data = "TMO\n"
	        except socket.error, e:
		        print ("Error receiving message: %s" % e)

	        status = data.split(" ")   

                if status[0] != "AUR":
		    print ("Error authenticating. Operation cancelled")
                    if fd != None:
		        close_socket(fd)
		    return "NOK\n"
	        if status[1] == "OK\n":
		    validation = True
	        elif status[1] == "NOK\n":
		    print("Authentication failed. Operation cancelled")
                    if fd != None:
		        close_socket(fd)
		    return "NOK\n"
	        else:
		    print ("Error authenticating. Operation cancelled")
                    if fd != None:
		        close_socket(fd)
		    return "NOK\n"
	

	elif authentication == False:
		try:
			fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		except socket.error, e:
			print ("Error creating socket: %s" % e)
			fd = None
	        try:
	                fd.connect(server_address)
	        except socket.error, e:
		        print ("Error connecting to server address %s : %s" % (server_address, e))
	        	exit()

	        fd.settimeout(4)

        
	try:
		fd.sendall(msg)
	except socket.error, e:
		print ("Error sending message: '%s' : %s" % (msg, e))
		print("sent %s" % msg)
	try:
		data = fd.recv(BUFFER_SIZE)
		while(data[-1:] != "\n"):
			data += fd.recv(BUFFER_SIZE)
		print (data)
	except socket.timeout, i:
		data = "TMO\n"
	except socket.error, e:
		print ("Error receiving message: %s" % e)

	close_socket(fd)

	return data


def close_socket(fd):
	try:
		fd.close()
	except socket.error, e:
		print ("Error closing socket: %s" % e)
	return

def socket_timeout(data):
	if data == "TMO\n":
		return True
	else:
		return False

def aut_failed(data):
	if data == "NOK\n":
		return True
	else:
		return False

def logged_in_bool():
	if USER == None or PASS == None:
		return False
	else:
		return True

def read_file(file_path):
	file = open(file_path, mode="r")
	content = file.read()
	file.close()
	return content

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

					msg = "AUT" + " " + user + " " + password + "\n"

					data = tcp_client(server_address, msg, False)

					if socket_timeout(data):
						print ("Error connecting to CS for authentication. Connection timeout")

					status = data.split(" ")
					if status[0] != "AUR":
						print ("Error authenticating")
						break
					if status[1] == "OK\n":
						print("Logged in. Successful authentication")
						global USER
						global PASS
						USER = user
						PASS = password
						break
					elif status[1] == "NOK\n":
						print("Authentication failed. Incorrect password")
						break
					elif status[1] == "NEW\n":
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
					print ("Invalid number of arguments - Correct format is : deluser")
					break
				elif len(command) == 1:
					msg = "DLU\n"
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
					if status[1] == "OK\n":
						print("User successfully deleted.")
					elif status[1] == "NOK\n":
						print("Could not delete user. User still has information stored")
				break
			continue

		elif action == "backup":
			while(True):
				if len(command) != 2:
					print ("Invalid number of arguments - Correct format is : backup [dir]")
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
						msg = "BCK " + bck_dir + " " + str(len(files))
						for file in files:
                                                        msg += " "
							mtime = os.path.getmtime(dir_path + "/" + file)
							last_modified_date = datetime.datetime.fromtimestamp(mtime)
							file_size = os.path.getsize(dir_path + "/" + file)
							last_modified_date = str(last_modified_date)
							last_modified_date = last_modified_date.split(".")
							last_modified_date = last_modified_date[0].decode('utf-8').replace("-".decode('utf-8'), ".").encode('utf-8')
							msg = msg + file + " " + last_modified_date + " " + str(file_size)
						msg += "\n"
						print("Going to connect to CS")
						print (msg)
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
						if status[1] == "EOF\n":
							print ("Could not complete restore request. No backup servers available")
							break
                                                elif status[1] == "ERR\n":
							print ("Request was not well formulated")
							break
						Bs_ip = status[1]
						Bs_port = status[2]
						nr_files = status[3]
						if int(nr_files) == 0:
							print ("Files already backed up")
							break
						else:
							msg = "UPL " + bck_dir + " " + nr_files
							file_names = ""
							for i in range(4, len(status)-3, 4):
								msg += " " + status[i] + " " + status[i+1] + " " + status[i+2]
								file_names += status[i] + "\n"
								file_path = dir_path + "/" + status[i]
								file = open(file_path, mode="r")
								content = read_file(file_path)
								msg += " " + content
							msg += "\n"
							print(msg)
                                                        data = tcp_client((Bs_ip, int(Bs_port)), msg, True)  ################ mudar server address para o do backup	--> data = tcp_client((Bs_ip, Bs_port), msg, True)
							if aut_failed(data):
								break
							if socket_timeout(data):
								print ("Error connecting to BS to send backup files. Connection timeout")
								break
							status = data.split(" ")

							if status[0] != "UPR":
								print ("Error in the response for backup request")
								break
							if status[1] == "OK\n" :
								print ("Backup completed")
								print ("Directory : %s" % bck_dir)
								print (file_names)
								break
							elif status[1] == "NOK\n" :
								print ("Error backing up directory")
								break
				break

			continue

		elif action == "restore":
			while(True):
				if len(command) != 2:
					print ("Invalid number of arguments - Correct format is : restore [dir]")
					break
				elif len(command) == 2:
					directory = command[1]
					msg = "RST" + " " + directory + "\n"
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
					if status[1] == "EOF\n":
						print ("Could not complete restore request. No backed up directorires or no backup servers available")
						break
					elif status[1] == "ERR\n":
						print ("Request was not well formulated")
						break
					if len(status) != 3:
						print ("Error in the response for restore request")
						break
					Bs_ip = status[1]
					Bs_port = status[2]
					msg = "RSB" + " " + directory + "\n"
					data = tcp_client((Bs_ip, int(Bs_port)), msg, True) 
					if aut_failed(data):
						break
					if socket_timeout(data):
						print ("Error connecting to BS for restore request. Connection timeout")
						break
					status = data.split(" ")
					if status[0] != "RBR":
						print ("Error in the response for restore request")
						break
					if status[1] == "EOF\n":
						print ("Could not complete restore request.")
						break
					elif status[1] == "ERR\n":
						print ("Request was not well formulated")
						break
					if len(status) < 2:
						print ("Error in the response for restore request")
						break
					nr_files = status[1]
					bite = len(status[0]) + len(nr_files) + 2
					if int(nr_files) == 0:
						print ("No files to restore")
						break
					else:
						data = data[bite:]
						file_names = ""
						for f in range(0, int(nr_files)):
							file_info = data.split(" ")
							bite = len(file_info[0]) + len(file_info[1]) + len(file_info[2]) + 3
							data = data[bite:]
							print file_info

							file = open(directory + "/" + file_info[0] , "w")
							for c in range (0, int(file_info[2])):
								file.write(data[c])
							file.close()
							file_names += file_info[0] + "\n"
							bite = int(file_info[2]) + 1
							data = data[bite:]
						print("Successful restore")
						print("Directory: %s" % directory)
						print(file_names)
						break

				break
			continue

		elif action == "dirlist":
			while(True):
				if len(command) != 1:
					print ("Invalid number of arguments - Correct command is : dirlist")
					break
				elif len(command) == 1:
					msg = "LSD\n"
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
                                        if status[1] == "0\n":
						print ("No directories backed up")
						break
					else:
						print("List of backed up directories:")
						for i in range(2, len(status)):
							print (status[i])
				break
			continue

		elif action == "filelist":
			while(True):
				if len(command) != 2:
					print ("Invalid number of arguments - Correct command is : filelist [dir]")
					break
				elif len(command) == 2:
					directory = command[1]
					msg = "LSF" + " " + directory + "\n"
					data = tcp_client(server_address, msg, True)
					if aut_failed(data):
						break
					if socket_timeout(data):
						print ("Error connecting to CS for listing files in the previously backed up directory. Connection timeout")
						break
					status = data.split(" ")

					if status[0] != "LFD":
						print ("Error listing files")
						break

					if status[1] == "NOK\n":
						print ("Could not complete the file listing request.")
						break

					if len(status) < 4:
						print("Error in the response for the file listing request")
						break

					elif len(status) >= 4:
						if status[3] == "0":
							print ("No files to list in directory " + directory )
							break
						else:
							print("Server Backup info where directory %s is located at: " %directory)
							print("  Server IP: " + status[1])
							print("  Server PORT: " + status[2])
							print("  Number of files in directory : " + status[3])
							print(" Files:")
							for i in range(4, len(status), 3):
								print("  " + status[i] + " " + status[i+1] + " " + status[i+2])
						break
					break
			continue


		elif action == "delete":
			while(True):
				if len(command) != 2:
					print ("Invalid number of arguments - Correct format is : delete [dir]")
					break
				elif len(command) == 2:
					msg = "DEL" + " " + command[1] + "\n"
					data = tcp_client(server_address, msg, True)
					if aut_failed(data):
						break
					if socket_timeout(data):
						print ("Error connecting to CS for directory deletion. Connection timeout")
						break
					status = data.split(" ")
					if status[0] != "DDR":
						print ("Error receiving response to delete directory")
						break
					if status[1] == "OK\n":
						print ("Directory deleted successfully")
						break
					elif status[1] == "NOK\n":
						print ("Directory not found in backup server")
						break
					else:
						print("Error deleting user")
						for i in range(2, len(status)):
							print (status[i])
				break
			continue

		elif action == "logout":
			while(True):
				if logged_in_bool():
					USER = None
					PASS = None
					print ("Logged out")
				elif not logged_in_bool():
					print ("Error - No user logged in")
				break
			continue

		elif action == "exit":
			exit()

		else:
			if logged_in_bool():
				print ("Error - Unknown action : %s" % action)
			else:
				print ("To execute any command you must login first: login [user] [password]")
			continue

if __name__ =='__main__':
	main()
