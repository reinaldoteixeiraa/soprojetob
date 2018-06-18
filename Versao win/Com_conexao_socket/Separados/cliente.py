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
            reply = self.socket.recv(1024)
            print("\n", reply.decode('utf-8'))

    def executar(self):
        try:
            while True:
                time.sleep(0.1)
                if len(self.msgs):
                    for i in self.msgs:
                        self.socket.sendall(bytes(i, 'utf-8'))
        except KeyboardInterrupt:
            print("Finalizando processo...")
            self.socket.close()

    def iniciar(self):
        try:
            self.socket.connect((self.HOST, self.PORT,))
            print("Conetado com o host remoto. Começando a enviar mensagens")
        except:
            print("Incapaz de estabelecer uma conexao")
            return False

        thread = threading.Thread(target=self.receber)
        thread.daemon = True
        thread.start()

        principal = threading.Thread(target=self.executar)
        principal.daemon = True
        principal.start()


'''
t = cliente_TCP()
t.iniciar()
'''
