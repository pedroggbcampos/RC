#!/usr/bin/env python
import socket
import sys

HOST = 'localhost'
PORT = 58000
BUFFER_SIZE = 80



def main():

    command = raw_input()
    command = command.split(" ")

    action = command[0]

    if action == "login":
    	print ("! Work in progress...\n")

    elif action == "deluser":
    	print ("! Work in progress...\n")

    elif action == "backup":
    	print ("! Work in progress...\n")

    elif action == "restore":
    	print ("! Work in progress...\n")

    elif action == "dirlist":
    	print ("! Work in progress...\n")

    elif action == "delete":
    	print ("! Work in progress...\n")

    elif action == "logout":
    	print ("! Work in progress...\n")

    elif action == "exit":
    	print ("Bye, bye\n")
    	exit()

    else:
    	print ("Error - Invalid action : %s\n" % action)

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

