
from disciplinas import Disciplina

disciplina1 = Disciplina("Cálculo I", "Ana", 30)

disciplina1.exibir_informacoes()

print("\nAtualizando a nota...")
disciplina1.atualizar_nota(65)

print("\nInformações atualizadas:")
disciplina1.exibir_informacoes()
