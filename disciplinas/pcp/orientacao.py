"""Representa uma orientação verificada da base JSON."""


class Orientacao:
    def __init__(self, dados):
        self.id = dados["id"]
        self.categoria = dados["categoria"]
        self.titulo = dados["titulo"]
        self.palavras_chave = dados["palavras_chave"]
        self.resposta = dados["resposta"]
        self.documentos = dados["documentos"]
        self.onde = dados["onde"]
        self.fonte = dados["fonte"]
        self.verificado_em = dados["verificado_em"]

    def exibir(self):
        """Devolve o mesmo texto para a janela gráfica e para o terminal."""
        documentos = "\n".join(f"- {item}" for item in self.documentos)
        return (
            f"{self.titulo}\nCategoria: {self.categoria}\n\n"
            f"{self.resposta}\n\nDOCUMENTOS\n{documentos}\n\n"
            f"ONDE BUSCAR ATENDIMENTO\n{self.onde}\n\n"
            f"FONTE OFICIAL\n{self.fonte}\n"
            f"Verificado em: {self.verificado_em}\n\n"
            "Aviso: este assistente não é canal oficial."
        )
