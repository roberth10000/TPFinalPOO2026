from datetime import date
from evento import Evento
from aula import Aula


class Calendario:
    def __init__(self, eventos: list[Evento] | None = None):
        self._eventos: list[Evento] = list(eventos or [])

    def adicionar_evento(self, evento: Evento) -> None:
        self._eventos.append(evento)

    def remover_evento(self, evento: Evento) -> None:
        self._eventos.remove(evento)

    def substituir_evento(self, antigo: Evento, novo: Evento) -> None:
        self._eventos[self._eventos.index(antigo)] = novo

    def consultar_eventos(self, disciplina=None, tipo: str | None = None) -> list[Evento]:
        res = self._eventos
        if disciplina is not None:
            res = [e for e in res if e.disciplina is disciplina or e.disciplina == disciplina]
        if tipo is not None:
            res = [e for e in res if e.TIPO == tipo]
        return list(res)

    def listar_eventos_por_data(self, dia: date) -> list[Evento]:
        from datetime import time
        doDia = [e for e in self._eventos if e.ocorre_em(dia)]
        return sorted(doDia, key=lambda e: e.horario or time.min)

    def aulas(self) -> list[Aula]:
        return [e for e in self._eventos if isinstance(e, Aula)]

    def gerar_alertas(self, hoje: date | None = None) -> list[str]:
        """Polimorfismo: cada evento sabe gerar o próprio alerta."""
        hoje = hoje or date.today()
        pares = [(e.dias_restantes(hoje), e.gerar_alerta(hoje)) for e in self._eventos]
        return [alerta for _, alerta in sorted((p for p in pares if p[1]), key=lambda p: p[0])]

    def __iter__(self):
        return iter(self._eventos)