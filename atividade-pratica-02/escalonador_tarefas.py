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
            print("[CLOCK] Todas as conexões estabelecidas. Iniciando o relógio...")
            
            # Recebe mensagem de término do Escalonador de Tarefas
            # DPS TEM QUE TIRAR ESSA THREAD DAQUI, AS THREAD VAO ESTAR SO NA MAIN (EU ACHO)
            threading.Thread(target=self.receive_messages, args=(self.conexoes[1],)).start


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

    def receive_messages(self, conn):
        """
        Recebe mensagens do Escalonador de Tarefas.
        Receber uma mensagem indicando que o Escalonador de Tarefas terminou a simulação.
        """
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode()
            print(f"[CLOCK] Mensagem recebida do Escalonador: {message}")
            if message == "Fim da simulação":
                print("[CLOCK] Encerrando o relógio.")
                self.stop()
                break
        conn.close()

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
    def __init__(self, file_path: str, porta_clock = 4000, porta= 4001, porta_escalonador= 4002):
        self.tarefas = self.read_tasks(file_path)
        self.current_index = 0
        self.porta_clock = porta_clock
        self.porta = porta
        self.porta_escalonador = porta_escalonador

    def read_tasks(self, file_path: str) -> list[Tarefa]:
        tarefas = []
        with open(file_path, 'r') as file:
            for line in file:
                id, tempo_ingresso, duracao_prevista, prioridade = map(int, line.strip().split(';'))
                tarefas.append(Tarefa(id, tempo_ingresso, duracao_prevista, prioridade))
        return tarefas
    
    def start(self):
        # Conecta ao Clock
        print(f"[EMISSOR] Iniciando conexão com o Clock na porta {self.porta_clock}")
        socket_clock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_clock.connect((host, self.porta_clock))
        print(f"[EMISSOR] Conectado ao Clock na porta {self.porta_clock}")

        # Conecta ao Escalonador de Tarefas
        print(f"[EMISSOR] Iniciando conexão com o Escalonador de Tarefas na porta {self.porta_escalonador}")
        socket_escalonador = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_escalonador.bind((host, self.porta_escalonador))
        socket_escalonador.listen(1)
        conn_escalonador, addr = socket_escalonador.accept()
        print(f"[EMISSOR] Conectado ao Escalonador de Tarefas na porta {self.porta_escalonador} de {addr}")

        # Inicia o loop de emissão de tarefas
        while self.current_index < len(self.tarefas):
            # Recebe o tempo atual do clock
            data = socket_clock.recv(1024)
            if not data:
                break
            tempo_atual = int(data.decode())
            print(f"[EMISSOR] Tempo atual recebido do Clock: {tempo_atual}")

            # Verifica se deve emitir a próxima tarefa
            if self.tarefas[self.current_index].tempo_ingresso == tempo_atual:
                tarefa = self.tarefas[self.current_index]
                print(f"[EMISSOR] Emitindo tarefa: {tarefa}")
                conn_escalonador.sendall(f"{tarefa.id};{tarefa.tempo_ingresso};{tarefa.duracao_prevista};{tarefa.prioridade}".encode())
                self.current_index += 1
            else:
                print(f"[EMISSOR] Aguardando tempo de ingresso da tarefa {self.tarefas[self.current_index].id} ({self.tarefas[self.current_index].tempo_ingresso})")
        # Envia mensagem ao Escalonador de Tarefas indicando que todas as tarefas foram emitidas
        conn_escalonador.sendall(b"Todas as tarefas foram escalonadas")

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
    def __init__(self, algoritmo, porta_clock: int = 4000, porta_emissor: int = 4001, porta: int = 4002):
        self.algoritmo = algoritmo
        self.tarefas_prontas = []
        self.tarefa_em_execucao = None
        self.clock_atual = 0
        self.porta_clock = porta_clock
        self.porta_emissor = porta_emissor
        self.porta = porta
        self.rodando = True
        self.tarefas_emitidas_acabaram = False

    def enviar_mensagem(self, destino, mensagem):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(destino)
                s.sendall(mensagem.encode())
        except ConnectionRefusedError:
            print(f"[Escalonador]: Falha ao conectar no {destino}")

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('localhost', self.porta))
        s.listen()

        # Inicia o loop de escalonamento
        while self.rodando:
            conn, addr = s.accept()
            with conn:
                mensagem = conn.recv(1024).decode()

                # Recebeu a mensagem do Clock
                if mensagem.startswith("CLOCK"):
                    self.clock_atual = int(mensagem.split()[1])
                    print(f"[T{self.clock_atual} - Escalonador] Recebeu Clock {self.clock_atual}.")
                    self.executar_escalonamento()

                # Recebeu sinal de término de emissão
                elif mensagem == "Todas as tarefas foram escalonadas":
                    print(f"[Escalonador]: Recebeu sinal de término do Emissor.")
                    self.tarefas_emitidas_acabaram = True

                # Recebeu tarefa
                else:
                    # Verifica se há tarefas prontas para serem escalonadas
                    if self.tarefas_prontas:
                        tarefa = self.tarefas_prontas.pop(0)
                        print(f"[ESCALONADOR] Executando tarefa: {tarefa.id} no tempo {tempo_atual}")
                        # implementar o algoritmo de escalonamento aqui !!

                        time.sleep(tarefa.duracao_prevista / 1000)  # Simula a execução da tarefa
                        print(f"[ESCALONADOR] Tarefa {tarefa.id} concluída no tempo {tempo_atual + tarefa.duracao_prevista}")

        def fcfs(self):
            """
            Simula o escalonamento de tarefas usando o algoritmo FCFS (First-Come, First-Served).
            """
            pass

        def rr(self):
            """
            Simula o escalonamento de tarefas usando o algoritmo RR (Round Robin).
            """
            pass

        def sjf(self):
            """
            Simula o escalonamento de tarefas usando o algoritmo SJF (Shortest Job First).
            """
            pass

        def srtf(self):
            """
            Simula o escalonamento de tarefas usando o algoritmo SRTF (Shortest Remaining Time First).
            """
            pass

        def prioc(self):
            """
            Simula o escalonamento de tarefas usando o algoritmo PRIOC (Prioridade com Inversão de Contexto).
            """
            pass

        def priop(self):
            """
            Simula o escalonamento de tarefas usando o algoritmo PRIOP (Prioridade com Preempção).
            """
            pass

        def priod(self):
            """
            Simula o escalonamento de tarefas usando o algoritmo PRIOD (Prioridade Dinâmica).
            """
            pass

    
def write_output(tarefas: list[Tarefa], file_path: str):
    """
    Escreve o resultado do escalonamento em um arquivo.
    """
    pass

def main():
    """
    Função principal para executar os componentes do sistema.
    Inicia o Clock, Emissor de Tarefas e Escalonador de Tarefas.
    Cada componente deve ser executado em uma thread separada.
    """
     #  Verifica quantidade de argumentos
    if len(sys.argv) != 3:
        print("Erro: Quantidade inválida de argumentos.")
        print("Uso: python escalonador_tarefas.py <caminho_do_arquivo> <algoritmo>")

    caminho_tarefas = sys.argv[1]
    algoritmo = sys.argv[2]

    clock = Clock()
    emissor = emissor_de_tarefas(caminho_tarefas)
    escalonador = escalonador_de_tarefas(algoritmo)

    # Inicia o Clock em uma thread
    threading.Thread(target=clock.start).start()

    # Inicia o Emissor de Tarefas em uma thread
    threading.Thread(target=emissor.start).start()

    # Inicia o Escalonador de Tarefas em uma thread
    threading.Thread(target=escalonador.start).start()

if __name__ == "__main__":
    main()