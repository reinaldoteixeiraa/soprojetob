
import win32file, win32event, win32con
import threading # import Thread, Event
import argparse, time, os
import socket

def get_args():
    parser = argparse.ArgumentParser(description="diretório para ser supervisionado")
    parser.add_argument("-ds", "--dir_superv", type=str, default="C://Users//danie//Desktop//Dir",
                        help="diretório para ser supervisionado")
    parser.add_argument("-dp", "--dir_backup", type=str, default="C://Users//danie//Documents//GitHub//soprojetob//Versao win//Sync",
                        help="diretório backup para ser supervisionado")
    parser.add_argument("-ip", "--ip", type=str, default="127.0.0.1",
                        help="ip da máquina que esta o servidor\npor padrao é o próprio computador")
    parser.add_argument("-t", "--tipo", type=str, default="servidor",
                        help="define o tipo do observador")                      
    return parser.parse_args()

class observador_win(object):
    def __init__(self, dir_superv, ip, port):
        self.dir_superv = dir_superv
        self.dest = (ip, port)
        self.UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def iniciar(self):
        t = threading.Thread(target=self.pegar_eventos_win)
        t.start()

        try:
            while 1:
                time.sleep(.1)
        except KeyboardInterrupt:
            print("Finalizando processo...") # Mata o processo
            self.UDP.close()
            os.popen("taskkill /PID " + str(os.getpid()) + " /F")

    def pegar_eventos_win(self):
        ACTIONS = {1 : "Created", 2 : "Deleted",3 : "Updated",4 : "Renamed from something",5 : "Renamed from something"}
        FILE_LIST_DIRECTORY = 0x0001
        hDir = win32file.CreateFile(
            self.dir_superv, FILE_LIST_DIRECTORY, win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
            None, win32con.OPEN_EXISTING, win32con.FILE_FLAG_BACKUP_SEMANTICS, None
        )

        while True:
            results = win32file.ReadDirectoryChangesW( hDir, 1024, True, win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                win32con.FILE_NOTIFY_CHANGE_DIR_NAME | win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                win32con.FILE_NOTIFY_CHANGE_SIZE | win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                win32con.FILE_NOTIFY_CHANGE_SECURITY, None, None
            )
            for action, file in results:
                token = " -- "
                full_filename = os.path.join(self.dir_superv, file)
                alteracao = str(ACTIONS.get(action, "Unknown")) + token + str(full_filename).replace("\\", "//")
                print(alteracao)
                # Enviando mudanca para o servico principal
                self.UDP.sendto(bytes(alteracao, 'utf-8'), self.dest)

def main():
    args = get_args()
    if args.tipo == "servidor":
        obsv = observador_win(args.dir_backup, args.ip, 7000)
    else:
        obsv = observador_win(args.dir_superv, args.ip, 7001)
    obsv.iniciar()

main()
