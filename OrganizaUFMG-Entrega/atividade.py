from datetime import date, time
from evento import Evento


class Atividade(Evento):
    TIPO = "atividade"

    def __init__(self, titulo: str, data: date, horario: time | None, disciplina,
                 tipo_tarefa: str = "exercício", status: str = "pendente",
                 descricao: str = ""):
        super().__init__(titulo, data, horario, disciplina, descricao)
        self._tipo_tarefa = tipo_tarefa
        self._status = status

    @property
    def tipo_tarefa(self) -> str:
        return self._tipo_tarefa

    @property
    def status(self) -> str:
        return self._status

    def marcar_concluida(self) -> None:
        self._status = "concluido"

    def exibir_detalhes(self) -> str:
        return (f"{self._tipo_tarefa.capitalize()}: '{self._titulo}' ({self._disciplina.nome}) - "
                f"Prazo: {self._data:%d/%m/%Y} - Situação: {self._status}")

    def gerar_alerta(self, hoje: date | None = None) -> str | None:
        if self._status == "concluido":
            return None
        d = self.dias_restantes(hoje)
        if d < 0:
            return f"Atividade '{self._titulo}' está atrasada!"
        if d <= 2:
            quando = "hoje" if d == 0 else f"em {d} dia(s)"
            return f"Atividade '{self._titulo}' vence {quando}."
        return None