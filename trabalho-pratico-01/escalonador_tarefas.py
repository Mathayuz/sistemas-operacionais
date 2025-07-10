import socket
import time
import sys
import math
import threading
from dataclasses import dataclass

host = 'localhost'

@dataclass
class Tarefa:
    """
    Representa uma tarefa com um identificador, tempo de chegada, tempo de execução e prioridade.
    """
    id: int
    tempo_ingresso: int
    duracao_prevista: int
    prioridade: int

class Clock:
    """
    Classe responsável por simular o relógio (clock) da CPU.
    O tempo começa em 0 e é incrementado em uma unidade de tempo a cada chamada do método tick.
    Existe um delay de 100ms por incremento, simulando o avanço da linha do tempo.
    A cada incremento, o clock envia uma mensagem: 
        Primeiro ao Emissor de Tarefas;
        Após 5ms, ao Escalonador de Tarefas (isso garante que o Emissor insira as 
        tarefas antes do Escalonador tentar escaloná-las).
    """
    def __init__(self, porta: int = 4000):
        self.tempo_atual = 0
        self.rodando: bool = False
        self.porta = porta
        self.conexoes = []

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, self.porta))
            s.listen(2)
            print(f"[CLOCK] Clock iniciado na porta {self.porta}. Aguardando conexões...")

            # Aceita conexões de Emissor de Tarefas e Escalonador de Tarefas
            for _ in range(2):
                conn, addr = s.accept()
                print(f"[CLOCK] Conectado a {addr}")
                self.conexoes.append(conn)

            # Inicia o relógio
            self.rodando = True
            while self.rodando:
                # Delay de 100ms para simular o avanço do tempo
                time.sleep(0.1)
                
                # Incrementa o tempo do clock
                self.tempo_atual += 1
                print(f"[CLOCK] Tempo atual: {self.tempo_atual}")

                # Envia o tempo atual para o Emissor de Tarefas
                self.conexoes[0].sendall(str(self.tempo_atual).encode())
                
                # Aguarda 5ms antes de enviar ao Escalonador de Tarefas
                time.sleep(0.005)
                
                # Envia o tempo atual para o Escalonador de Tarefas
                self.conexoes[1].sendall(str(self.tempo_atual).encode())

    def stop(self):
        self.rodando = False

class emissor_de_tarefas:
    """
    Classe responsável por informar o escalonador de tarefas sobre as 
    tarefas que estão prontas para serem executadas para a fila de tarefas prontas.
    A  emissão  é  baseada  na  leitura  de  um  arquivo  de  entrada  informado  na execução  do  processo.
    Com cada novo valor de clock recebido via socket, o Emissor verifica se uma ou 
    mais tarefas devem ser inseridas na fila de prontas.
    Quando o Emissor inserir a última tarefa, deve enviar uma mensagem ao 
    escalonador de tarefas informando que todas as tarefas já foram emitidas.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.tarefas = self.read_tasks()
        self.current_index = 0

    def read_tasks(self) -> list[Tarefa]:
        tarefas = []
        with open(self.file_path, 'r') as file:
            for line in file:
                id, tempo_ingresso, duracao_prevista, prioridade = map(int, line.strip().split(';'))
                tarefas.append(Tarefa(id, tempo_ingresso, duracao_prevista, prioridade))
        return tarefas

    def emit_task(self):
        # Verifica se ainda há tarefas a serem emitidas
        if self.current_index < len(self.tarefas):
            # verifica se a tarefa deve ser emitida com base no tempo atual do clock
            pass
        else:
            print("Emissor: Todas as tarefas já foram emitidas.")
            # Enviar mensagem ao escalonador de tarefas
            return None

class escalonador_de_tarefas:
    """
    Classe responsável por escalonar as tarefas recebidas do Emissor de Tarefas.
    O Escalonador deve receber as tarefas e aplicar o algoritmo de escalonamento especificado.
    A cada novo valor de clock recebido via socket, o Escalonador executa o 
    algoritmo ativo e seleciona qual tarefa deve ocupar o processador.
    Após o término da última tarefa, o Escalonador deve:  
        Enviar uma mensagem ao Clock e ao Emissor sinalizando o fim da simulação;  
        Escrever o arquivo de saída com os dados da execução.
    O arquivo gerado pelo Escalonador ao final da simulação deve conter, exatamente nesta ordem:  
        Linha com a sequência de tarefas escalonadas a cada unidade de clock, separadas por “;".
        Uma linha por tarefa, contendo (separados por “;”):  
            ID;clock de ingresso na fila de prontas;clock de finalização;turnaround time;waiting time
        Por fim, a média dos tempos de execução e espera, separados por “;” 
        e arredondados para cima com 1 casa decimal.
    """
    def __init__(self):
        self.tarefas_prontas = []
        self.clock = Clock()
        self.running = True

    def receive_task(self, tarefa: Tarefa):
        # Adiciona a tarefa à fila de prontas
        self.tarefas_prontas.append(tarefa)

    def run(self):
        while self.running:
            # Recebe o tempo do clock e executa o algoritmo de escalonamento
            pass

    def finish(self):
        self.running = False
        # Enviar mensagem ao Clock e Emissor de Tarefas
        # Escrever arquivo de saída com os dados da execução
        pass

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