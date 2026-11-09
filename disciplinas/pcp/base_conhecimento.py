"""Leitura da base e busca por pontuação, sem API de IA."""

import json
import unicodedata
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from orientacao import Orientacao


def normalizar(texto):
    """Remove acentos e pontuação e delimita palavras com espaços."""
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(letra for letra in texto if not unicodedata.combining(letra))
    texto = "".join(letra if letra.isalnum() else " " for letra in texto)
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = Path(caminho)
        self.orientacoes = []
        self.erro = ""

    def carregar(self):
        """Retorna False e uma mensagem legível se o arquivo estiver inválido."""
        self.orientacoes = []
        self.erro = ""
        try:
            with self.caminho.open(encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if not isinstance(dados, list) or not dados:
                raise ValueError("A base deve ser uma lista com orientações.")
            ids = set()
            novas = []
            for registro in dados:
                self._validar_registro(registro)
                if registro["id"] in ids:
                    raise ValueError("A base contém IDs repetidos.")
                ids.add(registro["id"])
                novas.append(Orientacao(registro))
            self.orientacoes = novas
            return True
        except FileNotFoundError:
            self.erro = "Base não encontrada. Coloque base_conhecimento.json na pasta data."
        except (json.JSONDecodeError, UnicodeError):
            self.erro = "O arquivo da base está corrompido ou não é um JSON UTF-8 válido."
        except OSError:
            self.erro = "Não foi possível ler a base. Confira as permissões do arquivo."
        except ValueError as erro:
            self.erro = str(erro)
        return False

    @staticmethod
    def _validar_registro(registro):
        if not isinstance(registro, dict):
            raise ValueError("Cada orientação deve ser um dicionário.")
        if type(registro.get("id")) is not int or registro["id"] <= 0:
            raise ValueError("Cada orientação precisa de um ID inteiro positivo.")
        for campo in ("categoria", "titulo", "resposta", "onde", "fonte", "verificado_em"):
            if not isinstance(registro.get(campo), str) or not registro[campo].strip():
                raise ValueError(f"Campo obrigatório ausente ou inválido: {campo}.")
        for campo in ("palavras_chave", "documentos"):
            itens = registro.get(campo)
            if not isinstance(itens, list) or not itens:
                raise ValueError(f"O campo {campo} deve ser uma lista não vazia.")
            if any(not isinstance(item, str) or not item.strip() for item in itens):
                raise ValueError(f"O campo {campo} contém um item inválido.")
        palavras = [normalizar(item) for item in registro["palavras_chave"]]
        if len(set(palavras)) < 3 or any(not palavra.strip() for palavra in palavras):
            raise ValueError("Cada orientação precisa de pelo menos três palavras-chave distintas.")
        try:
            date.fromisoformat(registro["verificado_em"])
        except ValueError:
            raise ValueError("A data de verificação deve estar no formato AAAA-MM-DD.") from None
        fonte = urlsplit(registro["fonte"])
        dominio = fonte.hostname or ""
        if fonte.scheme != "https" or not (dominio == "gov.br" or dominio.endswith(".gov.br")):
            raise ValueError("Esta base utiliza fontes HTTPS do domínio gov.br.")

    def categorias(self):
        return sorted({item.categoria for item in self.orientacoes})

    def por_categoria(self, categoria):
        return [item for item in self.orientacoes if item.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        pergunta_normalizada = normalizar(pergunta)
        titulo = normalizar(orientacao.titulo)
        # Cada palavra-chave distinta conta uma vez, mesmo que seja repetida na pergunta.
        pontos = sum(
            3 for palavra in {normalizar(p) for p in orientacao.palavras_chave}
            if palavra in pergunta_normalizada
        )
        for palavra in set(pergunta_normalizada.split()):
            if len(palavra) >= 4 and f" {palavra} " in titulo:
                pontos += 1
        return pontos

    def buscar(self, pergunta):
        resultados = [(self.pontuar(pergunta, item), item) for item in self.orientacoes]
        # Em empate, o menor ID aparece primeiro, mantendo o resultado previsível.
        return sorted(resultados, key=lambda resultado: (-resultado[0], resultado[1].id))
