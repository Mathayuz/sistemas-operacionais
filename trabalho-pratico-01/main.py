# Trabalho Prático 01 - Sistemas Operacionais
# Alunos:
# Caetano Vendrame Mantovani RA: 135846
# Matheus Cenerini Jacomini RA: 134700
# Data: 07/2025
import sys
import socket
import threading
import time
import select
from collections import deque
import math


# --- Componente do Clock ---
def rodar_clock(porta_clock: int):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", porta_clock))
    server.listen(2)
    conn_emissor, _ = server.accept()
    conn_escalonador, _ = server.accept()

    clock = 0
    try:
        while True:
            conn_emissor.sendall((f"{clock}\n").encode())
            time.sleep(0.005)
            conn_escalonador.sendall((f"{clock}\n").encode())

            r, _, _ = select.select([conn_escalonador], [], [], 0.095)
            if r:
                msg = conn_escalonador.recv(64).decode().strip().upper()
                if msg == "TERMINATE":
                    break
            clock += 1

    finally:
        conn_emissor.close()
        conn_escalonador.close()
        server.close()


# --- Componente do Emissor ---
def rodar_emissor(porta_emissor: int, arquivo_tarefas: str):
    sock_clock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_clock.connect(("localhost", 4000))

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", porta_emissor))
    server.listen(1)
    conn_escalonador, _ = server.accept()

    tarefas = []
    with open(arquivo_tarefas) as f:
        for linha in f:
            id_, t_ingresso, duracao, prio = linha.strip().split(";")
            tarefas.append({
                "id": id_,
                "t_ingresso": int(t_ingresso),
                "duracao": int(duracao),
                "prio": int(prio),
            })

    pendentes = list(tarefas)
    acabou_envio = False
    clock_buf = ""

    try:
        while True:
            raw = sock_clock.recv(256).decode()
            if not raw:
                break

            clock_buf += raw
            while "\n" in clock_buf:
                line, clock_buf = clock_buf.split("\n", 1)
                if not line:
                    continue
                clk = int(line)

            for t in [t for t in pendentes if t["t_ingresso"] == clk]:
                msg = f"TASK;{t['id']};{t['duracao']};{t['prio']}"
                conn_escalonador.sendall((msg + "\n").encode())
                pendentes.remove(t)

            if not pendentes and not acabou_envio:
                conn_escalonador.sendall("DONE\n".encode())
                acabou_envio = True

            r, _, _ = select.select([conn_escalonador], [], [], 0.01)
            if r:
                if conn_escalonador.recv(64).decode().strip().upper() == "TERMINATE":
                    break

    finally:
        sock_clock.close()
        conn_escalonador.close()
        server.close()


