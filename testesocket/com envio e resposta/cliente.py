#!/usr/bin/python2

from threading import Thread
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 9999,))

'''
class ReplyHandler(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        while True:
            reply = sock.recv(1024)
            print('  ', reply.decode('utf-8'))

thread = ReplyHandler()
'''
def receber():
    while True:
        reply = sock.recv(1024)
        print('  ', reply.decode('utf-8'))

thread = Thread(target=receber)
thread.daemon = True
thread.start()

while True:
    message = input('')
    sock.sendall(bytes(message, 'utf-8'))
sock.close()