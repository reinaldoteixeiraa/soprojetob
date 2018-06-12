import argparse
import sys
from datetime import datetime
import time
import os.path
import itertools
import threading # import Thread, Event

def get_args():
    parser = argparse.ArgumentParser(description="diretório para ser supervisionado")
    parser.add_argument("-dp", "--dir_to_sync", type=str, default="C://Users//danie//Desktop//Dir",
                        help="diretório para ser supervisionado")
    return parser.parse_args()

def iniciar_servico(FILE_LOG, path_to_sync):
    print("--> Inicializado... {}".format(str(datetime.now())))
    if not os.path.isfile(FILE_LOG): # Primeira inicialização do serviço
        with open(FILE_LOG, "w") as file:
            file.write("path: %s\n" % path_to_sync)
            file.write("data: %s\n" % str(datetime.now()))
    else:                           # Inicialização com diretório já existente
        with open(FILE_LOG, "r") as file:
            r = [i.replace("\n", "").split(": ") for i in file.readlines()] 
            rd = dict(r)
            for i,j in rd.items():
                print("%10s : %s" % (i, j) )
            dif = datetime.now() - datetime.strptime(rd["data"], "%Y-%m-%d %X.%f")
            print("%10s : %s" % ("diff", str(dif)) )

def atualizar_servico(FILE_LOG, path_to_sync, event):
    while event.is_set():
        time.sleep(5)
        print("--> Atualizando... {}".format(str(datetime.now())))
        with open(FILE_LOG, "r") as file:
            r = [i.replace("\n", "").split(": ") for i in file.readlines()] 
            rd = dict(r)
            for i,j in rd.items():
                print("%10s : %s" % (i, j) )
            dif = datetime.now() - datetime.strptime(rd["data"], "%Y-%m-%d %X.%f")
            print("%10s : %s" % ("diff", str(dif)) )
        with open(FILE_LOG, "w") as file:
            file.write("path: %s\n" % path_to_sync)
            file.write("data: %s\n" % str(datetime.now()))


# main é minha thread principal
def main():
    args = get_args()
    path_to_sync = args.dir_to_sync
    FILE_LOG = "LOG.txt"
    iniciar_servico(FILE_LOG, path_to_sync)

    events = threading.Event()
    events.set()
    t1 = threading.Thread(target=atualizar_servico, args=[FILE_LOG, path_to_sync, events])
    
    t1.start()

    try:
        while 1:
            time.sleep(.1)
    except KeyboardInterrupt:
        print("Finalizando threads...")
        events.clear()
        t1.join()
    
    
main()

'''
import win32file
import win32event
import win32con
import os, time, sys


def get():
    return win32file.ReadDirectoryChangesW( hDir, 1024, True, win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
            win32con.FILE_NOTIFY_CHANGE_DIR_NAME | win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
            win32con.FILE_NOTIFY_CHANGE_SIZE | win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
            win32con.FILE_NOTIFY_CHANGE_SECURITY, None, None
    )

path_to_watch = sys.argv[1] if len(sys.argv) > 1 else 'C://Users//danie//Desktop//Dir'
path_to_sync = sys.argv[2] if len(sys.argv) > 2 else 'C://Users//danie//Desktop//Sync'

ACTIONS = {1 : "Created", 2 : "Deleted",3 : "Updated",4 : "Renamed from something",5 : "Renamed from something"}
FILE_LIST_DIRECTORY = 0x0001

hDir = win32file.CreateFile(
    path_to_watch, FILE_LIST_DIRECTORY, win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
    None, win32con.OPEN_EXISTING, win32con.FILE_FLAG_BACKUP_SEMANTICS, None
)
while 1:
    time.sleep(1)
    results = get()
    for action, file in results:
        print(os.path.join(path_to_watch, file))
        print("%s" % os.listdir(os.path.join(path_to_watch, file)))
        try:
            print(os.path.join(path_to_sync, file))
            print("%s" % os.listdir(os.path.join(path_to_sync, file)))
        except:
            pass
        full_filename = os.path.join(path_to_watch, file)
        print(full_filename, ACTIONS.get(action, "Unknown"))
'''


# Site base para observar o diretório
# http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html
