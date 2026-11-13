from datetime import time
from compromisso import Compromisso
from aula import Aula


def _min(t: time) -> int:
    return t.hour * 60 + t.minute


def _hora(m: int) -> time:
    return time(m // 60, m % 60)


class AgendaSemanal:
    def __init__(self, compromissos: list[Compromisso] | None = None):
        self._compromissos_fixos: list[Compromisso] = []
        self._horarios_livres: list[Compromisso] = []
        self._aulas: list[Aula] = []
        for c in compromissos or []:
            (self._horarios_livres if c.livre else self._compromissos_fixos).append(c)

    # ---------- consultas ----------
    @property
    def compromissos_fixos(self) -> list[Compromisso]:
        return list(self._compromissos_fixos)

    @property
    def horarios_livres(self) -> list[Compromisso]:
        return list(self._horarios_livres)

    @property
    def aulas(self) -> list[Aula]:
        return list(self._aulas)

    # ---------- conflito ----------
    @staticmethod
    def _sobrepoe(a, b) -> bool:
        # duck typing: qualquer objeto com dia_semana, horario_inicio e horario_fim
        return (a.dia_semana == b.dia_semana
                and a.horario_inicio < b.horario_fim
                and b.horario_inicio < a.horario_fim)

    def verificar_conflito(self, novo, ignorar=None) -> bool:
        ocupados = self._compromissos_fixos + self._aulas
        return any(self._sobrepoe(novo, o) for o in ocupados if o is not ignorar)

    # ---------- cadastro ----------
    def cadastrar_compromisso(self, compromisso: Compromisso) -> None:
        if self.verificar_conflito(compromisso):
            raise ValueError("Conflito de horário com outro compromisso ou aula.")
        self._compromissos_fixos.append(compromisso)

    def cadastrar_horario_livre(self, janela: Compromisso) -> None:
        self._horarios_livres.append(janela)

    def remover_compromisso(self, compromisso: Compromisso) -> None:
        if compromisso in self._compromissos_fixos:
            self._compromissos_fixos.remove(compromisso)
        elif compromisso in self._horarios_livres:
            self._horarios_livres.remove(compromisso)

    def sincronizar_aulas(self, aulas: list[Aula]) -> None:
        """As aulas vêm do Calendario e contam como horários ocupados."""
        self._aulas = list(aulas)

    # ---------- disponibilidade ----------
    @staticmethod
    def _mesclar(intervalos: list[tuple[int, int]]) -> list[tuple[int, int]]:
        res: list[tuple[int, int]] = []
        for ini, fim in sorted(intervalos):
            if res and ini <= res[-1][1]:
                res[-1] = (res[-1][0], max(res[-1][1], fim))
            else:
                res.append((ini, fim))
        return res

    @staticmethod
    def _subtrair(livres, ocupados):
        resultado = []
        for ini, fim in livres:
            atual = ini
            for o_ini, o_fim in sorted(ocupados):
                if o_fim <= atual or o_ini >= fim:
                    continue
                if o_ini > atual:
                    resultado.append((atual, o_ini))
                atual = max(atual, o_fim)
            if atual < fim:
                resultado.append((atual, fim))
        return resultado

    def identificar_disponibilidade(self, inicio_dia: time = time(7, 0),
                                    fim_dia: time = time(22, 0)
                                    ) -> dict[int, list[tuple[time, time]]]:
        """Retorna {dia_semana: [(inicio, fim), ...]} com os intervalos realmente livres.

        Se o aluno cadastrou janelas livres naquele dia, usa só elas;
        caso contrário, usa o dia todo (inicio_dia..fim_dia). Em ambos os casos,
        desconta compromissos fixos e aulas.
        """
        resultado: dict[int, list[tuple[time, time]]] = {}
        for dia in range(7):
            janelas = [(_min(j.horario_inicio), _min(j.horario_fim))
                       for j in self._horarios_livres if j.dia_semana == dia]
            base = self._mesclar(janelas) if janelas else [(_min(inicio_dia), _min(fim_dia))]
            ocupados = [(_min(o.horario_inicio), _min(o.horario_fim))
                        for o in self._compromissos_fixos + self._aulas
                        if o.dia_semana == dia]
            livres = self._subtrair(base, self._mesclar(ocupados))
            resultado[dia] = [(_hora(i), _hora(f)) for i, f in livres]
        return resultado
