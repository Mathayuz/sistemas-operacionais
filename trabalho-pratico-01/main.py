# main.py
import sys
import socket
import threading
import time
import select
from collections import deque
import math


# --- Clock Component ---
def run_clock(port_clock: int):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", port_clock))
    server.listen(2)
    conn_emitter, _ = server.accept()
    conn_scheduler, _ = server.accept()

    clock = 0
    try:
        while True:
            # envia tick
            conn_emitter.sendall((f"{clock}\n").encode())
            time.sleep(0.005)
            conn_scheduler.sendall((f"{clock}\n").encode())
            # recebe eventual TERMINATE
            r, _, _ = select.select([conn_scheduler], [], [], 0.095)
            if r:
                msg = conn_scheduler.recv(64).decode().strip().upper()
                if msg == "TERMINATE":
                    break
            clock += 1
    finally:
        conn_emitter.close()
        conn_scheduler.close()
        server.close()


# --- Emitter Component ---
def run_emitter(port_emitter: int, arquivo_tarefas: str):
    sock_clock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_clock.connect(("localhost", 4000))

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", port_emitter))
    server.listen(1)
    conn_sched, _ = server.accept()

    tasks = []
    with open(arquivo_tarefas) as f:
        for line in f:
            id_, t0, dur, prio = line.strip().split(";")
            tasks.append({"id": id_, "t0": int(t0), "dur": int(dur), "prio": int(prio)})

    pending = list(tasks)
    done_sent = False

    try:
        while True:
            clk = int(sock_clock.recv(64).decode())
            # emite tarefas no tempo
            for t in [t for t in pending if t["t0"] == clk]:
                msg = f"TASK;{t['id']};{t['dur']};{t['prio']}"
                conn_sched.sendall((msg + "\n").encode())
                pending.remove(t)

            # sinaliza fim de emissão
            if not pending and not done_sent:
                conn_sched.sendall("DONE\n".encode())
                done_sent = True

            # verifica TERMINATE
            r, _, _ = select.select([conn_sched], [], [], 0.01)
            if r:
                if conn_sched.recv(64).decode().strip().upper() == "TERMINATE":
                    break
    finally:
        sock_clock.close()
        conn_sched.close()
        server.close()


