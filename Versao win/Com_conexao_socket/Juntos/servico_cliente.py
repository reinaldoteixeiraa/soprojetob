import sys
import time
import os
import socket

import win32file
import win32event
import win32con

import threading  # import Thread, Event
import util  # da minha pasta
from datetime import datetime
from log_class import log_file
#from servidor import servidor_TCP
from cliente import cliente_TCP
import util


class servico_cliente(cliente_TCP):
    def __init__(self, dir):
        super(servico_cliente, self).__init__()
        print("Iniciando CLIENTE...")
        name_log = "LOG_Cliente.txt"
        self.logf = log_file(name_log)
        self.diretorio = dir
        self.events = threading.Event()
        self.data = datetime.now()
        self.alteracoes = []

        keys = ["path", "data", "versao", "files", "diretorios"]
        values = [dir, str(self.data), 0, [], []]

        # Primeira inicialização do serviço
        if not os.path.isfile(self.logf.name_file):
            print("Criação de log para a primeira inicialização...")
            self.logf.add_arg(keys, values)
        else:  # Inicialização com diretório já existente
            print("Carregando log para inicialização em um diretório já monitorado...")
            self.logf.carregar()
            self.logf.set_arg(keys[:2], values[:2])
            self.versao = self.logf.dict["versao"]
            self.data = datetime.strptime(
                self.logf.dict["data"], "%Y-%m-%d %X.%f")

    def iniciar(self):
        self.iniciar_cliente()
        self.socket.send(bytes("Iniciando", 'utf-8'))
        self.socket.send(util.ler_arquivo(self.logf.name_file))
        self.events.set()
        in_threads = [self.monitorar, self.observador_win]
        threads = [threading.Thread(target=i) for i in in_threads]
        print("Iniciando threads...\n")
        for i in threads:
            i.start()
        try:
            while 1:
                time.sleep(.1)
        except KeyboardInterrupt:
            print("Finalizando processo...")  # Mata o processo
            self.socket.close()
            self.logf.salvar()
            os.popen("taskkill /PID " + str(os.getpid()) + " /F")

    def observador_win(self):
        diretorio = self.diretorio
        ACTIONS = {1: "Created", 2: "Deleted", 3: "Updated",
                   4: "Renamed from something", 5: "Renamed from something"}
        FILE_LIST_DIRECTORY = 0x0001
        hDir = win32file.CreateFile(
            diretorio, FILE_LIST_DIRECTORY, win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
            None, win32con.OPEN_EXISTING, win32con.FILE_FLAG_BACKUP_SEMANTICS, None
        )

        while True:
            results = win32file.ReadDirectoryChangesW(hDir, 1024, True, win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                                                      win32con.FILE_NOTIFY_CHANGE_DIR_NAME | win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                                                      win32con.FILE_NOTIFY_CHANGE_SIZE | win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                                                      win32con.FILE_NOTIFY_CHANGE_SECURITY, None, None
                                                      )
            for action, file in results:
                token = " -- "
                full_filename = os.path.join(diretorio, file)
                alteracao = str(ACTIONS.get(action, "Unknown")) + \
                    token + str(full_filename).replace("\\", "//")
                self.alteracoes.append(alteracao)

    def monitorar(self):
        print("Inicio do monitoramento...\n")
        while self.events.is_set():
            time.sleep(5)
            print(*self.alteracoes, sep='\n')
            print()

# Site base para observar o diretório
# http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html


'''
    def resolver_mudanca(self, alteracao):
        if len(alteracao) != 2:  # Não é renomear
            acao, diretorio = alteracao.split(" -- ")
            if os.path.isfile(diretorio):
                pass
            else:
                dir = self.diretorio + diretorio
                if acao == "Created":
                    #print("Criar diretorio %s ..." % dir)
                    util.criar_diretorio(dir)
                    self.alteracoes.remove(alteracao)
                elif acao == "Deleted":
                    #print("Deletar diretorio %s ..." % dir)
                    util.deletar_diretorio(dir)
                    self.alteracoes.remove(alteracao)
        else:
            dir1 = alteracao[0].split(" -- ")[1]
            dir2 = alteracao[1].split(" -- ")[1]
            dir1 = self.diretorio + dir1
            dir2 = self.diretorio + dir2
            util.renomear_arquivo_ou_diretorio(dir1, dir2)

    def atualizar(self):
        # acao = {"Created", "Deleted":,"Updated":, "Renamed from something":, "Renamed from something":}
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
'''
