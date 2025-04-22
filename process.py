from multiprocessing import Process
import os
import time


def info(title):
    print(f"\n[{title}]")
    print("Modulo:", __name__)
    print("Processo pai:", os.getppid())
    print("Processo atual:", os.getpid())


def f(name):
    info(f"Processo filho ({name})")
    for i in range(3):
        print(f"[{name}] contando {i+1}")
        time.sleep(1)


if __name__ == "__main__":
    info("Processo principal")

    nomes = ["bob", "alice", "john", "mary"]
    processos = []

    # Cria todos os processos
    for nome in nomes:
        p = Process(target=f, args=(nome,))
        processos.append(p)
        p.start()

    # Aguarda todos terminarem
    for p in processos:
        p.join()

    print("\n[Principal] Todos os processos terminaram.")
