import os
import shutil
import codecs


def fragmentar_arquivo(dados):
    resultado = []
    t = 500
    for i in range(len(dados)//t+1):
        if i*t+t < len(dados):
            resultado.append(dados[i*t:i*t+t])
        else:
            break
    if len(dados) % t != 0:
        resultado.append(dados[i*t:])
    return resultado


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
    if os.path.isfile(nome):
        with codecs.open(nome, "r", encoding='utf-8', errors='ignore') as file:
            lendo = file.read()
            if dados == lendo:
                return None
    with codecs.open(nome, "w+", encoding='utf-8', errors='ignore') as file:
        file.write(dados)


def atualizar_arquivo(nome, dados):
    if os.path.isfile(nome):
        with codecs.open(nome, "r", encoding='utf-8', errors='ignore') as file:
            lendo = file.read()
            if dados == lendo:
                return None
        with codecs.open(nome, "a", encoding='utf-8', errors='ignore') as file:
            file.write(dados)


def ler_arquivo(nome):
    if os.path.isfile(nome):
        with codecs.open(nome, "r", encoding='utf-8', errors='ignore') as file:
            lendo = file.read()
        return lendo
    return ""


def renomear_arquivo_ou_diretorio(d1, d2):
    if os.path.isfile(d1):
        os.rename(d1, d2)


def criar_diretorio(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def deletar_diretorio(dir):
    # os.rmdir(dir)
    shutil.rmtree(dir, ignore_errors=True)
