import threading
import socket
import time
import sys


class cliente(object):
    def __init__(self, ip='localhost', port=80):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = (ip, port)

        # mensagens: Simula uma fila que armazena as mensagens enviadas e recebidas
        self.mensagens = []
        print("Cliente pronto para se conectar")

    def consumir_mensagem(self):
        return self.mensagens.pop(0)

    def ha_mensagens(self):
        return len(self.mensagens) != 0

    def iniciar(self):
        self.conectar()
        thread = threading.Thread(target=self.receber)
        thread.daemon = True
        thread.start()

    def enviar(self):
        ''' Deve ser subscrita para a classe que estiver usando '''
        while True:
            message = input('')
            self.sock.send(bytes(message, 'utf-8'))
        self.sock.close()

    def send_message(self, message):
        time.sleep(0.01)
        self.sock.send(bytes(message, 'utf-8'))

    def conectar(self):
        try:
            self.sock.connect(self.addr)
            print("Cliente conectado")
        except:
            print("Incapaz de se conectar")
            sys.exit()

    def receber(self):
        ''' Deve ser subscrita para a classe que estiver usando '''
        while True:
            try:
                reply = self.sock.recv(1024)
                #print("Recebi:", reply.decode('utf-8'))
                self.mensagens.append(reply.decode('utf-8'))
            except:
                print("Desconectado do servidor")
                sys.exit()


'''
c = cliente()
c.iniciar()
c.enviar()
'''
