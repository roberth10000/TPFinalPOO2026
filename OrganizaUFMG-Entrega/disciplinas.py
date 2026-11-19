
class Disciplina:

    def __init__(self, nome, professor, nota_atual=0, id=None):
        self.id = id
        self.nome = nome
        self.professor = professor
        self.nota_atual = nota_atual

    def atualizar_nota(self, nova_nota):
        if 0 <= nova_nota <= 100:
            self.nota_atual = nova_nota
            print("Nota atualizada com sucesso!")
        else:
            print("Erro: a nota deve estar entre 0 e 100.")

    def exibir_informacoes(self):
        print(f"ID: {self.id}")
        print(f"Disciplina: {self.nome}")
        print(f"Professor: {self.professor}")
        print(f"Nota atual: {self.nota_atual}")
