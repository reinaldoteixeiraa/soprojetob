import threading
import socket
import time
import os


class UCP(object):
    def __init__(self):
        ip = '127.0.0.1'  # LOCAL HOST - PROPRIO DA MAQUINA
        #ip = raw_input('digite o ip de conexao: ')
        port = 7000
        self.dest = (ip, port)
        self.UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def iniciar(self):
        self.enviar()

    def enviar(self):
        msg = bytes("", 'utf-8')
        self.UDP.sendto(bytes("Conectado!", 'utf-8'), self.dest)
        while msg.decode('utf-8').lower() != "exit":
            msg = bytes(input("--> "), 'utf-8')
            self.UDP.sendto(msg, self.dest)
        self.UDP.close()


c = UCP()
c.iniciar()
