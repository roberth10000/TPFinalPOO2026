from datetime import date, time
from evento import Evento


class Avaliacao(Evento):
    TIPO = "avaliacao"

    def __init__(self, titulo: str, data: date, horario: time | None, disciplina,
                 conteudos: list[str] | None = None, dificuldade: int = 3,
                 valor: float = 0.0, descricao: str = ""):
        super().__init__(titulo, data, horario, disciplina, descricao)
        self._conteudos = list(conteudos or [])
        self._dificuldade = 3
        self.alterar_dificuldade(dificuldade)
        self._valor = valor

    @property
    def conteudos(self) -> list[str]:
        return list(self._conteudos)

    @property
    def dificuldade(self) -> int:
        return self._dificuldade

    @property
    def valor(self) -> float:
        return self._valor

    def cadastrar_conteudos(self, conteudo: str) -> None:
        if conteudo.strip():
            self._conteudos.append(conteudo.strip())

    def alterar_dificuldade(self, nivel: int) -> None:
        if not 1 <= nivel <= 5:
            raise ValueError("Dificuldade deve estar entre 1 e 5.")
        self._dificuldade = nivel

    def exibir_detalhes(self) -> str:
        conteudos = ", ".join(self._conteudos) or "não informados"
        return (f"Prova de {self._disciplina.nome} em {self._data:%d/%m/%Y} - "
                f"Conteúdos: {conteudos} - Dificuldade: {self._dificuldade}/5")

    def gerar_alerta(self, hoje: date | None = None) -> str | None:
        d = self.dias_restantes(hoje)
        if d < 0 or d > 7:
            return None
        quando = "hoje" if d == 0 else f"em {d} dia(s)"
        return f"Prova de {self._disciplina.nome} {quando}!"