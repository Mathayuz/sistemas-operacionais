import multiprocessing
import time
import random

# Configurações de tempo
CONFIGURACOES = {
    1: {"producao": (1, 2), "consumo": (1, 2)},
    2: {"producao": (3, 4), "consumo": (1, 2)},
    3: {"producao": (1, 2), "consumo": (3, 4)},
}

# Número de itens a serem produzidos
NUM_ITENS = 3


def produtor(conn, tempo_min, tempo_max):
    for i in range(1, NUM_ITENS + 1):
        inicio_producao = time.time()
        tempo_producao = random.uniform(tempo_min, tempo_max)
        time.sleep(tempo_producao)
        fim_producao = time.time()

        print(
            f"[Produtor] Produziu {i} | Inicio: {inicio_producao:.2f} | Fim: {fim_producao:.2f} | Duracao: {fim_producao - inicio_producao:.2f}s"
        )
        conn.send((i, fim_producao))  # Envia o produto e o tempo de envio

    fim_envio = time.time()
    print(f"[Produtor] Fim da producao | Tempo de envio do sinal: {fim_envio:.2f}")
    conn.send(("FIM", fim_envio))  # Envia sinal de fim da produção
    conn.close()


def consumidor(conn, tempo_min, tempo_max):
    while True:
        recebido, tempo_envio = conn.recv()
        if recebido == "FIM":
            tempo_recebimento_fim = time.time()
            print(
                f"[Consumidor] Recebeu FIM | Recebido em: {tempo_recebimento_fim:.2f} | Tempo desde envio: {tempo_recebimento_fim - tempo_envio:.2f}s"
            )
            break

        tempo_recebido = time.time()
        print(
            f"[Consumidor] Recebeu {recebido} | Enviado em: {tempo_envio:.2f} | Recebido em: {tempo_recebido:.2f} | Latencia: {tempo_recebido - tempo_envio:.2f}s"
        )

        tempo_consumo = random.uniform(tempo_min, tempo_max)
        time.sleep(tempo_consumo)
        fim_consumo = time.time()

        print(
            f"[Consumidor] Consumiu {recebido} | Fim: {fim_consumo:.2f} | Duracao: {fim_consumo - tempo_recebido:.2f}s"
        )
    conn.close()


def executar_configuracao(numero_config):
    print(f"\n=== Executando Configuracao {numero_config} ===")
    tempos = CONFIGURACOES[numero_config]
    tempo_inicio_total = time.time()

    conn_produtor, conn_consumidor = multiprocessing.Pipe()
    p_produtor = multiprocessing.Process(
        target=produtor, args=(conn_produtor, *tempos["producao"])
    )
    p_consumidor = multiprocessing.Process(
        target=consumidor, args=(conn_consumidor, *tempos["consumo"])
    )

    p_produtor.start()
    p_consumidor.start()

    p_produtor.join()
    p_consumidor.join()

    tempo_fim_total = time.time()
    print(
        f"=== Configuracao {numero_config} finalizada. Tempo total: {tempo_fim_total - tempo_inicio_total:.2f}s ===\n"
    )


if __name__ == "__main__":
    for i in range(1, 4):
        executar_configuracao(i)
