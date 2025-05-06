from multiprocessing import Process, Pipe
import time
import random

inicio = time.time()  # Marca o tempo de início


def produtor(conn):
    for i in range(1, 4):  # Produz 3 itens
        interv_ini = 1
        interv_fim = 2
        send_start = time.time()  # Marca o tempo de início do envio
        print(
            f"[{send_start - inicio:.4f} s] Produtor - iniciou a producao do produto {i}\n"
        )
        time.sleep(random.uniform(interv_ini, interv_fim))  # Simula tempo de produção
        send_end = time.time()
        print(
            f"[{send_end - inicio:.4f} s] Produtor - finalizou a producao do produto {i}. Enviando para o consumidor...\n"
        )
        conn.send(i)  # Envia o item produzido

    send_finalizacao = time.time()  # Marca o tempo de finalização
    print(
        f"[{send_finalizacao - inicio:.4f} s] Produtor - finalizou a producao de todos os itens. Enviando sinal de finalizacao...\n"
    )
    conn.send("fim")  # Envia sinal de fim de produção
    conn.close()  # Fecha a conexão do produtor


def consumidor(conn):
    while True:  # Loop infinito para receber itens
        produto = conn.recv()  # Recebe o item do produtor

        if produto == "fim":  # Verifica se o sinal de fim foi recebido
            recv_finalizacao = time.time()  # Marca o tempo de finalização
            print(
                f"[{recv_finalizacao - inicio:.4f} s] Consumidor - recebeu sinal de finalização. Finalizando...\n"
            )
            break  # Sai do loop
        else:
            recv_recepcao = time.time()  # Marca o tempo de recepção
            print(
                f"[{recv_recepcao - inicio:.4f} s] Consumidor - recebeu o produto {produto}. Processando...\n"
            )
            interv_ini = 3
            interv_fim = 4
            time.sleep(
                random.uniform(interv_ini, interv_fim)
            )  # Simula tempo de processamento
            recv_consumacao = time.time()  # Marca o tempo de início do recebimento
            print(
                f"[{recv_consumacao - inicio:.4f} s] Consumidor - consumiu o produto {produto}.\n"
            )


if __name__ == "__main__":
    prod_conn, cons_conn = Pipe()  # Cria um pipe para comunicação entre processos

    proc_prod = Process(target=produtor, args=(prod_conn,))  # Cria o processo produtor
    proc_cons = Process(
        target=consumidor, args=(cons_conn,)
    )  # Cria o processo consumidor

    proc_prod.start()  # Inicia o processo produtor
    proc_cons.start()  # Inicia o processo consumidor

    proc_prod.join()  # Espera o processo produtor terminar
    proc_cons.join()  # Espera o processo consumidor terminar
