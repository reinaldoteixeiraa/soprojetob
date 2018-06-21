import threading
import argparse
import time
import sys
import os

# Para monitorar o windows necessita desses imports
import win32event
import win32file
import win32con


class BkpSync(object):
    def __init__(self, dir):
        self.is_server = dir == ""
        self.dir = dir if dir != "" else os.getcwd() + "//backup"
        self.dir.replace("\\", "//")
        self.alteracoes = []

        if not os.path.exists(self.dir) and self.is_server:
            os.makedirs(self.dir)
        elif not os.path.exists(self.dir):
            print("Diretório, no modo cliente, deve existir no sistema")
            sys.exit()

    def iniciar(self):
        for_threads = [self.monitorar, self.observador_win]
        threads = [threading.Thread(target=i) for i in for_threads]
        [i.start() for i in threads]

        try:
            while 1:
                time.sleep(.1)
        except KeyboardInterrupt:
            print("Finalizando processo...")  # Mata o processo
            os.popen("taskkill /PID " + str(os.getpid()) + " /F")

    def monitorar(self):
        while True:
            if len(self.alteracoes) > 0:
                print(*self.alteracoes, sep='\n')
                print()
            time.sleep(5)

    def observador_win(self):
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
                self.alteracoes.append(alteracao)


def get_args():
    parser = argparse.ArgumentParser(
        description="diretório para ser supervisionado")
    parser.add_argument("-dir", "--dir", type=str, default="C://Users//danie//Desktop//Dir",
                        help="diretório para ser supervisionado")
    parser.add_argument("-ip", "--ip", type=str, default="127.0.0.1",
                        help="ip da máquina que esta o servidor\npor padrao é o próprio computador")
    return parser.parse_args()


def main():
    args = get_args()

    svc_p = BkpSync(args.dir)
    svc_p.iniciar()


main()
