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
#from cliente import cliente_TCP


class servico_servidor(servidor_TCP):
    def __init__(self, dir):
        super(servico_servidor, self).__init__()
        print("Iniciando SERVIDOR...")
        name_log = "LOG_Principal.txt"
        self.logf = log_file(name_log)
        self.diretorio = dir
        self.events = threading.Event()
        self.data = datetime.now()
        self.alteracoes = []

        keys = ["path", "data", "versao", "files", "diretorios"]
        values = [dir, str(self.data), 0, [], []]

        # Primeira inicialização do serviço
        if not os.path.isfile(name_log):
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
        self.iniciar_servidor()
        self.events.set()
        in_threads = [self.monitorar, self.observador_win]
        threads = [threading.Thread(target=i) for i in in_threads]
        for i in threads:
            i.start()

        try:
            while 1:
                if len(self.msgs):
                    for i in self.msgs:
                        self.enviar_mensagem(i)
        except KeyboardInterrupt:
            print("Finalizando processo...")  # Mata o processo
            self.socket.close()
            self.logf.salvar()
            os.popen("taskkill /PID " + str(os.getpid()) + " /F")

    def observador_win(self):
        print("Inicio da observação...")
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
        print("Inicio do monitoramento...")
        while self.events.is_set():
            time.sleep(5)
            #print("%15s : %s" % ("diff", datetime.now()-self.data))
            # print(self.logf)
            print(*self.alteracoes, sep='\n')
            print()
            '''
            t = threading.Thread(self.atualizar())
            t.start()
            t.join()
            '''

# Site base para observar o diretório
# http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html
