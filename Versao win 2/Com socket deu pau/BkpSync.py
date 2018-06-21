import argparse
from servico import servico


def get_args():
    parser = argparse.ArgumentParser(
        description="diretório para ser supervisionado")
    parser.add_argument("-dir", "--dir", type=str, default="",
                        help="diretório para ser supervisionado")
    parser.add_argument("-ip", "--ip", type=str, default="127.0.0.1",
                        help="ip da máquina que esta o servidor\npor padrao é o próprio computador")
    return parser.parse_args()


def main():
    teste_dir = "C://Users//danie//Desktop//Dir"
    args = get_args()
    svc_p = servico(args.dir) if args.dir == "" else servico(teste_dir)
    svc_p.iniciar()


main()
