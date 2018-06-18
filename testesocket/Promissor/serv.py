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
        self.clientes = []
        self.msgs = []

    def iniciar(self):
        print("Servidor iniciado na porta", self.PORT,
              "para no maximo", self.MAX_CONEXOES-1, "clientes")
        for i in range(self.MAX_CONEXOES):
            thread = threading.Thread(target=self.conexao)
            thread.deamon = True
            thread.start()

        try:
            while True:
                msg = input('')
                self.enviar_mensagem(msg)
                '''
                time.sleep(5)
                if len(self.msgs):
                    for i in self.msgs:
                        self.enviar_mensagem(i)
                '''
        except KeyboardInterrupt:
            print("Finalizando processo...")
            self.socket.close()

            # os.popen("taskkill /PID " + str(os.getpid()) +
            #         " /F")  # ''' MATA O PROCESSO '''

    def enviar_mensagem(self, msg, cliente=None):
        for c in self.clientes:
            if cliente == None:
                c.sendall(bytes(msg, 'utf-8'))
            elif cliente not in [self.clientes, c]:
                try:
                    c.send(msg)
                except:
                    c.close()
                    self.lista_de_conexao.remove(c)

    def conexao(self):
        try:    # Tenta estabelecer uma conexao
            cliente, addr = self.socket.accept()
            self.clientes.append(cliente)
            print("Cliente (%s, %s) conectado" % addr)

            while True:
                try:    # Tenta receber uma mensagem
                    msg = cliente.recv(1024)
                    print(msg.decode('utf-8'))
                except:  # Caso contrario, remove conexao e para a thread
                    cliente.close()
                    for i in self.clientes:
                        print(i)
                    self.clientes.remove(cliente)
                    break

                for outros_clientes in self.clientes:
                    if cliente != outros_clientes:
                        outros_clientes.sendall(msg)

        except:  # Caso contrario, finaliza a thread
            print("Conexao perdida.")


t = servidor_TCP()
t.iniciar()
