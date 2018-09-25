import socket
import sys
import os
import argparse

HOST = '127.0.0.1'
UDP_PORT = 58038

parser = argparse.ArgumentParser(description='')
parser.add_argument('-e','--CSname', help='CSname',required=False, default='127.0.0.1')
parser.add_argument('-n','--CSport',help='CSport', required=False, default=58038)
parser.add_argument('-p','--WSport',help='WSport', required=False, default=59000)
parser.add_argument('ptc', nargs='*')
args = parser.parse_args()  
    
tcp_ws = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_ws.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
dest = (HOST, int(args.WSport))
tcp_ws.bind(dest)
tcp_ws.listen(1)



udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.connect((HOST, UDP_PORT))
udp.sendto('REG ' + ' '.join(args.ptc) + ' ' + args.CSname + ' ' + str(args.WSport), (HOST, UDP_PORT))
data, addr = udp.recvfrom(1024)
print data
m_cs = data.split()
    
    
if m_cs[0] == 'RAK':
    if m_cs[1] == 'NOK' or m_cs[1] == 'ERR':
        print 'Registo negado.'
    #else:
        #print 'RAK ERR'

        sys.exit()

while True:
    con, cliente = tcp_ws.accept()
    
    msg = con.recv(1024)
    if not msg: 
        break
    print msg
    wrq = msg.split()
    
    if wrq[0] == 'WRQ':
        if wrq[1] =='WCT' or wrq[1] == 'FLW':
            rt = 'R'
            con.send('REP ' + rt + 'ola' + ' hdb css jhscbhs')

        elif wrq[1] == 'UPP' or wrq[1] == 'LOW':
            rt = 'F'
            size = wrq[3]
            data = msg.split(" ", 4)
            
            con.send('REP ' + rt + ' ' + size + ' ' + data[4])
            
    
    con.close()
    #if msg.split()[0] == 'REQ':
    
    continue


#try:
	# WS-CS (UDP)
'''	
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.connect((HOST, UDP_PORT))
udp.sendto('REG ' + ' '.join(args.ptc) + ' ' + args.CSname + ' ' + str(args.WSport), (HOST, UDP_PORT))
data, addr = udp.recvfrom(1024)
print data
m_cs = data.split()
    
    
if m_cs[0] == 'RAK':
    if m_cs[1] == 'NOK' or m_cs[1] == 'ERR':
        print 'Registo negado.'
        sys.exit()
  '''  
'''
except KeyboardInterrupt: # Deals with Ctrl+c
    udp.sendto('UNR ' + args.CSname + ' ' + str(args.WSport), (HOST, UDP_PORT))
    data, addr = udp.recvfrom(1024)
    m_cs = data.split()
    if m_cs[0] == 'UAK':
		if m_cs[1] == 'NOK' or m_cs[1] == 'ERR':
			print 'CS nao deixa acabar'
		if m_cs[1] == 'OK':
			tcp_ws.close()
			udp.close()
			print '\nexit'
			sys.exit(0)
   
'''