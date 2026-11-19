
import customtkinter as ctk

from calendario import Calendario
from agendasemanal import AgendaSemanal
from repositorio_eventos import RepositorioEventos
from gerenciador_disciplinas import GerenciadorDisciplinas

from telas.tela_calendario import TelaCalendario
from telas.tela_agenda import TelaAgenda
from telas.tela_disciplinas import TelaDisciplinas
from telas.tela_planejamento import TelaPlanejamento
from repositorio_sessoes import RepositorioSessoes


# Banco de dados
CAMINHO_BANCO = "organizaufmg.db"

# Gerenciador de disciplinas
gerenciador = GerenciadorDisciplinas(CAMINHO_BANCO)


# Funções para consultar as disciplinas
def listar_disciplinas():
    return gerenciador.repositorio.listar_disciplinas()


def buscar_disciplina(id):
    disciplina = gerenciador.repositorio.buscar_disciplina(id)

    if disciplina is None:
        raise ValueError(f"Disciplina com ID {id} não encontrada.")

    return disciplina


# Repositório de eventos
repo = RepositorioEventos(CAMINHO_BANCO)
repo_sessoes = RepositorioSessoes(CAMINHO_BANCO)
repo_sessoes.pausar_sessoes_interrompidas()     

# Calendário e agenda
calendario = Calendario(repo.listar_eventos(buscar_disciplina))
agenda = AgendaSemanal(repo.listar_compromissos())


# Janela principal
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("OrganizaUFMG")
app.geometry("1100x700")

# Abas
abas = ctk.CTkTabview(app)
abas.pack(fill="both", expand=True)


# Aba Calendário
tela_calendario = TelaCalendario(
    abas.add("Calendário"),
    calendario,
    agenda,
    repo,
    listar_disciplinas
)
tela_calendario.pack(fill="both", expand=True)


# Aba Agenda Semanal
tela_agenda = TelaAgenda(
    abas.add("Agenda semanal"),
    agenda,
    calendario,
    repo
)
tela_agenda.pack(fill="both", expand=True)


# Aba Disciplinas e NSG


tela_disciplinas = TelaDisciplinas(
    abas.add("Disciplinas e NSG"),
    gerenciador,
    calendario,
    agenda,
    repo
)



tela_disciplinas.pack(
    fill="both",
    expand=True
)

# Aba Planejamento de Estudos


tela_planejamento = TelaPlanejamento(
    abas.add("Planejamento de Estudos"),
    calendario,
    agenda,
    repo_sessoes
)



tela_planejamento.pack(
    fill="both",
    expand=True
)

# Atualizar as telas ao trocar de aba
abas.configure(
    command=lambda: (
        tela_agenda.atualizar(),
        tela_calendario.atualizar(),
        tela_planejamento.atualizar_avaliacoes()
    )
)


# Iniciar o aplicativo
app.mainloop()
