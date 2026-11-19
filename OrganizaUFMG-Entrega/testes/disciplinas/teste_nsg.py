
from gerenciador_disciplinas import GerenciadorDisciplinas


def main():

    gerenciador = GerenciadorDisciplinas("organizaufmg.db")

    nsg = gerenciador.calcular_nsg()

    print("ORGANIZAUFMG")
    print("-------------------------")
    print(f"NSG atual: {nsg:.2f}")


if __name__ == "__main__":
    main()
