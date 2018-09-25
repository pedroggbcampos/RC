import socket
import sys
import os
import select
import os.path

HOST = 'localhost'
TCP_PORT = 58038
UDP_PORT = 58038

INPUTS = []

working_server = []

if os.path.exists('fileprocessingtasks.txt'): #remover ficheiro dos WS se ja existir
    os.remove('fileprocessingtasks.txt')
    

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
orig = (HOST, TCP_PORT)
tcp.bind(orig)
tcp.listen(1)

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
udp.bind((HOST, UDP_PORT))


INPUTS.append(tcp)
INPUTS.append(udp)

def availableWS(ptcn):
    available_servers = []
    with open('fileprocessingtasks.txt') as f:
        for line in f:
            l = line.split()
            if l[0] == ptcn:
                available_servers.append((l[1], int(l[2])))
    return available_servers

def numfilesWS (n):
    return '{:03d}'.format(n)

def clientRequest():
    tcp.close()
    print 'Conectado por ', cliente
    while True:
        msg = con.recv(1024)
        if not msg: 
            break
        
        if msg == 'LST':
            if os.path.exists('fileprocessingtasks.txt'):
                tasks = []
                with open("fileprocessingtasks.txt") as f:
                    for line in f:
                        if line.split()[0] not in tasks:
                            tasks.append(line.split()[0])
                con.send('FPT ' + str(len(tasks)) + ' ' + ' '.join(tasks))
            else:
                con.send('No tasks available.')
                
        elif msg.split()[0] == 'REQ':
            count = 0
            num_file = 1
            ptcn = msg.split()[1]
            n_bytes = msg.split()[2]
            data2 = msg.split(" ", 3)
            data =  data2[3].split("\n")
            print data
            d = " ".join(data)
            pid = str(os.getpid())
            number = pid.zfill(5)
            f = open(number + '.txt', 'a')
            f.write(data2[3].rstrip())
            f.close()
            available_servers = availableWS(ptcn)
            
            
            with open(number + '.txt', 'r') as file:
                for line in file:
                    count += 1

            num_ws = len(available_servers)
            print count
            print num_ws
            j = count // num_ws
            print j
            info_ws = []
            for i in range(num_ws):
                if i == num_ws-1:
                    info_ws.append(data[i*j:])
                else:
                    info_ws.append(data[i*j:i+1*j])
                    
            for k in range(len(info_ws)):
                print info_ws
                f = open(str(number)+str(numfilesWS(num_file))+'.txt', 'w')
                f.write (str(info_ws[k]))
                f.close()
                num_file +=1
                num_file = int(num_file) + 1
                

                
            if available_servers != []:
                for ws in available_servers:
                    pid = os.fork()
                    print ws
                    if pid == 0:
                        tcp_ws = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        tcp_ws.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        tcp_ws.connect(ws)
                        tcp_ws.send('WRQ ' + ptcn + ' ' + str(number) + str(numfilesWS(num_file)) +'.txt' + ' ' + str(n_bytes) + ' ' + data2[3])
                    
                        msgrecv = tcp_ws.recv(1024)
                        print msgrecv
                        rep = msgrecv.split()
                        con.send(rep[0] + ' ' + rep[1] + ' ' + rep[2]  + ' ' + ' '.join(data))
                        tcp_ws.close()
                        sys.exit(0)
                 
            else:
                print 'Invalid PTC' #print 'WRP EOF'
                
        print cliente, msg
    
    print 'Finalizando conexao do cliente ', cliente
    con.close()
    sys.exit(0)

while True:
    inputs, outputs, in_error =  select.select(INPUTS, [], [], 0)
    for sock in inputs:
        if sock == tcp:
            con, cliente = tcp.accept()
            pid = os.fork()
            if pid == 0:
                clientRequest()
            else:
                con.close()
        elif sock == udp:
            data, addr = udp.recvfrom(1024) # buffer size is 1024 bytes
            print data
            f = open('fileprocessingtasks.txt', 'a')
            ptcs = data.split()[1:-2]
            address = " ".join(data.split()[-2:])
            working_server.append((data.split()[-2], int(data.split()[-1])))
            print working_server
            for ptc in ptcs:
                f.write(ptc + ' ' + address + '\n')
            f.close() 
            udp.sendto("RAK OK", addr)