
from disciplinas import Disciplina
from repositorio_disciplinas import RepositorioDisciplinas


def main():

    repositorio = RepositorioDisciplinas("organizaufmg.db")

    # Cadastra uma disciplina
    disciplina = Disciplina("Cálculo I", "Ana", 30)

    repositorio.salvar_disciplina(disciplina)

    print("DISCIPLINA CADASTRADA:")
    disciplina.exibir_informacoes()

    # Atualiza a nota
    disciplina.atualizar_nota(65)
    repositorio.salvar_disciplina(disciplina)

    # Consulta os dados salvos
    print("\nDISCIPLINA RECUPERADA DO BANCO:")

    disciplina_salva = repositorio.buscar_disciplina(
        disciplina.id
    )

    disciplina_salva.exibir_informacoes()

    # Lista todas as disciplinas
    print("\nTODAS AS DISCIPLINAS:")

    for item in repositorio.listar_disciplinas():
        print(f"{item.id} - {item.nome} - Nota: {item.nota_atual}")


if __name__ == "__main__":
    main()
