from datetime import date, time, timedelta
from evento import Evento

NOMES_DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]


class Aula(Evento):
    TIPO = "aula"

    def __init__(self, titulo: str, disciplina, dia_semana: int,
                 horario_inicio: time, horario_fim: time,
                 local: str = "", descricao: str = ""):
        if not 0 <= dia_semana <= 6:
            raise ValueError("Dia da semana deve estar entre 0 (segunda) e 6 (domingo).")
        if horario_fim <= horario_inicio:
            raise ValueError("O fim da aula deve ser depois do início.")
        super().__init__(titulo, None, horario_inicio, disciplina, descricao)
        self._dia_semana = dia_semana
        self._horario_inicio = horario_inicio
        self._horario_fim = horario_fim
        self._local = local

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
    def local(self) -> str:
        return self._local

    def ocorre_em(self, dia: date) -> bool:
        return dia.weekday() == self._dia_semana

    def proxima_data(self, hoje: date | None = None) -> date:
        hoje = hoje or date.today()
        return hoje + timedelta(days=(self._dia_semana - hoje.weekday()) % 7)

    def exibir_detalhes(self) -> str:
        return (f"Aula de {self._disciplina.nome} - {NOMES_DIAS[self._dia_semana]}, "
                f"{self._horario_inicio:%H:%M} às {self._horario_fim:%H:%M}"
                f" - Local: {self._local or 'não informado'}")

    def gerar_alerta(self, hoje: date | None = None) -> str | None:
        d = self.dias_restantes(hoje)
        if d == 0:
            return f"Aula de {self._disciplina.nome} hoje às {self._horario_inicio:%H:%M}."
        if d == 1:
            return f"Aula de {self._disciplina.nome} amanhã às {self._horario_inicio:%H:%M}."
        return None
