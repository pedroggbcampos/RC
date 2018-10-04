#!/usr/bin/env python
import socket
import sys

i = 0

def msg():
  global i
  i += 1
  if i == 1 or i == 2 or i == 4:
    return "AUR OK\n"
  elif i == 3:
    return "RSR localhost 58023\n"
  elif i == 5:
    return "RBR 3 text.txt dd.mm.yyyy 6 oi\nola text2.txt dd.mm.yyyy 2 oi text3.txt dd.mm.yyyy 4 oi !\n"


def oi():

  HOST = ''
  PORT = 58023
  BUFFER_SIZE = 80

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

  message = msg()

  connection.sendall(message)

  print data

  while (True):
    try:

      data = connection.recv(BUFFER_SIZE)
      if data == "":
        break
    except socket.error as e:
      print "Error receiving message: %s" % e

    message = msg()
    connection.sendall(message)
    break
  
  print data


  connection.close

def main():
  while(True):
    oi()
  
if __name__ =='__main__':
  main() 
  
