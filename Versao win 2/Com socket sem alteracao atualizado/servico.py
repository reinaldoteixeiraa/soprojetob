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
        self.resultados_observador = []
        self.alteracoes_me = []

        # Variáveis para tratar as ocorrencias do servidor
        self.servidor = servidor() if self.is_server else cliente()
        self.semaforo_recebi = threading.Semaphore()
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
                       self.receber_servico, self.executar_acao,
                       self.decodificar_observador]
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
            Executa as alteracoes armazenadas.

            Existe uma região critica concorrente com receber_servico.

            Se não existe alteracoes ele dorme.

            Executado por uma Thread.
        '''
        while True:
            # Região critica
            self.semaforo_recebi.acquire()
            dirs = list(map(str, self.recebi.keys()))
            self.semaforo_recebi.release()

            for dir in dirs:
                # Região critica
                self.semaforo_recebi.acquire()
                consumo = self.consome_recebi(dir)
                self.semaforo_recebi.release()

                dir_me = self.dir + dir
                acao = consumo[0]
                isfile = consumo[1]
                if acao == "Conectado":
                    print("Usuario conectado possui o diretorio:", dir)
                    self.dir_usuarios.append(dir)
                elif acao == "Created":
                    if isfile == "dir":
                        print("Diretorio criado:", dir)
                        # util.criar_diretorio(dir_me)
                    elif isfile == "file":
                        print("Arquivo criado:", dir)
                        dados = consumo[2]
                        print(dados)
                        #util.criar_arquivo(dir_me, dados)
                elif acao == "Deleted":
                    if os.path.isfile(dir_me):
                        print("Arquivo deletado:", dir)
                        # util.deletar_arquivo(dir_me)
                    if os.path.isdir(dir_me):
                        print("Diretorio deletado:", dir)
                        # util.deletar_diretorio(dir_me)
                elif acao == "Renamed from something":
                    dir2 = isfile
                    if os.path.isfile(dir_me):
                        print("Arquivo renomeado")
                    if os.path.isdir(dir_me):
                        print("Diretorio renomeado")
                    print("De:", dir)
                    print("Para:", dir2)
                    if os.path.isdir(dir_me) or os.path.isfile:
                        print("Esse arquivo ou diretório existe e posso altera-lo")
                        #util.renomear_arquivo_ou_diretorio(dir_me, self.dir+dir2)
                elif acao == "Updated":
                    if os.path.isfile(dir_me):
                        print("Arquivo alterado:", dir)
                        dados = consumo[2]
                        if os.path.isfile(dir_me):
                            print("Esse arquivo existe e posso atualiza-lo")
                            # util.criar_arquivo(dir_me, dados)
                else:  # Se eu não consegui fazer nada, coloca de volta na estrutura
                    print("Não existe um procedimento para essa ação ainda.")
                    print("Acao retornada para a estrutura.")
                    # Região critica
                    self.semaforo_recebi.acquire()
                    self.add_recebi(dir, consumo)
                    self.semaforo_recebi.release()
            else:
                time.sleep(1)

    def remover_diretorio_principal(self, dir):
        if not self.is_server:
            return dir.split("backup")[1]
        else:
            return util.comprimir_diretorio(dir, self.dir_usuarios)

    def receber_servico(self):
        '''
            Recebe todas as mensagens do servidor e armazena na variavel alteracoes_from da classe.
            Faz as verificacoes necessarias para armazenar uma alteracao.

            Se não existe mensagens ele dorme.

            Existe uma região critica concorrente com executar_acao.

            Executado por uma Thread.
        '''
        while True:
            while self.servidor.ha_mensagens():
                msg = self.servidor.consumir_mensagem()

                alt = msg.split(self.token)
                acao = alt[0]
                dir = alt[1]
                isfile = alt[2]

                dir = self.remover_diretorio_principal(dir)

                if acao == "Renamed from something":
                    while not self.servidor.ha_mensagens():
                        time.sleep(0.01)
                    msg2 = self.servidor.consumir_mensagem()

                    alt = msg2.split(self.token)
                    acao = alt[0]
                    dir2 = alt[1]
                    dir2 = self.remover_diretorio_principal(dir2)
                    # Regiao critica
                    self.semaforo_recebi.acquire()
                    self.add_recebi(dir, [acao, dir2])
                    self.semaforo_recebi.release()
                else:
                    # Regiao critica
                    self.semaforo_recebi.acquire()
                    if isfile == "file":
                        dados = alt[3]
                        self.add_recebi(dir, [acao, isfile, dados])
                    else:
                        self.add_recebi(dir, [acao, isfile])
                    self.semaforo_recebi.release()
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

            Se não existe alteracoes para enviar ele dorme.

            Executado por uma Thread.
        '''
        while True:
            if len(self.alteracoes_me) > 0:
                print("Enviei")
                print(*self.alteracoes_me, sep='\n')
                self.enviar_servico()
            else:
                time.sleep(1)

    def decodificar_observador(self):
        '''
            Transforma o resultado do observador em algo útil para a aplicação.

            Se não existe resultados do observador para decoficicar ele dorme.

            Executado por uma Thread.
        '''

        diretorio = self.dir
        ACTIONS = {1: "Created", 2: "Deleted", 3: "Updated",
                   4: "Renamed from something", 5: "Renamed from something"}
        while True:
            while len(self.resultados_observador) > 0:
                results = self.resultados_observador.pop(0)
                for action, file in results:
                    token = " -- "
                    full_filename = os.path.join(diretorio, file)
                    alteracao = str(ACTIONS.get(action, "Unknown")) + \
                        token + str(full_filename).replace("\\", "//")
                    if os.path.isfile(full_filename):
                        alteracao += token + "file"
                        time.sleep(0.001)
                        alteracao += token + \
                            str(util.ler_arquivo(full_filename))
                    elif os.path.isdir(full_filename):
                        alteracao += token + "dir"
                    else:
                        alteracao += token + "unk"
                    self.alteracoes_me.append(alteracao)
            else:
                time.sleep(1)

    def observador_win(self):
        ''' 
            Interface do windows para detectar a ação em um diretório.
            Parecido com o Inotify.

            Executado por uma Thread.
        '''
        diretorio = self.dir

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
            self.resultados_observador.append(results)
