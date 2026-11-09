"""Janela Tkinter. As regras de busca ficam nas classes, não nos botões."""

import re
import tkinter as tk
import tkinter.font as tkfont
import webbrowser
from tkinter import messagebox, simpledialog, ttk
from tkinter.scrolledtext import ScrolledText


# Nomes exibidos ao cidadão e seus destinos. Não tentamos adivinhar URLs.
LINKS_SERVICOS = {
    "Meu SUS Digital": "https://meususdigital.saude.gov.br",
    "Meu INSS": "https://meu.inss.gov.br",
    "Carteira da Pessoa Idosa": "https://carteiraidoso.cidadania.gov.br",
    "Carteira Digital de Trânsito": "https://www.gov.br/pt-br/servicos/emitir-credencial-de-estacionamento-digital",
    "Portal de Serviços Senatran": "https://portalservicos.senatran.serpro.gov.br",
    "Receita Federal": "https://www.gov.br/receitafederal",
    "Cadastro Único": "https://www.gov.br/mds/pt-br/acoes-e-programas/cadastro-unico/Cadastro-unico/",
    "Carteira de Identidade Nacional": "https://www.gov.br/governodigital/pt-br/identidade/cin/duvidas-frequentes-sobre-a-cin-campanha",
    "gov.br": "https://www.gov.br/pt-br",
}


def identificar_links(texto):
    """Devolve (início, fim, destino) para URLs e nomes conhecidos, sem sobreposição."""
    links = []
    for resultado in re.finditer(r"https?://[^\s<>\"']+", texto):
        url = resultado.group().rstrip(".,;:!?)]}")
        links.append((resultado.start(), resultado.start() + len(url), url))
    for nome in sorted(LINKS_SERVICOS, key=len, reverse=True):
        # Também reconhece um nome dividido por quebra de linha no texto.
        padrao = r"(?<!\w)" + r"\s+".join(re.escape(p) for p in nome.split()) + r"(?!\w)"
        for resultado in re.finditer(padrao, texto, flags=re.IGNORECASE):
            inicio, fim = resultado.span()
            if not any(inicio < outro_fim and fim > outro_inicio for outro_inicio, outro_fim, _ in links):
                links.append((inicio, fim, LINKS_SERVICOS[nome]))
    return sorted(links)


