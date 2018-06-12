#########=====serv_tuto.py=====########## #!/user/bin/python #
# -*- coding: utf-8 -*-
#  # servidor que recebe mensagens de aplicação client parecido com o netsend # #
import socket

host = ''
port = 7000
addr = (host, port)
UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#UDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
UDP.bind(addr)
msg, cliente = UDP.recvfrom(1024)
print("-->", msg.decode('utf-8'))
while msg.decode('utf-8').lower() != "exit":
    msg, cliente = UDP.recvfrom(1024)
    print("-->", msg.decode('utf-8'))
UDP.close()
#############=====EOF======###################

