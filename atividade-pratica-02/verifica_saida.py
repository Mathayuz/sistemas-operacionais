def main():
    gabarito = "gabarito_n=8.txt"
    arquivo_saida = "arquivo.txt"

    print(
        f"Quantidade de caracteres incorretos: {calcula_qtd_incorretos(arquivo_saida, gabarito)}"
    )
    print(
        f"Quantidade de caracteres no gabarito: {calcula_qtd_caracteres_gabarito(gabarito)}"
    )
    print(
        f"Quantidade de caracteres na saída: {calcula_qtd_caracteres_saida(arquivo_saida)}"
    )


def calcula_qtd_incorretos(arquivo_saida, gabarito):
    with open(gabarito, "r") as g, open(arquivo_saida, "r") as a:
        buffer_gabarito = g.read(1)
        buffer_saida = a.read(1)
        quantidade_incorretos = 0
        caractere = 0
        while buffer_gabarito:
            if buffer_gabarito != buffer_saida:
                quantidade_incorretos += 1
            else:
                print(f"Caracteres iguais: {buffer_gabarito} na posição {caractere}")
            buffer_gabarito = g.read(1)
            buffer_saida = a.read(1)
            caractere += 1
    return quantidade_incorretos


def calcula_qtd_caracteres_gabarito(gabarito):
    with open(gabarito, "r") as g:
        buffer_gabarito = g.read(1)
        quantidade_caracteres = 0
        while buffer_gabarito:
            quantidade_caracteres += 1
            buffer_gabarito = g.read(1)
    return quantidade_caracteres


def calcula_qtd_caracteres_saida(arquivo_saida):
    with open(arquivo_saida, "r") as a:
        buffer_saida = a.read(1)
        quantidade_caracteres = 0
        while buffer_saida:
            quantidade_caracteres += 1
            buffer_saida = a.read(1)
    return quantidade_caracteres


main()
