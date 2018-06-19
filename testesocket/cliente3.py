# Cliente 
import socket
 

 
HOST='localhost' #coloca o host do servidor 
PORT=57000
 
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
 

s.connect((HOST,PORT))
 

arq=open('oi.jpg','rb')
 

for i in arq:
    #print i
    s.send(i)
 

arq.close()
s.close()