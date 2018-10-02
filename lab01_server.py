#!/usr/bin/env python
import socket
import sys

def msg(i):
  if i == 1 or i == 2 or i == 3:
    return "AUR OK\n"
  elif i == 4:
    return "LFD 123.456.567 50000 text.txt dd.mm.yyyy 56 text2.txt dd.mm.yyyy 49 text3.txt dd.mm.yyyy 1000\n"

def main():

  HOST = ''
  PORT = 58020
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
  
