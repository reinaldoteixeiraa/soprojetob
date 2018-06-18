import threading
import socket
import time
import os


class cliente_TCP(object):
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HOST = '127.0.0.1'
        self.PORT = 9999
        self.execute = False
        self.msgs = []

        try:
            self.socket.connect((self.HOST, self.PORT,))
            self.execute = True
            print("Conetado com o host remoto. Começando a enviar mensagens")
        except:
            print("Incapaz de estabelecer uma conexao")

    def receber(self):
        while self.execute:
            reply = self.socket.recv(1024)
            print("\n", reply.decode('utf-8'))

    def iniciar(self):
        if self.execute:
            return False
        thread = threading.Thread(target=self.receber)
        thread.daemon = True
        thread.start()

        try:
            while True:
                if len(self.msgs):
                    for i in self.msgs:
                        self.socket.sendall(bytes(i, 'utf-8'))
        except KeyboardInterrupt:
            print("Finalizando processo...")
            self.socket.close()
        return True


t = cliente_TCP()
t.iniciar()

'''
    def enviar_mensagem(self, sock, msg):
        for socket in self.lista_de_conexao:
            if socket != self.socket and socket != sock:
                try:
                    socket.send(message)
                except:
                    socket.close()
                    self.lista_de_conexao.remove(socket)
'''
