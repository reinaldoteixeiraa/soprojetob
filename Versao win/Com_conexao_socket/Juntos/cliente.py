import threading
import socket
import time
import os


class cliente_TCP(object):
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HOST = '127.0.0.1'
        self.PORT = 9999
        self.msgs = []

    def receber(self):
        while True:
            try:
                reply = self.socket.recv(1024)
                print("\n", reply.decode('utf-8'))
            except:
                break

    def iniciar_cliente(self):
        try:
            self.socket.connect((self.HOST, self.PORT,))
            print("Conetado com o host remoto. Começando a enviar mensagens")
        except:
            print("Incapaz de estabelecer uma conexao")
            return False

        thread = threading.Thread(target=self.receber)
        thread.daemon = True
        thread.start()
