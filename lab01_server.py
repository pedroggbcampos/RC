#!/usr/bin/env python
import socket
import sys

def main():

  HOST = ''
  PORT = 58000
  BUFFER_SIZE = 80

  try:
    fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
  
  msg = 'HEY'

  connection.sendall(msg)

  connection.close
  
if __name__ =='__main__':
  main() 
  