class Interface:
    def __init__(self, janela, assistente):
        self.janela = janela
        self.assistente = assistente
        self.resultados = []
        self.atual = None
        self.links = {}
        janela.title(f"{assistente.nome} | Orientação ao cidadão")
        largura = min(1120, janela.winfo_screenwidth() - 60)
        altura = min(760, janela.winfo_screenheight() - 80)
        janela.geometry(f"{largura}x{altura}")
        janela.minsize(min(880, largura), min(600, altura))
        janela.configure(background="#f3f6f8")
        janela.columnconfigure(0, weight=1)
        janela.rowconfigure(0, weight=1)

        for nome in ("TkDefaultFont", "TkTextFont", "TkMenuFont"):
            tkfont.nametofont(nome).configure(size=13)
        estilo = ttk.Style(janela)
        estilo.theme_use("clam")
        estilo.configure("TFrame", background="#f3f6f8")
        estilo.configure("TLabel", background="#f3f6f8", foreground="#172b3a")
        estilo.configure("Titulo.TLabel", font=("sans-serif", 23, "bold"))
        estilo.configure("TButton", padding=(12, 9))
        estilo.configure("Principal.TButton", background="#12665c", foreground="white")
        estilo.map("Principal.TButton", background=[("active", "#0b5048")])
        estilo.configure("TCombobox", padding=6)

        painel = ttk.Frame(janela, padding=18)
        painel.grid(row=0, column=0, sticky="nsew")
        painel.columnconfigure(0, weight=1)
        painel.rowconfigure(4, weight=1)
        ttk.Label(painel, text="Como podemos ajudar?", style="Titulo.TLabel").grid(
            row=0, column=0, sticky="w")
        ttk.Label(painel, text="Orientações sobre serviços públicos em todo o Brasil.").grid(
            row=1, column=0, sticky="w", pady=(4, 12))
        aviso = ttk.Label(
            painel, text="Este assistente não é canal oficial. Não informe nome, CPF, telefone, e-mail ou senha.",
            wraplength=900)
        aviso.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        painel.bind("<Configure>", lambda evento: aviso.configure(wraplength=max(200, evento.width - 36)))

        busca = ttk.Frame(painel)
        busca.grid(row=3, column=0, sticky="ew", pady=(0, 16))
        busca.columnconfigure(0, weight=1)
        ttk.Label(busca, text="Escreva sua dúvida, por exemplo: Como consultar minhas vacinas?").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))
        self.pergunta = tk.StringVar()
        self.entrada = ttk.Entry(busca, textvariable=self.pergunta, font=("sans-serif", 14))
        self.entrada.grid(row=1, column=0, sticky="ew", ipady=7)
        self.entrada.bind("<Return>", self.buscar)
        ttk.Button(busca, text="Buscar", style="Principal.TButton", command=self.buscar).grid(
            row=1, column=1, padx=(10, 0))

        conteudo = ttk.Panedwindow(painel, orient=tk.HORIZONTAL)
        conteudo.grid(row=4, column=0, sticky="nsew")
        esquerda = ttk.Frame(conteudo, padding=(0, 0, 14, 0))
        direita = ttk.Frame(conteudo, padding=(14, 0, 0, 0))
        conteudo.add(esquerda, weight=1)
        conteudo.add(direita, weight=3)
        esquerda.columnconfigure(0, weight=1)
        esquerda.rowconfigure(4, weight=1)
        direita.columnconfigure(0, weight=1)
        direita.rowconfigure(1, weight=1)

        ttk.Label(esquerda, text="Ou escolha uma categoria").grid(row=0, column=0, sticky="w")
        self.categoria = tk.StringVar(value="Todas as categorias")
        self.seletor = ttk.Combobox(esquerda, textvariable=self.categoria, state="readonly", width=27)
        self.seletor.grid(row=1, column=0, sticky="ew", pady=(6, 8))
        self.seletor.bind("<<ComboboxSelected>>", self.navegar)
        ttk.Button(esquerda, text="Ver orientações", command=self.navegar).grid(
            row=2, column=0, sticky="ew", pady=(0, 12))
        self.resumo = tk.StringVar(value="")
        ttk.Label(esquerda, textvariable=self.resumo).grid(row=3, column=0, sticky="w", pady=(0, 6))

        lista_painel = ttk.Frame(esquerda)
        lista_painel.grid(row=4, column=0, sticky="nsew")
        lista_painel.rowconfigure(0, weight=1)
        lista_painel.columnconfigure(0, weight=1)
        self.lista = tk.Listbox(lista_painel, font=("sans-serif", 13), width=28, height=8,
                               background="white", foreground="#172b3a", selectbackground="#12665c",
                               selectforeground="white", exportselection=False, activestyle="dotbox")
        self.lista.grid(row=0, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(lista_painel, orient="vertical", command=self.lista.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(lista_painel, orient="horizontal", command=self.lista.xview)
        horizontal.grid(row=1, column=0, sticky="ew")
        self.lista.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.lista.bind("<<ListboxSelect>>", self.abrir_selecao)
        self.lista.bind("<Return>", self.abrir_selecao)

        self.contexto = tk.StringVar(value="Selecione uma orientação")
        rotulo_contexto = ttk.Label(direita, textvariable=self.contexto, wraplength=400)
        rotulo_contexto.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        direita.bind("<Configure>", lambda evento: rotulo_contexto.configure(wraplength=max(100, evento.width - 14)))
        self.resposta = ScrolledText(direita, wrap="word", font=("sans-serif", 14), width=45,
                                    height=12, padx=14, pady=14, background="white", foreground="#172b3a")
        self.resposta.grid(row=1, column=0, sticky="nsew")
        self.resposta.tag_configure("hyperlink", foreground="#0055aa", underline=True)
        self.resposta.tag_bind("hyperlink", "<Enter>",
                               lambda evento: self.resposta.configure(cursor="hand2"))
        self.resposta.tag_bind("hyperlink", "<Leave>",
                               lambda evento: self.resposta.configure(cursor="xterm"))
        self.resposta.tag_bind("hyperlink", "<Button-1>", self.abrir_link_no_texto)
        self.fonte = ttk.Button(direita, text="Abrir fonte oficial", command=self.abrir_fonte, state="disabled")
        self.fonte.grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.avaliacao = ttk.Frame(direita)
        self.avaliacao.grid(row=3, column=0, sticky="w", pady=(8, 0))
        ttk.Label(self.avaliacao, text="Essa orientação ajudou?").grid(row=0, column=0, sticky="w")
        ttk.Button(self.avaliacao, text="Sim", command=lambda: self.avaliar(True)).grid(row=1, column=0, sticky="w")
        ttk.Button(self.avaliacao, text="Não", command=lambda: self.avaliar(False)).grid(row=1, column=1, padx=6)
        ttk.Button(self.avaliacao, text="Pular", command=lambda: self.avaliar(None)).grid(row=1, column=2)
        self.sem_resposta = ttk.Button(direita, text="Encerrar sem resposta", command=lambda: self.avaliar(False))
        self.sem_resposta.grid(row=3, column=0, sticky="w", pady=(8, 0))

        rodape = ttk.Frame(painel)
        rodape.grid(row=5, column=0, sticky="ew", pady=(16, 0))
        rodape.columnconfigure(1, weight=1)
        ttk.Button(rodape, text="Voltar ao início", command=self.inicio).grid(row=0, column=0, sticky="w")
        ttk.Button(rodape, text="Indicadores", command=self.mostrar_indicadores).grid(row=0, column=2, padx=4)
        ttk.Button(rodape, text="Exportar CSV", command=self.exportar_csv).grid(row=0, column=3, padx=4)
        ttk.Button(rodape, text="Recarregar base", command=self.recarregar).grid(row=0, column=4, padx=4)
        ttk.Button(rodape, text="Sair", command=self.sair).grid(row=0, column=5)
        janela.protocol("WM_DELETE_WINDOW", self.sair)
        janela.bind("<Escape>", lambda evento: self.inicio())
        self.inicio()

    def escrever(self, texto):
        self.resposta.configure(state="normal")
        self.resposta.configure(cursor="xterm")
        for tag in self.links:
            self.resposta.tag_delete(tag)
        self.links.clear()
        self.resposta.delete("1.0", tk.END)
        self.resposta.insert("1.0", texto)
        for numero, (inicio_texto, fim_texto, url) in enumerate(identificar_links(texto)):
            inicio = f"1.0 + {inicio_texto} chars"
            fim = f"1.0 + {fim_texto} chars"
            tag = f"url_{numero}"
            self.links[tag] = url
            self.resposta.tag_add("hyperlink", inicio, fim)
            self.resposta.tag_add(tag, inicio, fim)
        self.resposta.configure(state="disabled")
        self.resposta.yview_moveto(0)

    def abrir_link_no_texto(self, evento):
        posicao = self.resposta.index(f"@{evento.x},{evento.y}")
        for tag in self.resposta.tag_names(posicao):
            if tag in self.links:
                self.abrir_site(self.links[tag])
                return "break"

    def listar(self, resultados):
        self.resultados = resultados
        self.lista.delete(0, tk.END)
        self.atual = None
        self.fonte.configure(state="disabled")
        self.avaliacao.grid_remove()
        self.sem_resposta.grid_remove()
        for _, orientacao in resultados:
            self.lista.insert(tk.END, orientacao.titulo)
        self.resumo.set(f"{len(resultados)} orientações disponíveis")

    def inicio(self):
        if not self.finalizar():
            return
        self.pergunta.set("")
        self.categoria.set("Todas as categorias")
        self.seletor.configure(values=["Todas as categorias"] + self.assistente.base.categorias())
        self.listar([(None, item) for item in self.assistente.base.orientacoes])
        self.contexto.set("Comece pela busca ou pelas categorias")
        self.escrever(self.assistente.base.erro or self.assistente.erro_historico or (
            "1. Escreva uma dúvida e clique em Buscar.\n\n"
            "2. Ou escolha uma categoria e selecione uma orientação na lista.\n\n"
            "Aqui você verá os passos, os documentos, o canal de atendimento, "
            "a fonte e a data de verificação.\n\n"
            "A busca utiliza palavras-chave da base. Este assistente não é canal oficial."
        ))
        self.entrada.focus_set()

    def buscar(self, evento=None):
        try:
            resultados = self.assistente.perguntar(self.pergunta.get())
        except ValueError as erro:
            self.contexto.set(str(erro))
            self.pergunta.set("")
            self.entrada.focus_set()
            return
        except OSError as erro:
            self.contexto.set(str(erro))
            return
        self.categoria.set("Todas as categorias")
        self.listar(resultados)
        if not resultados:
            self.contexto.set("Não encontrei uma orientação")
            self.escrever("Tente outras palavras ou escolha uma categoria.\n\n"
                          "Este assistente não é canal oficial.")
            self.sem_resposta.grid()
            return
        self.resumo.set("Melhor resultado e alternativas")
        self.lista.selection_set(0)
        self.abrir_selecao()

    def navegar(self, evento=None):
        if not self.finalizar():
            return
        categoria = self.categoria.get()
        itens = (self.assistente.base.orientacoes if categoria == "Todas as categorias"
                 else self.assistente.navegar(categoria))
        self.listar([(None, item) for item in itens])
        self.contexto.set("Selecione uma orientação na lista")
        self.escrever(self.assistente.base.erro or
                      "Clique no assunto desejado para ler a orientação.\n\n"
                      "Este assistente não é canal oficial.")

    def abrir_selecao(self, evento=None):
        selecao = self.lista.curselection()
        if not selecao or selecao[0] >= len(self.resultados):
            return
        pontos, orientacao = self.resultados[selecao[0]]
        if self.atual is orientacao:
            return
        origem = "categoria" if pontos is None else "pergunta"
        try:
            self.assistente.selecionar_orientacao(orientacao, origem)
        except OSError as erro:
            self.contexto.set(str(erro))
            self.lista.selection_clear(0, tk.END)
            return
        self.atual = orientacao
        if pontos is None:
            self.contexto.set("Navegação por categoria")
        else:
            self.contexto.set(f"Confiança da busca: {self.assistente.confianca(pontos)} ({pontos} pontos)")
        self.escrever(self.atual.exibir())
        self.fonte.configure(state="normal")
        if self.assistente.pendente:
            self.avaliacao.grid()

    def finalizar(self, ajudou=None):
        try:
            self.assistente.registrar(ajudou)
        except OSError as erro:
            self.contexto.set(str(erro))
            return False
        return True

    def avaliar(self, ajudou):
        if self.finalizar(ajudou):
            self.avaliacao.grid_remove()
            self.sem_resposta.grid_remove()
            self.contexto.set("Atendimento registrado. Você já pode fazer outra consulta.")

    def sair(self):
        if not self.finalizar() and not messagebox.askyesno(
            "Atendimento pendente", "A gravação falhou. Deseja sair sem salvar o atendimento atual?", parent=self.janela
        ):
            return
        nota = simpledialog.askinteger(
            "Facilidade de uso", "Como foi usar o assistente?\n1 = muito difícil · 5 = muito fácil\nCancelar para pular.",
            parent=self.janela, minvalue=1, maxvalue=5,
        )
        if nota is not None:
            try:
                self.assistente.registrar_facilidade(nota)
            except OSError as erro:
                messagebox.showerror("Erro ao salvar nota", str(erro), parent=self.janela)
                return
        self.janela.destroy()

    def mostrar_indicadores(self):
        try:
            resumo = self.assistente.resumo_indicadores()
        except OSError as erro:
            messagebox.showerror("Erro ao consultar indicadores", str(erro), parent=self.janela)
            return
        janela = tk.Toplevel(self.janela)
        janela.title("Indicadores dos atendimentos")
        janela.transient(self.janela)
        texto = ScrolledText(janela, wrap="word", font=("sans-serif", 13), width=60, height=18, padx=12, pady=12)
        texto.pack(fill="both", expand=True, padx=12, pady=(12, 0))
        texto.insert("1.0", resumo)
        texto.configure(state="disabled")
        ttk.Button(janela, text="Fechar", command=janela.destroy).pack(pady=12)
        janela.bind("<Escape>", lambda evento: janela.destroy())

    def exportar_csv(self):
        try:
            caminho = self.assistente.exportar_csv()
        except OSError as erro:
            messagebox.showerror("Erro ao exportar CSV", str(erro), parent=self.janela)
            return
        messagebox.showinfo("CSV exportado", f"Arquivo salvo em:\n{caminho}", parent=self.janela)

    def abrir_fonte(self):
        if self.atual:
            self.abrir_site(self.atual.fonte)

    def abrir_site(self, url):
        try:
            abriu = webbrowser.open(url, new=2)
        except (webbrowser.Error, OSError):
            abriu = False
        if not abriu:
            self.contexto.set("Copie o endereço do site para seu navegador.")

    def recarregar(self):
        if not self.finalizar():
            return
        ok = self.assistente.base.carregar()
        self.inicio()
        if ok:
            self.contexto.set("Base recarregada. Você já pode fazer uma nova busca.")