# --- Scheduler Component ---
def run_scheduler(port_scheduler: int, algoritmo: str):
    sock_clock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_clock.connect(("localhost", 4000))
    sock_emit = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_emit.connect(("localhost", 4001))

    ready_queue = deque()
    rr_queue = deque()
    tasks_info = {}
    timeline = []
    all_emitted = False
    current = None
    quantum_left = 0
    emitter_buf = ""

    try:
        while True:
            # recebe clock
            clk = int(sock_clock.recv(64).decode())

            # lê mensagens do emissor, bufferiza linhas
            while True:
                r, _, _ = select.select([sock_emit], [], [], 0)
                if not r:
                    break
                raw = sock_emit.recv(256).decode()
                if not raw:
                    all_emitted = True
                    break
                emitter_buf += raw
                # processa todas linhas completas
                while "\n" in emitter_buf:
                    line, emitter_buf = emitter_buf.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(";")
                    if parts[0] == "DONE":
                        all_emitted = True
                    elif parts[0] == "TASK" and len(parts) == 4:
                        _, tid, dur, prio = parts
                        tasks_info[tid] = {
                            "arrival": clk,
                            "dur": int(dur),
                            "prio": int(prio),
                            "remain": int(dur),
                            "finish": None,
                        }
                        ready_queue.append(tid)
                        rr_queue.append(tid)

            # seleção de tarefa
            if algoritmo == "fcfs":
                if current is None and ready_queue:
                    current = ready_queue.popleft()
            elif algoritmo == "sjf":
                if current is None and ready_queue:
                    nxt = min(ready_queue, key=lambda t: tasks_info[t]["dur"])
                    ready_queue.remove(nxt)
                    current = nxt
            elif algoritmo == "prioc":
                if current is None and ready_queue:
                    nxt = min(ready_queue, key=lambda t: tasks_info[t]["prio"])
                    ready_queue.remove(nxt)
                    current = nxt
            elif algoritmo == "rr":
                if current is None and rr_queue:
                    current = rr_queue.popleft()
                    quantum_left = 3
            elif algoritmo == "srtf":
                candidates = list(ready_queue) + ([current] if current else [])
                if candidates:
                    nxt = min(candidates, key=lambda t: tasks_info[t]["remain"])
                    if nxt != current:
                        if current and tasks_info[current]["remain"] > 0:
                            ready_queue.append(current)
                        if nxt in ready_queue:
                            ready_queue.remove(nxt)
                        current = nxt
            elif algoritmo == "priop":
                candidates = list(ready_queue) + ([current] if current else [])
                if candidates:
                    nxt = min(candidates, key=lambda t: tasks_info[t]["prio"])
                    if nxt != current:
                        if current and tasks_info[current]["remain"] > 0:
                            ready_queue.append(current)
                        ready_queue.remove(nxt) if nxt in ready_queue else None
                        current = nxt
            elif algoritmo == "priod":
                candidates = list(ready_queue) + ([current] if current else [])
                if candidates:
                    eff = {
                        t: tasks_info[t]["prio"] - (clk - tasks_info[t]["arrival"])
                        for t in candidates
                    }
                    nxt = min(candidates, key=lambda t: eff[t])
                    if nxt != current:
                        if current and tasks_info[current]["remain"] > 0:
                            ready_queue.append(current)
                        ready_queue.remove(nxt) if nxt in ready_queue else None
                        current = nxt

            # execução de um tick
            if current:
                timeline.append(current)
                tasks_info[current]["remain"] -= 1
                if algoritmo == "rr":
                    quantum_left -= 1
                if tasks_info[current]["remain"] == 0:
                    tasks_info[current]["finish"] = clk + 1
                    current = None
                elif algoritmo == "rr" and quantum_left == 0:
                    rr_queue.append(current)
                    current = None
            else:
                timeline.append("idle")

            # condição de término
            busy = any(info["finish"] is None for info in tasks_info.values())
            if all_emitted and not busy and current is None:
                break

        # sinaliza término
        sock_clock.sendall("TERMINATE".encode())
        sock_emit.sendall("TERMINATE".encode())

        # gera arquivo de saída
        with open(f"saida_{algoritmo}.txt", "w") as f:
            f.write(";".join(timeline) + "\n")
            turn_sum = 0
            wait_sum = 0
            n = len(tasks_info)
            for tid, info in tasks_info.items():
                turnaround = info["finish"] - info["arrival"]
                waiting = turnaround - info["dur"]
                turn_sum += turnaround
                wait_sum += waiting
                f.write(
                    f"{tid};{info['arrival']};{info['finish']};{turnaround};{waiting}\n"
                )
            avg_turn = math.ceil((turn_sum / n) * 10) / 10
            avg_wait = math.ceil((wait_sum / n) * 10) / 10
            f.write(f"{avg_turn};{avg_wait}\n")

    finally:
        sock_clock.close()
        sock_emit.close()


# --- main() ---
def main():
    if len(sys.argv) != 3:
        print("Uso: python main.py <arquivo_tarefas> <algoritmo>")
        sys.exit(1)
    arquivo, alg = sys.argv[1], sys.argv[2]
    validos = {"fcfs", "rr", "sjf", "srtf", "prioc", "priop", "priod"}
    if alg not in validos:
        print(f"Algoritmo inválido: {alg}")
        sys.exit(1)

    threads = [
        threading.Thread(target=run_clock, args=(4000,)),
        threading.Thread(target=run_emitter, args=(4001, arquivo)),
        threading.Thread(target=run_scheduler, args=(4002, alg)),
    ]
    for t in threads[:-1]:
        t.daemon = True
    for t in threads:
        t.start()
    threads[-1].join()


if __name__ == "__main__":
    main()
