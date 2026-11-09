"""Execute python main.py para Tkinter, ou acrescente --terminal."""

import argparse
from pathlib import Path

from assistente import Assistente
from base_conhecimento import BaseConhecimento


def escolher(rotulo, quantidade):
    while True:
        entrada = input(rotulo).strip()
        if entrada.isdecimal():
            try:
                numero = int(entrada)
            except ValueError:
                numero = -1
            if 0 <= numero <= quantidade:
                return numero
        print(f"Digite um número de 0 a {quantidade}.")


def mostrar_resultados(assistente, resultados):
    if not resultados:
        print("Não encontrei uma orientação. Tente outras palavras ou consulte as categorias.")
        print("Aviso: este assistente não é canal oficial.")
        return
    pontos, orientacao = resultados[0]
    print(f"\nConfiança da busca: {assistente.confianca(pontos)} ({pontos} pontos)")
    print(orientacao.exibir())
    if len(resultados) > 1:
        print("\nOutras orientações encontradas:")
        for numero, (pontos, item) in enumerate(resultados[1:], 1):
            print(f"{numero}. {item.titulo} ({pontos} pontos)")
        while True:
            numero = escolher("Abrir alternativa (0 para voltar): ", len(resultados) - 1)
            if numero == 0:
                break
            pontos, item = resultados[numero]
            assistente.selecionar_orientacao(item, "pergunta")
            print(f"\nConfiança da busca: {assistente.confianca(pontos)} ({pontos} pontos)")
            print(item.exibir())


def avaliar_terminal(assistente):
    respostas = {"s": True, "n": False, "1": True, "2": False, "0": None}
    while True:
        resposta = input("\nEssa orientação ajudou? (s/n, 0 para pular): ").strip().lower()
        if resposta in respostas:
            finalizar_terminal(assistente, respostas[resposta])
            return
        print("Digite s para sim, n para não ou 0 para pular.")


def finalizar_terminal(assistente, ajudou=None):
    try:
        if assistente.registrar(ajudou):
            print("Atendimento registrado.")
        return True
    except OSError as erro:
        print(erro)
        return False


def executar_terminal(assistente):
    print(f"\n{assistente.nome} — consultas\nEste assistente não é canal oficial.")
    print("Não digite nome, CPF, telefone, e-mail ou senha.")
    if assistente.base.erro:
        print(assistente.base.erro)
    if assistente.erro_historico:
        print(assistente.erro_historico)
    while True:
        print("\n1. Fazer uma pergunta\n2. Navegar por categorias\n3. Recarregar base"
              "\n4. Ver indicadores\n5. Exportar CSV\n0. Sair")
        opcao = escolher("Escolha: ", 5)
        if opcao == 0:
            finalizar_terminal(assistente)
            nota = escolher("Facilidade de uso (1 = muito difícil, 5 = muito fácil, 0 = pular): ", 5)
            if nota:
                try:
                    assistente.registrar_facilidade(nota)
                    print("Nota de facilidade registrada.")
                except OSError as erro:
                    print(erro)
            return
        if opcao == 1:
            while True:
                pergunta = input("\nDigite sua dúvida (0 para voltar): ")
                if pergunta.strip() == "0":
                    if finalizar_terminal(assistente):
                        break
                    continue
                try:
                    resultados = assistente.perguntar(pergunta)
                    mostrar_resultados(assistente, resultados)
                    if resultados:
                        avaliar_terminal(assistente)
                except (ValueError, OSError) as erro:
                    print(erro)
        elif opcao == 2:
            categorias = assistente.base.categorias()
            if not categorias:
                print(assistente.base.erro or "Nenhuma categoria disponível.")
                continue
            while True:
                for numero, categoria in enumerate(categorias, 1):
                    print(f"{numero}. {categoria}")
                numero = escolher("Categoria (0 para voltar): ", len(categorias))
                if numero == 0:
                    break
                itens = assistente.navegar(categorias[numero - 1])
                while True:
                    for indice, item in enumerate(itens, 1):
                        print(f"{indice}. {item.titulo}")
                    indice = escolher("Orientação (0 para voltar): ", len(itens))
                    if indice == 0:
                        break
                    item = itens[indice - 1]
                    try:
                        assistente.selecionar_orientacao(item, "categoria")
                    except OSError as erro:
                        print(erro)
                        continue
                    print("\n" + item.exibir())
                    avaliar_terminal(assistente)
        elif opcao == 3:
            ok = assistente.base.carregar()
            print("Base recarregada." if ok else assistente.base.erro)
        elif opcao in (4, 5):
            try:
                if opcao == 4:
                    print("\n" + assistente.resumo_indicadores())
                else:
                    print(f"CSV exportado em {assistente.exportar_csv()}")
            except OSError as erro:
                print(erro)


def main():
    parser = argparse.ArgumentParser(description="Assistente acadêmico de orientação ao cidadão.")
    parser.add_argument("--terminal", action="store_true", help="Abre a interface de terminal.")
    argumentos = parser.parse_args()
    caminho = Path(__file__).resolve().parent / "data" / "base_conhecimento.json"
    base = BaseConhecimento(caminho)
    base.carregar()
    assistente = Assistente("Citizen Assist AI", base, caminho.with_name("historico.json"))
    if not argumentos.terminal:
        try:
            import tkinter as tk
            from interface import Interface
        except ImportError:
            print("Tkinter indisponível. O assistente será aberto no terminal.")
        else:
            try:
                janela = tk.Tk()
            except tk.TclError:
                print("Sessão gráfica indisponível. O assistente será aberto no terminal.")
            else:
                Interface(janela, assistente)
                janela.mainloop()
                return 0
    try:
        executar_terminal(assistente)
    except (EOFError, KeyboardInterrupt):
        finalizar_terminal(assistente)
        print("\nPrograma encerrado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
