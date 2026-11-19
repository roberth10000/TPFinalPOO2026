from datetime import date, time
from evento import Evento


class Trabalho(Evento):
    TIPO = "trabalho"

    def __init__(self, titulo: str, data: date, horario: time | None, disciplina,
                 valor: float = 0.0, status: str = "pendente", descricao: str = ""):
        super().__init__(titulo, data, horario, disciplina, descricao)
        self._valor = valor
        self._status = status

    @property
    def valor(self) -> float:
        return self._valor

    @property
    def status(self) -> str:
        return self._status

    @property
    def prazo_entrega(self) -> date:
        return self._data

    def marcar_concluido(self) -> None:
        self._status = "concluido"

    def exibir_detalhes(self) -> str:
        return (f"Trabalho '{self._titulo}' ({self._disciplina.nome}) - "
                f"Prazo: {self._data:%d/%m/%Y} - Status: {self._status}")

    def gerar_alerta(self, hoje: date | None = None) -> str | None:
        if self._status == "concluido":
            return None
        d = self.dias_restantes(hoje)
        if d < 0:
            return f"Trabalho '{self._titulo}' está atrasado há {-d} dia(s)!"
        if d <= 3:
            quando = "hoje" if d == 0 else f"em {d} dia(s)"
            return f"Trabalho '{self._titulo}' vence {quando}."
        return None