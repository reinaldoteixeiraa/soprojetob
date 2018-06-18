import os
import shutil
import argparse


def get_args():
    parser = argparse.ArgumentParser(
        description="diretório para ser supervisionado")
    parser.add_argument("-ds", "--dir_superv", type=str, default="C://Users//danie//Desktop//Dir",
                        help="diretório para ser supervisionado")
    parser.add_argument("-dp", "--dir_backup", type=str, default="",
                        help="diretório backup para ser supervisionado")
    parser.add_argument("-ip", "--ip", type=str, default="127.0.0.1",
                        help="ip da máquina que esta o servidor\npor padrao é o próprio computador")
    parser.add_argument("-t", "--tipo", type=str, default="servidor",
                        help="define o tipo do observador")
    return parser.parse_args()


def inicializando():
    args = get_args()
    servidor = True if args.tipo == "servidor" else False
    if servidor:
        if args.dir_backup == "":
            args.dir_backup = (os.getcwd() + "//Backup").replace("\\", "//")
        if not os.path.exists(args.dir_backup):
            os.makedirs(args.dir_backup)
        print("\nDiretorio backup: %s" % args.dir_backup)
    return args.dir_superv, args.dir_backup, args.ip, servidor


def capturar_todos_arquivos_e_pastas(mypath):
    f = []
    dp = []
    dn = []
    for (dirpath, dirnames, filenames) in os.walk(mypath):
        dire = dirpath.replace(mypath, "")
        dn.extend(dirnames)
        dp.append(dire)
        f.extend(map(lambda x: dire+"\\"+x, filenames))
    dp.pop(0)
    return dp, f


def deletar_arquivo(nome):
    if os.path.isfile(nome):
        os.remove(nome)


def criar_arquivo(nome, dados):
    with open(nome, "wb") as file:
        file.write(dados)


def ler_arquivo(nome):
    with open(nome, "rb") as file:
        lendo = file.read()
    return lendo


def renomear_arquivo_ou_diretorio(d1, d2):
    os.rename(d1, d2)


def criar_diretorio(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def deletar_diretorio(dir):
    shutil.rmtree(dir, ignore_errors=True)


def mudar_caminho(dir_principal, dir_replace, dir_new):
    return dir_new + dir_principal.replace(dir_replace, "")
