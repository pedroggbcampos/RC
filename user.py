import socket
import os.path

HOST = '127.0.0.1'
PORT = 58038

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT)
tcp.connect(dest)

def avaiableTasks(ptcn):
    with open('fileprocessingtasks.txt') as f:
        for line in f:
            l = line.split()
            if l[0] == ptcn:
                return True
    return False


msg = raw_input("> ")
request = msg.split()
while msg != 'exit':
	if msg == 'list':
		tcp.send('LST\n')
		msgrecv = tcp.recv(1024)
		if msgrecv.split()[0] == 'FPT':
			tasks = msgrecv.split()[2:]
			for i in range(int(msgrecv.split()[1])):
				print str(i+1) + ' - ' + tasks[i]
				
	elif request[0] == 'request':
		ptcn = request[1]
		fname = request[2]
		name = os.path.splitext(os.path.basename(fname))[0]
		n_bytes = os.path.getsize(fname)
		data = open(fname, 'r').read()
		tcp.send('REQ ' + ptcn + ' ' + str(n_bytes) + ' ' + data +'\n')
		msgrecv = tcp.recv(1024)
		print msgrecv
			
			
		if msgrecv.split()[0] == 'REP':
			if msgrecv.split()[1] != 'EOF' and msgrecv.split()[1] != 'ERR':
				if msgrecv.split()[1] == 'R':
					#n_words = sum(len(line.split()) for line in open('fileprocessingtasks.txt'))
					print 'Number of words: ' + 'x'
				elif msgrecv.split()[1] == 'F':
					print str(n_bytes) + ' Bytes to transmit \n received file ' + name + '_' + ptcn +'.txt\n' + str(n_bytes) + ' Bytes'  
						
						
		elif request[1] == 'EOF':
			print 'The REQ request cannot be answered.'
				
		elif request[1] == 'ERR':
			print 'The REQ request is not correctly formulated.'
	
	else:
		print 'O CS nao seguiu o protocolo esperado.'
		
	
	
	msg = raw_input("> ")
    #inputready,outputready,exceptready = select.select(msg,[],[]) 
    
    
tcp.close()