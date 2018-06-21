import threading
import time
import sys
import os

# Para monitorar o windows necessita desses imports
import win32event
import win32file
import win32con

# Includes para controlar o servidor do socket
from servidor import servidor
from cliente import cliente

# Include para modificar o diretorio
import util


class servico(object):
    def __init__(self, dir):
        self.is_server = dir == ""
        self.dir = dir if dir != "" else os.getcwd() + "//backup"
        self.dir.replace("\\", "//")
        self.alteracoes_me = []

        # Variáveis para tratar as ocorrencias do servidor
        self.servidor = servidor() if self.is_server else cliente()
        self.alteracoes_from = []
        self.dir_usuarios = []
        self.token = " -- "
        self.recebi = {}

        if not os.path.exists(self.dir) and self.is_server:
            os.makedirs(self.dir)
        elif not os.path.exists(self.dir):
            print("Diretório, no modo cliente, deve existir no sistema")
            sys.exit()

    def add_recebi(self, key, value):
        if key not in self.recebi.keys():
            self.recebi[key] = [value]
        else:
            self.recebi[key].append(value)

    def consome_recebi(self, key):
        pop = self.recebi[key].pop(0)
        if len(self.recebi[key]) == 0:
            self.recebi.pop(key)
        return pop

    def iniciar(self):
        '''
            Iniciar o programa. Cria e executa as threads necessárias para rodar o programa e fica esperando por uma tecla de interrupção.
            Se a tecla é pressionada, ele mata o processo.

            Deve ser iniciada pelo usuário.
        '''
        self.servidor.iniciar()
        # Primeira mensagem do cliente
        # Envia o diretirio dele para fazer as alterações necessarias
        if not self.is_server:
            self.servidor.send_message(
                "Conectado -- " + self.dir + self.token + "unk")

        for_threads = [self.observador_win, self.monitorar,
                       self.receber_servico, self.executar_acao]
        threads = [threading.Thread(target=i) for i in for_threads]
        [i.start() for i in threads]

        try:
            while 1:
                time.sleep(.1)
        except KeyboardInterrupt:
            print("Finalizando processo...")  # Mata o processo
            os.popen("taskkill /PID " + str(os.getpid()) + " /F")

    def executar_acao(self):
        '''
            Executado por uma Thread.
        '''
        while True:
            time.sleep(3)
            keys = list(map(str, self.recebi.keys()))
            valor = list(map(str, self.recebi.values()))
            for k, v in zip(keys, valor):
                print("key:", k)
                print(v)
            print()

    def detectar_acao(self):
        '''
            Faz as verificacoes necessarias para armazenar uma alteracao.

            Executado pelo metodo receber_servico.
        '''
        while len(self.alteracoes_from):
            for i in self.alteracoes_from:
                alteracao = i.split(self.token)
                # print(alteracao)
                acao = alteracao[0]
                dir = alteracao[1]
                isfile = alteracao[2]
                time.sleep(2)
                self.add_recebi(dir, [acao, isfile])
                self.alteracoes_from.pop(0)

    def receber_servico(self):
        '''
            Recebe todas as mensagens do servidor e armazena na variavel alteracoes_from da classe.

            Executado por uma Thread.
        '''
        while True:
            while self.servidor.ha_mensagens():
                msg = self.servidor.consumir_mensagem()
                alt = msg.split(self.token)
                acao = alt[0]
                dir = alt[1]
                isfile = alt[2]
                if acao == "Renamed from something":
                    msg1 = msg
                    dir1 = msg1.split(self.token)[1]
                    while not self.servidor.ha_mensagens():
                        time.sleep(0.01)
                    msg2 = self.servidor.consumir_mensagem()
                    acao = msg2.split(self.token)[0]
                    dir2 = msg2.split(self.token)[1]
                    self.add_recebi(dir1, [acao, dir2])
                else:
                    if isfile == "file":
                        dados = alt[3]
                        self.add_recebi(dir, [acao, isfile, dados])
                    else:
                        self.add_recebi(dir, [acao, isfile])
            else:
                time.sleep(1)

    def enviar_servico(self):
        '''
            Envia todas as mensagens de uma vez.
            Usa a ideia de fila para isso.

            Executado pelo metodo monitorar.
        '''
        while len(self.alteracoes_me):
            self.servidor.send_message(self.alteracoes_me.pop(0))

    def monitorar(self):
        '''
            Printa as alteracoes e envia a mensagem da alteracao pelo servidor.

            Executado por uma Thread.
        '''
        while True:
            if len(self.alteracoes_me) > 0:
                print("Enviei")
                print(*self.alteracoes_me, sep='\n')
                self.enviar_servico()
            time.sleep(5)

    def observador_win(self):
        ''' 
            Interface do windows para detectar a ação em um diretório.
            Parecido com o Inotify.

            Executado por uma Thread.
        '''
        diretorio = self.dir
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
                if os.path.isfile(full_filename):
                    alteracao += token + "file"
                    time.sleep(0.01)
                    alteracao += token + str(util.ler_arquivo(full_filename))
                elif os.path.isdir(full_filename):
                    alteracao += token + "dir"
                else:
                    alteracao += token + "unk"
                self.alteracoes_me.append(alteracao)
