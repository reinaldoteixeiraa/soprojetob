############## client_tuto.py################# 
 #!/usr/bin/python #Coded by: Alisson Menezes [kernelcrash] # 
# -*- coding: utf-8 -*-
import socket
ip = '127.0.0.1' # LOCAL HOST - PROPRIO DA MAQUINA
#ip = raw_input('digite o ip de conexao: ') 
port = 7000 
addr = ((ip,port)) 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
client_socket.connect(addr) 
mensagem = raw_input("digite uma mensagem para enviar ao servidor: ") 
client_socket.send(mensagem) 
print 'mensagem enviada' 
client_socket.close() 

############=----EOF----###########

#https://www.vivaolinux.com.br/artigo/Sockets-em-Python