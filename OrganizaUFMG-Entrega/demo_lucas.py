import customtkinter as ctk
from dataclasses import dataclass

from calendario import Calendario
from agendasemanal import AgendaSemanal
from repositorio_eventos import RepositorioEventos
from telas.tela_calendario import TelaCalendario
from telas.tela_agenda import TelaAgenda


@dataclass
class DisciplinaFake:          # substituta temporária da classe da Isabel
    id: int
    nome: str


DISCIPLINAS = [DisciplinaFake(1, "Cálculo I"), DisciplinaFake(2, "Física I"),
               DisciplinaFake(3, "Programação")]
POR_ID = {d.id: d for d in DISCIPLINAS}

repo = RepositorioEventos("organizaufmg.db")
calendario = Calendario(repo.listar_eventos(lambda i: POR_ID[i]))
agenda = AgendaSemanal(repo.listar_compromissos())

app = ctk.CTk()
app.title("OrganizaUFMG - Calendário e Agenda")
app.geometry("1100x700")
abas = ctk.CTkTabview(app)
abas.pack(fill="both", expand=True)

tela_cal = TelaCalendario(abas.add("Calendário"), calendario, agenda, repo, lambda: DISCIPLINAS)
tela_cal.pack(fill="both", expand=True)
tela_agenda = TelaAgenda(abas.add("Agenda semanal"), agenda, calendario, repo)
tela_agenda.pack(fill="both", expand=True)

# a agenda precisa refletir mudanças feitas no calendário ao trocar de aba
abas.configure(command=lambda: (tela_agenda.atualizar(), tela_cal.atualizar()))
app.mainloop()