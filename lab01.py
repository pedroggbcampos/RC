import socket
import sys

HOST = 'localhost'
PORT = 58000
BUFFER_SIZE = 80

def main():
  try:
    fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  except socket.error, e:
    print "Error creating socket: %s" % e
  
  server_address = (HOST, PORT)
  
  fd.connect(server_address)
  
  try:
    msg = "OLA"
    fd.sendall(msg)
  except socket.error, e:
    print "Error sending message: %s :%s" % (msg, e) 
  
  data = fd.recv(BUFFER_SIZE)
  
  print data
  
  fd.close

if __name__ =='__main__':
  main()

