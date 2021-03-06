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
from servidor import servidor_TCP
from cliente import cliente_TCP


class servico_principal(object):
    def __init__(self, dir_superv, dir_backup, serv=True):
        print("Iniciando %s..." % ("servidor" if serv else "cliente"))
        name_log = "LOG_Principal.txt" if serv else "LOG_Cliente.txt"
        self.logf = log_file(name_log)
        self.servidor = serv
        self.dir_superv = dir_superv
        self.dir_backup = dir_backup
        self.versao = 0
        self.events = threading.Event()
        self.data = datetime.now()
        self.alteracoes = []

        keys = ["path supervisionado", "path backup",
                "data", "versao", "Files", "Diretorios"]
        values = [self.dir_superv, self.dir_backup,
                  str(self.data), 0, [], []]

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

        print()

    def iniciar(self):
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
            self.logf.salvar()
            os.popen("taskkill /PID " + str(os.getpid()) + " /F")

    def observador_win(self):
        ACTIONS = {1: "Created", 2: "Deleted", 3: "Updated",
                   4: "Renamed from something", 5: "Renamed from something"}
        FILE_LIST_DIRECTORY = 0x0001
        diretorio = self.dir_backup if self.servidor else self.dir_superv
        # print(diretorio)
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
                self.TCP.msgs.append(alteracao)

    def resolver_mudanca(self, alteracao):
        if len(alteracao) != 2:  # Não é renomear
            acao, diretorio = alteracao.split(" -- ")
            if os.path.isfile(diretorio):
                pass
            else:
                dir = util.mudar_caminho(
                    diretorio, self.dir_backup, self.dir_superv)
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
            dir1 = util.mudar_caminho(dir1, self.dir_backup, self.dir_superv)
            dir2 = util.mudar_caminho(dir2, self.dir_backup, self.dir_superv)
            #print("Renomar diretorio ou arquivo\nDe: %s" % dir1)
            #print("Para: %s" % dir2)
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

    def monitorar(self):
        print("Inicio do monitoramento...\n")
        while self.events.is_set():
            time.sleep(5)
            #print("%15s : %s" % ("diff", datetime.now()-self.data))
            # print(self.logf)
            print(*self.alteracoes, sep='\n')
            print()

            if self.servidor:
                t = threading.Thread(self.atualizar())
                t.start()
                t.join()

# Site base para observar o diretório
# http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html
