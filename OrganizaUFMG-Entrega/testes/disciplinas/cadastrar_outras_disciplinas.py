from disciplinas import Disciplina
from repositorio_disciplinas import RepositorioDisciplinas


def main():

    repositorio = RepositorioDisciplinas("organizaufmg.db")

    # Disciplinas que queremos cadastrar
    novas_disciplinas = [
        Disciplina("Física I", "Carlos", 40),
        Disciplina("Programação", "Mariana", 55)
    ]

    # Consulta as disciplinas que já estão cadastradas
    cadastradas = repositorio.listar_disciplinas()

    for disciplina in novas_disciplinas:

        # Verifica se já existe uma disciplina com esse nome
        existe = any(
            item.nome == disciplina.nome
            for item in cadastradas
        )

        if not existe:
            repositorio.salvar_disciplina(disciplina)
            print(f"{disciplina.nome} cadastrada com sucesso!")
        else:
            print(f"{disciplina.nome} já está cadastrada!")

    # Mostra todas as disciplinas
    print("\nDISCIPLINAS NO BANCO:")

    for item in repositorio.listar_disciplinas():
        print(f"{item.nome} - Nota: {item.nota_atual}")


if __name__ == "__main__":
    main()