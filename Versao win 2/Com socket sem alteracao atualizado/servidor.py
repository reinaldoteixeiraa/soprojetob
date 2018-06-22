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
        self.lim_envio = 4096

        self.CONNECTION_LIST = []
        # mensagens: Simula uma fila que armazena as mensagens enviadas e recebidas
        self.mensagens = []
        print("Servidor iniciado na porta", port)

    def consumir_mensagem(self):
        return self.mensagens.pop(0)

    def ha_mensagens(self):
        return len(self.mensagens) != 0

    def iniciar(self, conectar=None):
        conectar = self.conectar if conectar == None else conectar
        thread = threading.Thread(target=conectar)
        thread.daemon = True
        thread.start()

    def enviar(self):
        ''' Deve ser subscrita para a classe que estiver usando '''
        try:
            while True:
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

    def conectar(self):
        ''' Deve ser subscrita para a classe que estiver usando '''
        peer, addr = self.sock.accept()
        self.CONNECTION_LIST.append(peer)

        print("Cliente (%s, %s) conectado" % addr)

        while True:
            try:
                message = peer.recv(self.lim_envio)
                #print("Recebi:", message.decode('utf-8'))
                self.mensagens.append(message.decode('utf-8'))
                for other in self.CONNECTION_LIST:
                    if peer != other:
                        other.sendall(bytes(message, "utf-8"))
            except:
                print("Cliente (%s, %s) se desconectou" % addr)
                self.CONNECTION_LIST.remove(peer)
                break

    '''def send_message(self, message):
        for socket in self.CONNECTION_LIST:
            socket.sendall(bytes(message, "utf-8"))
    '''


'''
s = servidor()
s.iniciar()
s.enviar()
'''
