#!/usr/bin/env python
import socket
import sys

def msg(i):
  if i == 1 or i == 2:
    return "AUR OK"
  elif i == 3:
    return "BKR 1060 50000 1"

def main():

  HOST = ''
  PORT = 58023
  BUFFER_SIZE = 80
  i = 0
  while(True):
    i += 1
    try:
      fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error as e:
      print "Error creating socket: %s" % e
  
    server_address = (HOST, PORT)
    
    fd.bind(server_address)

  
    fd.listen(1)
  
  
    connection, client_address = fd.accept()
  
    try:
      data = connection.recv(BUFFER_SIZE)
    except socket.error as e:
      print "Error receiving message: %s" % e
  
    print data
  
    message = msg(i)

    connection.sendall(message)

    connection.close
  
if __name__ =='__main__':
  main() 
  
