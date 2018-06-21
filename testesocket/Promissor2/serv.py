import threading
import socket
import time
import os


class UCP(object):
    def __init__(self):
        host = ''
        port = 7000
        self.addr = (host, port)
        self.UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.UDP.bind(self.addr)

    def iniciar(self):
        self.receber()

    def receber(self):
        msg, cliente = self.UDP.recvfrom(1024)
        print("-->", cliente, " : ", msg.decode('utf-8'))
        while msg.decode('utf-8').lower() != "exit":
            msg, cliente = self.UDP.recvfrom(1024)
            print("-->", cliente, " : ", msg.decode('utf-8'))
        self.UDP.close()


s = UCP()
s.iniciar()
