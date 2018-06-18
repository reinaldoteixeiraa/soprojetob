from servico_unico import servico_principal
import os
import util


if __name__ == "__main__":
    dir, backup, ip, servidor = util.inicializando()
    svc_p = servico_principal(dir, backup, servidor)
    svc_p.iniciar()
