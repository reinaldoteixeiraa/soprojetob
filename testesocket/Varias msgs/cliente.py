############## client_tuto.py#################
#!/usr/bin/python #Coded by: Alisson Menezes [kernelcrash] #
# -*- coding: utf-8 -*-
import socket
ip = '127.0.0.1'  # LOCAL HOST - PROPRIO DA MAQUINA
#ip = raw_input('digite o ip de conexao: ')
port = 7000
dest = (ip, port)
UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

msg = bytes(input("--> "), 'utf-8')
UDP.sendto(msg, dest)
while msg.decode('utf-8').lower() != "exit":
    msg = bytes(input("--> "), 'utf-8')
    UDP.sendto(msg, dest)
UDP.close()
############=----EOF----###########

# https://www.vivaolinux.com.br/artigo/Sockets-em-Python
