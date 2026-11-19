
from repositorio_disciplinas import RepositorioDisciplinas


class GerenciadorDisciplinas:

    def __init__(self, caminho_banco):
        self.repositorio = RepositorioDisciplinas(caminho_banco)

    def calcular_nsg(self):
        disciplinas = self.repositorio.listar_disciplinas()

        if len(disciplinas) == 0:
            return 0

        soma_notas = 0

        for disciplina in disciplinas:
            soma_notas += disciplina.nota_atual

        nsg = soma_notas / len(disciplinas)

        return nsg
