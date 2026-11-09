"""Regras de atendimento e histórico compartilhados pelas duas interfaces."""

import csv
import json
import time
from datetime import datetime
from pathlib import Path
from statistics import mean


CAMPOS_CSV = (
    "data", "origem", "pergunta", "id_orientacao", "encontrou", "ajudou",
    "tentativas", "tempo_segundos", "tempo_encontro_segundos",
)


class Assistente:
    def __init__(self, nome, base, caminho_historico=None):
        self.nome = nome
        self.base = base
        self.caminho_historico = Path(caminho_historico) if caminho_historico else None
        self.pasta_dados = self.caminho_historico.parent if self.caminho_historico else Path(base.caminho).parent
        self.avaliacoes = []
        self.historico = []
        self.pendente = None
        self.inicio_atendimento = None
        self.erro_historico = ""
        try:
            self.historico = self._ler_historico()
        except OSError as erro:
            self.erro_historico = str(erro)

    def _ler_historico(self):
        if self.caminho_historico is None:
            return self.historico
        try:
            registros = json.loads(self.caminho_historico.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return []
        except (ValueError, OSError):
            raise OSError("Não foi possível ler data/historico.json. Confira o arquivo e tente novamente.") from None
        if not isinstance(registros, list) or any(not isinstance(item, dict) for item in registros):
            raise OSError("data/historico.json deve conter uma lista de atendimentos.")
        return registros

    def perguntar(self, pergunta):
        # Perguntas recusadas não entram no atendimento nem no histórico.
        if "@" in pergunta or sum(letra.isdigit() for letra in pergunta) >= 8:
            raise ValueError("Não informe CPF, telefone ou e-mail. Reescreva sem dados pessoais.")
        if not pergunta.strip() or not any(letra.isalnum() for letra in pergunta):
            raise ValueError("Escreva uma dúvida antes de buscar.")
        if len(pergunta) > 1000:
            raise ValueError("Escreva uma pergunta com até 1.000 caracteres.")
        if not self.base.orientacoes:
            raise ValueError(self.base.erro or "A base está vazia. Recarregue a base.")
        inicio = time.time()
        resultados = [(pontos, item) for pontos, item in self.base.buscar(pergunta) if pontos >= 3][:3]
        if self.pendente and (self.pendente["origem"] != "pergunta" or self.pendente["encontrou"]):
            self.registrar()
        id_orientacao = resultados[0][1].id if resultados else None
        self._tentativa("pergunta", pergunta.strip(), id_orientacao, inicio)
        return resultados

    def _tentativa(self, origem, pergunta, id_orientacao, inicio):
        if self.pendente is None:
            self.inicio_atendimento = inicio
            self.pendente = {
                "data": datetime.now().astimezone().isoformat(timespec="seconds"),
                "origem": origem,
                "tentativas": 0,
            }
        self.pendente.update(pergunta=pergunta, id_orientacao=id_orientacao,
                             encontrou=id_orientacao is not None)
        self.pendente.pop("ajudou", None)
        self.pendente["tentativas"] += 1
        if id_orientacao is not None and "tempo_encontro_segundos" not in self.pendente:
            self.pendente["tempo_encontro_segundos"] = round(max(0, time.time() - self.inicio_atendimento), 1)

    def selecionar_orientacao(self, orientacao, origem):
        if origem == "pergunta":
            if self.pendente and self.pendente["id_orientacao"] != orientacao.id:
                self._tentativa(origem, self.pendente["pergunta"], orientacao.id, time.time())
            return
        if self.pendente:
            if self.pendente["origem"] == "categoria" and self.pendente["id_orientacao"] == orientacao.id:
                return
            self.registrar()
        self._tentativa("categoria", "", orientacao.id, time.time())

    def registrar(self, ajudou=None):
        """Finaliza o atendimento e preserva a avaliação pendente se a gravação falhar."""
        if self.pendente is None:
            return False
        if not self.pendente["encontrou"]:
            ajudou = False
        if ajudou is not None or "ajudou" not in self.pendente:
            self.pendente["ajudou"] = ajudou
        registro = dict(self.pendente,
                        tempo_segundos=round(max(0, time.time() - self.inicio_atendimento), 1))
        historico = self._ler_historico() + [registro]
        if self.caminho_historico is not None:
            self._salvar_json(self.caminho_historico, historico)
        self.historico = historico
        self.erro_historico = ""
        self.pendente = None
        self.inicio_atendimento = None
        return True

    @staticmethod
    def _salvar_json(caminho, dados):
        temporario = caminho.with_suffix(".tmp")
        try:
            temporario.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            temporario.replace(caminho)
        except OSError:
            raise OSError(f"Não foi possível salvar {caminho.name}. Confira a pasta e tente novamente.") from None

    def _ler_avaliacoes(self):
        if self.caminho_historico is None:
            return self.avaliacoes
        caminho = self.pasta_dados / "avaliacoes.json"
        try:
            notas = json.loads(caminho.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return []
        except (OSError, ValueError):
            raise OSError("Não foi possível ler data/avaliacoes.json. Confira o arquivo.") from None
        if not isinstance(notas, list) or any(type(nota) is not int or not 1 <= nota <= 5 for nota in notas):
            raise OSError("data/avaliacoes.json deve conter apenas notas inteiras de 1 a 5.")
        return notas

    def registrar_facilidade(self, nota):
        if type(nota) is not int or not 1 <= nota <= 5:
            raise ValueError("A nota de facilidade deve ser um número inteiro de 1 a 5.")
        notas = self._ler_avaliacoes() + [nota]
        if self.caminho_historico is not None:
            self._salvar_json(self.pasta_dados / "avaliacoes.json", notas)
        self.avaliacoes = notas

    def indicadores(self):
        registros = self._ler_historico()
        notas = self._ler_avaliacoes()
        encontrados = [r for r in registros if r.get("encontrou") is True]
        avaliados = [r for r in registros if type(r.get("ajudou")) is bool]
        tempos = [r["tempo_encontro_segundos"] for r in encontrados
                  if type(r.get("tempo_encontro_segundos")) in (int, float)]
        tentativas = [r["tentativas"] for r in registros if type(r.get("tentativas")) is int]
        titulos = {item.id: item.titulo for item in self.base.orientacoes}
        sem_solucao = []
        for registro in registros:
            if registro.get("encontrou") is False or registro.get("ajudou") is False:
                identificador = registro.get("id_orientacao")
                pergunta = registro.get("pergunta")
                assunto = pergunta if isinstance(pergunta, str) and pergunta.strip() else titulos.get(
                    identificador if type(identificador) is int else None, "Orientação sem título"
                )
                if assunto not in sem_solucao:
                    sem_solucao.append(assunto)
        return {
            "total": len(registros),
            "avaliados": len(avaliados),
            "notas": len(notas),
            "tempos_medidos": len(tempos),
            "encontrada_pct": 100 * len(encontrados) / len(registros) if registros else None,
            "ajudou_pct": 100 * sum(r["ajudou"] for r in avaliados) / len(avaliados) if avaliados else None,
            "tempo_medio": mean(tempos) if tempos else None,
            "tentativas_media": mean(tentativas) if tentativas else None,
            "facilidade_media": mean(notas) if notas else None,
            "sem_solucao": sem_solucao,
        }

    def resumo_indicadores(self):
        dados = self.indicadores()

        def valor(chave, unidade=""):
            numero = dados[chave]
            return f"{numero:.1f}{unidade}" if numero is not None else "Sem dados"

        linhas = [
            f"Atendimentos concluídos: {dados['total']}",
            f"Resposta encontrada: {valor('encontrada_pct', '%')}",
            f"Taxa de acerto (ajudou): {valor('ajudou_pct', '%')} ({dados['avaliados']} com resultado de ajuda)",
            f"Tempo médio para encontrar: {valor('tempo_medio', ' s')} ({dados['tempos_medidos']} medições)",
            f"Tentativas por atendimento: {valor('tentativas_media')}",
            f"Facilidade de uso (1 a 5): {valor('facilidade_media')} ({dados['notas']} notas)",
            "",
            "Dúvidas sem solução",
        ]
        linhas.extend(f"- {item}" for item in dados["sem_solucao"] or ["Nenhuma registrada."])
        return "\n".join(linhas)

    def exportar_csv(self):
        registros = self._ler_historico()
        caminho = self.pasta_dados / "atendimentos.csv"
        temporario = caminho.with_suffix(".csv.tmp")
        try:
            with temporario.open("w", encoding="utf-8-sig", newline="") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV)
                escritor.writeheader()
                for registro in registros:
                    linha = {campo: registro.get(campo) for campo in CAMPOS_CSV}
                    # Planilhas podem interpretar uma pergunta que começa com '=' como fórmula.
                    pergunta = linha["pergunta"]
                    if isinstance(pergunta, str) and pergunta.lstrip().startswith(("=", "+", "-", "@")):
                        linha["pergunta"] = "'" + pergunta
                    escritor.writerow(linha)
            temporario.replace(caminho)
        except OSError:
            raise OSError("Não foi possível exportar data/atendimentos.csv. Confira a pasta e tente novamente.") from None
        return caminho

    def navegar(self, categoria):
        return self.base.por_categoria(categoria)

    @staticmethod
    def confianca(pontos):
        if pontos >= 6:
            return "ALTA"
        if pontos >= 3:
            return "MÉDIA"
        return "NÃO ENCONTRADA"
