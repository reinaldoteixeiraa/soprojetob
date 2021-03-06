import threading
import socket
import time
import os


class servidor(object):
    def __init__(self, ip='localhost', port=80):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # A porta (port) deve ser a mesma para a conexao funcionar
        self.addr = (ip, port)      # Endereço para ouvir
        self.sock.bind(self.addr)   # Ligando para o endereço (self.addr)
        self.sock.listen(1)         # Ouvindo: max (1) conexao
        self.CONNECTION_LIST = []
        print("Chat server iniciado na porta", port)

    def iniciar(self, conectar=None):
        conectar = self.conectar if conectar == None else conectar
        thread = threading.Thread(target=conectar)
        thread.daemon = True
        thread.start()

    def enviar(self):
        ''' Deve ser subscrita para a classe que estiver usando '''
        try:
            while 1:
                message = input('')
                self.send_message(message)
        except KeyboardInterrupt:
            for peer in self.CONNECTION_LIST:
                peer.close()
            self.sock.close()

    def send_message(self, message):
        # def broadcast_data copy
        for socket in self.CONNECTION_LIST:
            try:
                socket.send(bytes(message, "utf-8"))
            except:
                socket.close()
                self.CONNECTION_LIST.remove(socket)

    '''def send_message(self, message):
        for socket in self.CONNECTION_LIST:
            socket.sendall(bytes(message, "utf-8"))
    '''

    def conectar(self):
        ''' Deve ser subscrita para a classe que estiver usando '''
        peer, addr = self.sock.accept()
        self.CONNECTION_LIST.append(peer)

        print("Cliente (%s, %s) conectado" % addr)

        while True:
            try:
                message = peer.recv(1024)
                print('  ', message.decode('utf-8'))
                for other in self.CONNECTION_LIST:
                    if peer != other:
                        other.sendall(bytes(message, "utf-8"))
            except:
                print("Cliente (%s, %s) se desconectou" % addr)
                self.CONNECTION_LIST.remove(peer)
                break


s = servidor()
s.iniciar()
s.enviar()
