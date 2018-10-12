def check_protocol(msg):
	'''check_protocol : string x list -> logico
	:: recebe um argumento do tipo string que representa o tipo de mensagem recebida e uma
	lista com os restantes argumentos da mensagem, devolve True caso a mensagem esteja de
	acordo com o protocolo e False caso contrario'''
	command = msg[0]
	n_args = len(msg)
	#print "vou verificar uma mensagem com len " + str(n_args)
	if command == "ERR":
		return False
	elif command == "AUT":
		return n_args == 3
	elif command == "DLU":
		return n_args == 1
	elif command == "BCK":
		n = int(msg[2])
		return n_args == (3+n*4)
	elif command == "RST":
		return n_args == 2
	elif command == "LSD":
		return n_args == 1
	elif command == "LSF":
		return n_args == 2
	elif command == "DEL":
		return n_args == 2
	elif command == "REG":
		return n_args == 3
	elif command == "UNR":
		return n_args == 3
	elif command == "LFD":
		n = int(msg[1])
		return n_args == (2+n*4)
	elif command == "LUR":
		return n_args == 2
	elif command == "DBR":
		return n_args == 2
	return False