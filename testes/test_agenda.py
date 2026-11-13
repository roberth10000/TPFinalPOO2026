import unittest
from dataclasses import dataclass
from datetime import time

from agendasemanal import AgendaSemanal
from compromisso import Compromisso
from aula import Aula


@dataclass
class Disc:
    id: int
    nome: str


class TestAgenda(unittest.TestCase):
    def setUp(self):
        self.ag = AgendaSemanal()

    def test_conflito_sobreposto(self):
        self.ag.cadastrar_compromisso(Compromisso(0, time(8), time(10), "estágio"))
        with self.assertRaises(ValueError):
            self.ag.cadastrar_compromisso(Compromisso(0, time(9), time(11)))

    def test_encostado_nao_conflita(self):
        self.ag.cadastrar_compromisso(Compromisso(0, time(8), time(10)))
        self.ag.cadastrar_compromisso(Compromisso(0, time(10), time(12)))
        self.assertEqual(len(self.ag.compromissos_fixos), 2)

    def test_dias_diferentes_nao_conflitam(self):
        self.ag.cadastrar_compromisso(Compromisso(0, time(8), time(10)))
        self.ag.cadastrar_compromisso(Compromisso(1, time(8), time(10)))

    def test_aula_conflita_com_compromisso(self):
        self.ag.sincronizar_aulas([Aula("Cálculo", Disc(1, "C"), 2, time(8), time(10))])
        self.assertTrue(self.ag.verificar_conflito(Compromisso(2, time(9), time(11))))

    def test_ignorar_ao_editar(self):
        aula = Aula("Cálculo", Disc(1, "C"), 2, time(8), time(10))
        self.ag.sincronizar_aulas([aula])
        self.assertFalse(self.ag.verificar_conflito(aula, ignorar=aula))

    def test_disponibilidade_dia_todo(self):
        self.ag.cadastrar_compromisso(Compromisso(0, time(9), time(11)))
        livres = self.ag.identificar_disponibilidade(time(7), time(12))
        self.assertEqual(livres[0], [(time(7), time(9)), (time(11), time(12))])
        self.assertEqual(livres[1], [(time(7), time(12))])

    def test_disponibilidade_com_janelas_livres(self):
        self.ag.cadastrar_horario_livre(Compromisso(0, time(14), time(18), livre=True))
        self.ag.cadastrar_compromisso(Compromisso(0, time(15), time(16)))
        livres = self.ag.identificar_disponibilidade()
        self.assertEqual(livres[0], [(time(14), time(15)), (time(16), time(18))])


if __name__ == "__main__":
    unittest.main()