from datetime import time


class Compromisso:
    """Intervalo semanal: compromisso fixo ou janela de horário livre."""

    def __init__(self, dia_semana: int, horario_inicio: time, horario_fim: time,
                 descricao: str = "", livre: bool = False):
        if not 0 <= dia_semana <= 6:
            raise ValueError("Dia da semana deve estar entre 0 e 6.")
        if horario_fim <= horario_inicio:
            raise ValueError("O fim deve ser depois do início.")
        self.id = None
        self._dia_semana = dia_semana
        self._horario_inicio = horario_inicio
        self._horario_fim = horario_fim
        self._descricao = descricao
        self._livre = livre

    @property
    def dia_semana(self) -> int:
        return self._dia_semana

    @property
    def horario_inicio(self) -> time:
        return self._horario_inicio

    @property
    def horario_fim(self) -> time:
        return self._horario_fim

    @property
    def descricao(self) -> str:
        return self._descricao

    @property
    def livre(self) -> bool:
        return self._livre

    def __str__(self) -> str:
        return f"{self._horario_inicio:%H:%M}-{self._horario_fim:%H:%M} {self._descricao}"