import os
import shutil


def comprimir_diretorio(dir, dirs):
    for i in dirs:
        if i in dir:
            return dir.replace(i, "")
    return dir


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
    os.remove(nome)


def criar_arquivo(nome, dados):
    with open(nome, "rb") as file:
        if dados == file.read():
            return None
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
    # os.rmdir(dir)
    shutil.rmtree(dir, ignore_errors=True)
