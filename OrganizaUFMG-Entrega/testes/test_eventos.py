import unittest
from dataclasses import dataclass
from datetime import date, time

from aula import Aula
from avaliacao import Avaliacao
from trabalho import Trabalho
from atividade import Atividade
from calendario import Calendario
from evento import Evento


@dataclass
class Disc:
    id: int
    nome: str


D = Disc(1, "Cálculo I")
HOJE = date(2026, 10, 26)  # segunda-feira


class TestEventos(unittest.TestCase):
    def test_evento_e_abstrato(self):
        with self.assertRaises(TypeError):
            Evento("x", HOJE, None, D)

    def test_alerta_avaliacao(self):
        self.assertIsNotNone(Avaliacao("P1", date(2026, 10, 30), None, D).gerar_alerta(HOJE))
        self.assertIsNone(Avaliacao("P1", date(2026, 12, 1), None, D).gerar_alerta(HOJE))
        self.assertIsNone(Avaliacao("P1", date(2026, 10, 1), None, D).gerar_alerta(HOJE))

    def test_dificuldade_invalida(self):
        with self.assertRaises(ValueError):
            Avaliacao("P1", HOJE, None, D, dificuldade=9)

    def test_trabalho_concluido_nao_alerta(self):
        t = Trabalho("TP", date(2026, 10, 27), None, D)
        self.assertIn("vence", t.gerar_alerta(HOJE))
        t.marcar_concluido()
        self.assertIsNone(t.gerar_alerta(HOJE))

    def test_trabalho_atrasado(self):
        t = Trabalho("TP", date(2026, 10, 20), None, D)
        self.assertIn("atrasado", t.gerar_alerta(HOJE))

    def test_aula_ocorre_em(self):
        a = Aula("Cálculo", D, 0, time(8), time(10))
        self.assertTrue(a.ocorre_em(date(2026, 10, 26)))
        self.assertFalse(a.ocorre_em(date(2026, 10, 27)))
        self.assertEqual(a.proxima_data(date(2026, 10, 27)), date(2026, 11, 2))

    def test_aula_horario_invalido(self):
        with self.assertRaises(ValueError):
            Aula("X", D, 0, time(10), time(8))

    def test_polimorfismo_no_calendario(self):
        cal = Calendario([Aula("Cálculo", D, 0, time(8), time(10)),
                          Avaliacao("P1", HOJE, time(14), D),
                          Atividade("Lista 1", HOJE, None, D)])
        dia = cal.listar_eventos_por_data(HOJE)
        self.assertEqual(len(dia), 3)
        self.assertEqual([type(e) for e in dia], [Atividade, Aula, Avaliacao])
        for e in dia:
            self.assertIsInstance(e.exibir_detalhes(), str)

    def test_substituir_e_remover(self):
        a = Atividade("L1", HOJE, None, D)
        b = Atividade("L2", HOJE, None, D)
        cal = Calendario([a])
        cal.substituir_evento(a, b)
        self.assertEqual(cal.consultar_eventos(), [b])
        cal.remover_evento(b)
        self.assertEqual(cal.consultar_eventos(), [])


if __name__ == "__main__":
    unittest.main()