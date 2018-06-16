import argparse, sys, time, os, socket
from datetime import datetime
import threading # import Thread, Event
import win32file, win32event, win32con
import util # da minha pasta

def get_args():
    parser = argparse.ArgumentParser(description="diretório para ser supervisionado")
    parser.add_argument("-dp", "--dir_superv", type=str, default="C://Users//danie//Desktop//Dir",
                        help="diretório para ser supervisionado")
    return parser.parse_args()

class servico_cliente(object):
    def __init__(self, dir_superv = "", FILE_LOG = "LOG_Cliente.txt"):
        print("Iniciando...")
        self.FILE_LOG   = FILE_LOG
        self.dir_superv = dir_superv
        self.versao     = 0
        self.events     = threading.Event()
        self.data       = datetime.now()

        ''' ALTERA '''
        ''' DIRETORIO BACKUP '''
        self.dir_backup = ""    
        ''' DIRETORIO BACKUP '''

        
        ''' SOCKET - OBSERVADOR '''
        ''' ALTERA '''
        addr = ('', 7001) #(host, port)
        
        self.UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.UDP.bind(addr)
        self.msgs = []
        ''' SOCKET - OBSERVADOR '''

        if not os.path.isfile(FILE_LOG): # Primeira inicialização do serviço
            print("\nCriação de log para a primeira inicialização...")
            self.atualizar_log(str(self.data), 0)
        else:                           # Inicialização com diretório já existente
            print("\nCarregando log para inicialização em um diretório já monitorado...")
            self.ler_log() 
        print()

    def ler_log(self):
        with open(self.FILE_LOG, "r") as file:
            f1 = file.read().split("\nFiles:\n")[0]
            rd = dict([i.split(": ") for i in f1.split("\n")])
            for i,j in rd.items():
                print("%15s : %s" % (i,j) )
            self.data   = datetime.strptime(rd["data"], "%Y-%m-%d %X.%f")
            self.versao = rd["versao"]
            print("%15s : %s" % ("diff", datetime.now()-self.data))
            print()            

    def atualizar_log(self, data, versao):
        with open(self.FILE_LOG, "w") as file:
            ''' ALTERA '''
            dirpath, files = util.capturar_todos_arquivos_e_pastas(self.dir_superv)
            
            file.write("path superv: %s\n" % self.dir_superv)
            file.write("path backup: %s\n" % self.dir_backup)
            file.write("data: %s\n" % data)
            file.write("versao: %d\n" % versao)
            file.write("Files:\n")
            escrevendo = lambda i: file.write(i+"\n")
            for i in files: escrevendo(i)
            file.write("Diretorios:\n")
            for i in dirpath: escrevendo(i)

    def iniciar(self):
        self.events.set()
        t1 = threading.Thread(target=self.atualizar)
        t1.start()

        t2 = threading.Thread(target=self.receber_msg)
        t2.start()

        try:
            while 1:
                time.sleep(.1)
        except KeyboardInterrupt:
            print("Finalizando threads...")
            self.events.clear()
            self.UDP.close()
            t1.join()

    def receber_msg(self):
        while self.events.is_set():
            msg, cliente = self.UDP.recvfrom(1024)
            self.msgs.append((msg.decode('utf-8'),cliente))

    def atualizar(self):
        print("Inicio do monitoramento...")
        while self.events.is_set():
            time.sleep(60)
            if len(self.msgs) :
                for i in self.msgs:
                    print(i)
            
            self.ler_log()
            if False:
                self.atualizar_log(str(datetime.now()), 0)

# main é minha thread principal
def main():
    args = get_args()
    svc_p = servico_cliente(args.dir_superv)
    svc_p.iniciar()
    
main()

# Site base para observar o diretório
# http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html
