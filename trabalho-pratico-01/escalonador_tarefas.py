import socket
import time
import sys
import math
import threading
from dataclasses import dataclass

@dataclass
class Tarefa:
    """
    Representa uma tarefa com um identificador, tempo de chegada, tempo de execução e prioridade.
    
    """
    id: int
    tempo_ingresso: int
    duracao_prevista: int
    prioridade: int

def fcfs(tarefas: list[Tarefa]) -> list[Tarefa]:
    """
    Simula o escalonamento de tarefas usando o algoritmo FCFS (First-Come, First-Served).
    """
    pass

def rr(tarefas: list[Tarefa], quantum: int=3) -> list[Tarefa]:
    """
    Simula o escalonamento de tarefas usando o algoritmo RR (Round Robin).
    """
    pass

def sjf(tarefas: list[Tarefa]) -> list[Tarefa]:
    """
    Simula o escalonamento de tarefas usando o algoritmo SJF (Shortest Job First).
    """
    pass

def srtf(tarefas: list[Tarefa]) -> list[Tarefa]:
    """
    Simula o escalonamento de tarefas usando o algoritmo SRTF (Shortest Remaining Time First).
    """
    pass

def prioc(tarefas: list[Tarefa]) -> list[Tarefa]:
    """
    Simula o escalonamento de tarefas usando o algoritmo PRIOC (Prioridade com Inversão de Contexto).
    """
    pass

def priop(tarefas: list[Tarefa]) -> list[Tarefa]:
    """
    Simula o escalonamento de tarefas usando o algoritmo PRIOP (Prioridade com Preempção).
    """
    pass

def priod(tarefas: list[Tarefa]) -> list[Tarefa]:
    """
    Simula o escalonamento de tarefas usando o algoritmo PRIOD (Prioridade Dinâmica).
    """
    pass

def start_clock():
    """
    Inicia o relógio do sistema para simular o tempo de execução das tarefas.
    """
    pass

def read_tasks(file_path: str) -> list[Tarefa]:
    """
    Lê as tarefas de um arquivo e retorna uma lista de objetos Tarefa.
    """
    pass

def emit_tasks(tarefas: list[Tarefa], file_path: str):
    """
    Emite as tarefas para um arquivo.
    """
    pass

def schedule_tasks(tarefas: list[Tarefa], algoritmo: str) -> list[Tarefa]:
    """
    Escalona as tarefas usando o algoritmo especificado.
    """
    if algoritmo == "FCFS":
        return fcfs(tarefas)
    elif algoritmo == "RR":
        return rr(tarefas)
    elif algoritmo == "SJF":
        return sjf(tarefas)
    elif algoritmo == "SRTF":
        return srtf(tarefas)
    elif algoritmo == "PRIOc":
        return prioc(tarefas)
    elif algoritmo == "PRIOp":
        return priop(tarefas)
    elif algoritmo == "PRIOd":
        return priod(tarefas)
    else:
        raise ValueError(f"Algoritmo desconhecido: {algoritmo}")
    
def write_output(tarefas: list[Tarefa], file_path: str):
    """
    Escreve o resultado do escalonamento em um arquivo.
    """
    pass

def main():
    """
    Função principal para executar o escalonador de tarefas.
    """
    pass

if __name__ == "__main__":
    main()