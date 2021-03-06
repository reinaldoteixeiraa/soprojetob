import threading
import socket
import time
import os
import sys


class cliente(object):
    def __init__(self, ip='localhost', port=80):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = (ip, port)

    def iniciar(self):
        self.conectar()
        thread = threading.Thread(target=self.receber)
        thread.daemon = True
        thread.start()

    def enviar(self):
        while True:
            message = input('')
            self.sock.send(bytes(message, 'utf-8'))
        self.sock.close()

    def conectar(self):
        try:
            self.sock.connect(self.addr)
        except:
            print("Incapaz de se conectar")
            sys.exit()

    def receber(self):
        while True:
            try:
                reply = self.sock.recv(1024)
                print('  ', reply.decode('utf-8'))
            except:
                print("Desconectado do servidor")
                sys.exit()


c = cliente()
c.iniciar()
c.enviar()
