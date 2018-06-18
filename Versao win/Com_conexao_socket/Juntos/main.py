from servico_servidor import servico_servidor
from servico_cliente import servico_cliente
import os
import util


if __name__ == "__main__":
    dir, backup, ip, servidor = util.inicializando()
    svc_p = servico_servidor(backup) if servidor else servico_cliente(dir)
    svc_p.iniciar()
