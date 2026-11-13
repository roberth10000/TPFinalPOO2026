from abc import ABC, abstractmethod
from datetime import date, time


class Evento(ABC):
    TIPO = "evento"

    def __init__(self, titulo: str, data: date | None, horario: time | None,
                 disciplina, descricao: str = ""):
        if not titulo or not titulo.strip():
            raise ValueError("O título não pode ser vazio.")
        self.id = None  # preenchido pelo repositório
        self._titulo = titulo.strip()
        self._data = data
        self._horario = horario
        self._disciplina = disciplina
        self._descricao = descricao

    @property
    def titulo(self) -> str:
        return self._titulo

    @property
    def data(self) -> date | None:
        return self._data

    @property
    def horario(self) -> time | None:
        return self._horario

    @property
    def disciplina(self):
        return self._disciplina

    @property
    def descricao(self) -> str:
        return self._descricao

    def ocorre_em(self, dia: date) -> bool:
        """Evento pontual: ocorre apenas na sua data."""
        return self._data == dia

    def proxima_data(self, hoje: date | None = None) -> date:
        return self._data

    def dias_restantes(self, hoje: date | None = None) -> int:
        hoje = hoje or date.today()
        return (self.proxima_data(hoje) - hoje).days

    @abstractmethod
    def exibir_detalhes(self) -> str: ...

    @abstractmethod
    def gerar_alerta(self, hoje: date | None = None) -> str | None: ...

    def __str__(self) -> str:
        return self.exibir_detalhes()
