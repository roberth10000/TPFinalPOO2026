
from datetime import date, timedelta
from planejamento import PlanejamentoEstudos

# Simula uma prova daqui a 10 dias
data_prova = date.today() + timedelta(days=10)

avaliacao = {
    "data": data_prova.strftime("%d/%m/%Y")
}

# Cria o planejamento
planejamento = PlanejamentoEstudos(
    avaliacao=avaliacao,
    conteudos=["Derivadas", "Integrais"],
    dificuldade="difícil"
)

# Simula horários livres de segunda a sexta
horarios_livres = [
    {"dia_semana": dia, "inicio": "19:00", "fim": "21:00"}
    for dia in range(5)
]

# Gera as sessões
resultado = planejamento.gerar_planejamento(
    agenda=horarios_livres
)

print("PLANEJAMENTO DE ESTUDOS")
print("-------------------------")

print(f"Data da prova: {data_prova:%d/%m/%Y}")

for sessao in resultado["sessoes"]:
    print(
        f"{sessao.data} - "
        f"{sessao.horario_inicio} às {sessao.horario_fim} - "
        f"{sessao.conteudo}"
    )

print(f"\nTotal de sessões: {len(resultado['sessoes'])}")