# --- Componente do Escalonador ---
def rodar_escalonador(porta_escalonador: int, algoritmo: str):
    sock_clock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_clock.connect(("localhost", 4000))
    sock_emit = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_emit.connect(("localhost", 4001))

    fila_prontas = deque()
    fila_rr = deque()
    tarefas_info = {}
    timeline = []
    todas_emitidas = False
    atual = None
    quantum_restante = 0
    buffer_emissor = ""
    clock_buf = ""

    try:
        while True:
            raw = sock_clock.recv(256).decode()
            if not raw:
                break

            clock_buf += raw
            while "\n" in clock_buf:
                line, clock_buf = clock_buf.split("\n", 1)
                if not line:
                    continue
                clk = int(line)

            # Processa mensagens do emissor
            while True:
                r, _, _ = select.select([sock_emit], [], [], 0)
                if not r:
                    break
                msg_emissor = sock_emit.recv(256).decode()
                if not msg_emissor:
                    todas_emitidas = True
                    break
                buffer_emissor += msg_emissor
                while "\n" in buffer_emissor:
                    linha, buffer_emissor = buffer_emissor.split("\n", 1)
                    linha = linha.strip()
                    if not linha:
                        continue
                    partes = linha.split(";")
                    if partes[0] == "DONE":
                        todas_emitidas = True
                    elif partes[0] == "TASK" and len(partes) == 4:
                        _, tid, duracao, prio = partes
                        tarefas_info[tid] = {
                            "chegada": clk,
                            "duracao": int(duracao),
                            "prio": int(prio),
                            "faltante": int(duracao),
                            "terminada": None,
                            "wait_time": 0,  # contador de espera
                        }
                        fila_prontas.append(tid)
                        fila_rr.append(tid)

            # Aging: incrementa espera de quem está na fila
            for tid in list(fila_prontas):
                tarefas_info[tid]["wait_time"] += 1
            # quem está executando não envelhece
            if atual:
                tarefas_info[atual]["wait_time"] = 0

            # Seleção de tarefa
            if algoritmo == "fcfs":
                if atual is None and fila_prontas:
                    atual = fila_prontas.popleft()

            elif algoritmo == "rr":
                if atual is None and fila_rr:
                    atual = fila_rr.popleft()
                    quantum_restante = 3

            elif algoritmo == "sjf":
                if atual is None and fila_prontas:
                    prox = min(fila_prontas, key=lambda t: tarefas_info[t]["duracao"])
                    fila_prontas.remove(prox)
                    atual = prox

            elif algoritmo == "srtf":
                candidatos = list(fila_prontas) + ([atual] if atual else [])
                if candidatos:
                    prox = min(candidatos, key=lambda t: tarefas_info[t]["faltante"])
                    if prox != atual:
                        if atual and tarefas_info[atual]["faltante"] > 0:
                            fila_prontas.append(atual)
                        if prox in fila_prontas:
                            fila_prontas.remove(prox)
                        atual = prox

            elif algoritmo == "prioc":
                if atual is None and fila_prontas:
                    prox = min(fila_prontas, key=lambda t: tarefas_info[t]["prio"])
                    fila_prontas.remove(prox)
                    atual = prox

            elif algoritmo == "priop":
                candidatos = list(fila_prontas) + ([atual] if atual else [])
                if candidatos:
                    prox = min(candidatos, key=lambda t: tarefas_info[t]["prio"])
                    if prox != atual:
                        if atual and tarefas_info[atual]["faltante"] > 0:
                            fila_prontas.append(atual)
                        if prox in fila_prontas:
                            fila_prontas.remove(prox)
                        atual = prox

            elif algoritmo == "priod":
                candidatos = list(fila_prontas) + ([atual] if atual else [])
                if candidatos:
                    # prioridade ajustada pelo tempo de espera
                    eff = {t: tarefas_info[t]["prio"] - tarefas_info[t]["wait_time"] for t in candidatos}
                    prox = min(candidatos, key=lambda t: (eff[t], tarefas_info[t]["chegada"]))
                    if prox != atual:
                        if atual and tarefas_info[atual]["faltante"] > 0:
                            fila_prontas.append(atual)
                        if prox in fila_prontas:
                            fila_prontas.remove(prox)
                        atual = prox
                        tarefas_info[atual]["wait_time"] = 0

            # Execução de um tick
            if atual:
                timeline.append(atual)
                tarefas_info[atual]["faltante"] -= 1
                if algoritmo == "rr":
                    quantum_restante -= 1
                if tarefas_info[atual]["faltante"] == 0:
                    tarefas_info[atual]["terminada"] = clk + 1
                    atual = None
                elif algoritmo == "rr" and quantum_restante == 0:
                    fila_rr.append(atual)
                    atual = None
            else:
                timeline.append("idle")

            # Condição de término
            ocupada = any(info["terminada"] is None for info in tarefas_info.values())
            if todas_emitidas and not ocupada and atual is None:
                break

        # Sinaliza término
        sock_clock.sendall("TERMINATE".encode())
        sock_emit.sendall("TERMINATE".encode())

        # Gera arquivo de saída
        saida_timeline = [t for t in timeline if t != "idle"]
        with open(f"saida_{algoritmo}.txt", "w") as f:
            f.write(";".join(saida_timeline) + "\n")
            turn_total = 0
            espera_total = 0
            n = len(tarefas_info)
            for tid, info in tarefas_info.items():
                turnaround = info["terminada"] - info["chegada"]
                espera = turnaround - info["duracao"]
                turn_total += turnaround
                espera_total += espera
                f.write(
                    f"{tid};{info['chegada']};{info['terminada']};{turnaround};{espera}\n"
                )
            media_turn = math.ceil((turn_total / n) * 10) / 10
            media_espera = math.ceil((espera_total / n) * 10) / 10
            f.write(f"{media_turn};{media_espera}\n")

    finally:
        sock_clock.close()
        sock_emit.close()


# --- main() ---
def main():
    if len(sys.argv) != 3:
        print("Uso: python main.py <arquivo_tarefas> <algoritmo>")
        sys.exit(1)
    arquivo, algoritmo = sys.argv[1], sys.argv[2]

    validos = {"fcfs", "rr", "sjf", "srtf", "prioc", "priop", "priod"}
    if algoritmo not in validos:
        print(f"Algoritmo inválido: {algoritmo}")
        sys.exit(1)

    threads = [
        threading.Thread(target=rodar_clock, args=(4000,)),
        threading.Thread(target=rodar_emissor, args=(4001, arquivo)),
        threading.Thread(target=rodar_escalonador, args=(4002, algoritmo)),
    ]

    for t in threads[:-1]:
        t.daemon = True

    for t in threads:
        t.start()
    threads[-1].join()


if __name__ == "__main__":
    main()