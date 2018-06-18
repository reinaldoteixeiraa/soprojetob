import threading
import socket
import time
import os


class servidor_TCP(object):
    def __init__(self, max_conexoes=5):
        # Configurando
        self.MAX_CONEXOES = max_conexoes
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.HOST = '127.0.0.1'
        self.PORT = 9999
        self.socket.bind((self.HOST, self.PORT,))
        self.socket.listen(10)

        self.lista_de_conexao = [self.socket]
        self.msgs = []

    def iniciar_servidor(self):
        print("Servidor iniciado na porta", self.PORT, end=" ")
        print("para no maximo", self.MAX_CONEXOES-1, "clientes")

        for i in range(self.MAX_CONEXOES):
            thread = threading.Thread(target=self.conexao)
            thread.deamon = True
            thread.start()
        '''
        t = threading.Thread(target=self.enviar_mensagens)
        t.deamon = True
        t.start()
        '''

    def enviar_mensagens(self):
        try:
            while True:
                if len(self.msgs):
                    for i in self.msgs:
                        self.enviar_mensagem(i)
        except KeyboardInterrupt:
            print("Finalizando processo...")
            self.socket.close()

    def enviar_mensagem(self, msg, cliente=None):
        for c in self.lista_de_conexao:
            if c != self.socket:
                c.sendall(bytes(msg, 'utf-8'))

    def conexao(self):
        try:    # Tenta estabelecer uma conexao
            cliente, addr = self.socket.accept()
            self.lista_de_conexao.append(cliente)
            print("\nCliente (%s, %s) conectado" % addr)

            while True:
                try:    # Tenta receber uma mensagem
                    msg = cliente.recv(1024)
                    print(msg.decode('utf-8'))
                except:  # Caso contrario, remove conexao e para a thread
                    cliente.close()
                    for i in self.lista_de_conexao:
                        print(i)
                    self.lista_de_conexao.remove(cliente)
                    break

                for outros_clientes in self.lista_de_conexao:
                    if cliente not in [outros_clientes, self.socket]:
                        outros_clientes.sendall(msg)
        except:  # Caso contrario, finaliza a thread
            print("Conexao perdida.")


t = servidor_TCP()
t.iniciar_servidor()
