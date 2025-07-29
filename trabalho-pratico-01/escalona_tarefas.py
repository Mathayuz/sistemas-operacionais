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

class Escalonador:
    """
    Classe responsável por escalonar as tarefas recebidas do Emissor de Tarefas.
    O Escalonador deve receber a tarefa e aplicar o algoritmo de escalonamento especificado.
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
        """
        Inicializa o Escalonador com o algoritmo especificado.
        """
        self.algoritmo = algoritmo
        self.porta_clock = porta_clock
        self.porta_emissor = porta_emissor
        self.porta = porta
        self.tarefas_prontas = []
        self.tarefas_executadas = []
        self.tarefa_em_execucao = None
        self.rodando = False
        self.tarefas_emitidas_acabaram = False
        self.clock_atual = 0

    def enviar_mensagem(self, destino, mensagem):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(destino)
                s.sendall(mensagem.encode())
        except ConnectionRefusedError:
            print(f"[Escalonador]: Falha ao conectar no {destino}")

    def start(self):
        """
        Inicia o Escalonador, aguardando conexões do Clock e do Emissor de Tarefas.
        """
        self.rodando = True
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, self.porta))
            s.listen()
            print(f"[Escalonador]: Escutando na porta {self.porta}...")

            while self.rodando:
                conn, addr = s.accept()
                with conn:
                    print(f"[Escalonador]: Conexão estabelecida com {addr}")
                    data = conn.recv(1024)
                    if not data:
                        break
                    mensagem = data.decode()
                    print(f"[Escalonador]: Mensagem recebida: {mensagem}")

                    # Processa a mensagem recebida
                    # Se a mensagem for do tipo clock, atualiza o clock atual e processa as tarefas
                    if mensagem.startswith("clock:"):
                        self.clock_atual = int(mensagem.split(":")[1])
                        print(f"[Escalonador]: Clock atualizado para {self.clock_atual}")
                        self.processar_tarefas()

                    # Se a mensagem for do tipo emissor, adiciona a tarefa à lista de prontas
                    elif mensagem.startswith("emissor:"):
                        tarefa_info = mensagem.split(":")[1].split(";")
                        tarefa = Tarefa(
                            id=int(tarefa_info[0]),
                            tempo_ingresso=int(tarefa_info[1]),
                            duracao_prevista=int(tarefa_info[2]),
                            prioridade=int(tarefa_info[3])
                        )
                        self.tarefas_prontas.append(tarefa)
                        print(f"[Escalonador]: Tarefa recebida: {tarefa}")
                        self.processar_tarefas()

                    # Se a mensagem for de fim, encerra a simulação
                    elif mensagem == "fim":
                        self.rodando = False
                        print("[Escalonador]: Encerrando a simulação.")
                        self.finalizar_simulacao()

    def processar_tarefas(self):
        pass
        

def main():
    """
    Função principal para executar os componentes do sistema.
    Inicia o Clock, Emissor de Tarefas e Escalonador de Tarefas.
    Cada componente deve ser executado em uma thread separada.
    """
    # Verifica se o número correto de argumentos foi fornecido
    if len(sys.argv) != 3:
        print("Erro: Número incorreto de argumentos.")
        print("Uso: python escalona_tarefas.py <caminho_do_arquivo> <algoritmo>")
    
    caminho_arquivo = sys.argv[1]
    algoritmo = sys.argv[2]

    # Constrói os componentes
    clock = Clock()
    emissor = Emissor_de_tarefas(caminho_tarefas)
    escalonador = Escalonador(algoritmo)

    # Inicia o Clock
    clock_thread = threading.Thread(target=clock)
    clock_thread.start()

    # Inicia o Emissor de Tarefas
    emissor_thread = threading.Thread(target=emissor_tarefas, args=(caminho_arquivo,))
    emissor_thread.start()

    # Inicia o Escalonador de Tarefas
    escalonador_thread = threading.Thread(target=escalonador_tarefas, args=(algoritmo,))
    escalonador_thread.start()

    # Aguarda a conclusão das threads
    clock_thread.join()
    emissor_thread.join()
    escalonador_thread.join()

if __name__ == "__main__":
    main()