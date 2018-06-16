import argparse, sys, time, os, socket
from datetime import datetime
import threading # import Thread, Event
import util # da minha pasta
from log_class import log_file


# TEM QUE ALTERAR OS ARGS TAMBEM...
def get_args():
    parser = argparse.ArgumentParser(description="diretório para ser supervisionado")
    parser.add_argument("-ds", "--dir_superv", type=str, default="C://Users//danie//Desktop//Dir",
                        help="diretório para ser supervisionado")
    parser.add_argument("-dp", "--dir_backup", type=str, default="C://Users//danie//Documents//GitHub//soprojetob//Versao win//Backup",
                        help="diretório backup para ser supervisionado")
    parser.add_argument("-ip", "--ip", type=str, default="127.0.0.1",
                        help="ip da máquina que esta o servidor\npor padrao é o próprio computador")
    parser.add_argument("-t", "--tipo", type=str, default="servidor",
                        help="define o tipo do observador")                      
    return parser.parse_args()

class servico_principal(object):
    def __init__(self, dir_superv, dir_backup, servidor=True):
        print("Iniciando %s..." % ("servidor" if servidor else "cliente"))
        self.logf       = log_file("LOG_Principal.txt" if servidor else "LOG_Cliente.txt")
        self.servidor   = servidor
        self.dir_superv = dir_superv
        self.dir_backup = dir_backup
        self.versao     = 0
        self.events     = threading.Event()
        self.data       = datetime.now()
        self.alteracoes = []

        if not os.path.isfile(self.logf.name_file): # Primeira inicialização do serviço
            print("\nCriação de log para a primeira inicialização...")
            keys = ["path supervisionado", "path backup", "data", "versao", "Files", "Diretorios"]
            values = [self.dir_superv, self.dir_backup, str(self.data), 0, [], []]
            self.logf.add_arg(keys, values)
        else:                           # Inicialização com diretório já existente
            print("\nCarregando log para inicialização em um diretório já monitorado...")
            self.logf.carregar()
            self.versao = self.logf.dict["versao"]
            self.data   = datetime.strptime(self.logf.dict["data"], "%Y-%m-%d %X.%f")
            
        print()

    def iniciar(self):
        self.events.set()
        in_threads = [self.monitorar]
        threads = [threading.Thread(target=i) for i in in_threads]
        print("Iniciando threads...\n")
        for i in threads: i.start()
        
        try:
            while 1:
                time.sleep(.1)
        except KeyboardInterrupt:
            print("Finalizando processo...") # Mata o processo
            self.logf.salvar()
            os.popen("taskkill /PID " + str(os.getpid()) + " /F")

    def resolver_mudanca(self, alteracao):
        if len(alteracao) != 2 : # Não é renomear
            acao, diretorio = alteracao.split(" -- ")
            if os.path.isfile(diretorio):
                pass
            else:
                dir = util.mudar_caminho(diretorio, self.dir_backup, self.dir_superv)
                if acao == "Created":
                    print("Criar diretorio %s ..." % dir)
                    util.criar_diretorio(dir)
                    self.alteracoes.remove(alteracao)
                elif acao == "Deleted":
                    print("Deletar diretorio %s ..." % dir)
                    util.deletar_diretorio(dir)
                    self.alteracoes.remove(alteracao)
        else:
            dir1, dir2 = alteracao[0].split(" -- ")[1], alteracao[1].split(" -- ")[1] 
            dir1 = util.mudar_caminho(dir1, self.dir_backup, self.dir_superv)
            dir2 = util.mudar_caminho(dir2, self.dir_backup, self.dir_superv)
            print("Renomar diretorio ou arquivo\nDe: %s" % dir1)
            print("Para: %s" % dir2)
            util.renomear_arquivo_ou_diretorio(dir1, dir2)

    def atualizar(self):
        #acao = {"Created", "Deleted":,"Updated":, "Renamed from something":, "Renamed from something":}
        while len(self.alteracoes):
            count = 0
            renomear = []
            for i in self.alteracoes:
                acao, diretorio = i.split(" -- ")
                if acao != "Renamed from something":
                    self.resolver_mudanca(i)
                elif count == 0:
                    renomear.append(i)
                    count += 1
                elif count == 1:
                    renomear.append(i)
                    self.resolver_mudanca(i)
                    count = 0
        
    def monitorar(self):
        print("Inicio do monitoramento...\n")
        while self.events.is_set():
            time.sleep(5)
            print("%15s : %s" % ("diff", datetime.now()-self.data))
            print(self.logf)
            print(*self.alteracoes, sep='\n')
            print()
            
            t = threading.Thread(self.atualizar())
            t.start()
            t.join()

# main é minha thread principal
def main():
    args = get_args()
    servidor = True if args.tipo == "servidor" else False

    # PRECISA DAR UMA OLHADA NESSA PARTE !!!
    # Ela esta formatada para pegar diretorio do windows...
    # Então precisa ver como ela vai fazer pra criar um diretorio de backup
    if servidor:
        args.dir_backup = (os.getcwd() + "//Backup").replace("\\", "//")
        if not os.path.exists(args.dir_backup):
            os.makedirs(args.dir_backup)
        print("\nDiretorio backup: %s" % args.dir_backup)
    
    svc_p = servico_principal(args.dir_superv, args.dir_backup, True)
    svc_p.iniciar()
    
main()

# Site base para observar o diretório
# http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html
