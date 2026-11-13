import customtkinter as ctk
from tkinter import messagebox

from aula import NOMES_DIAS
from compromisso import Compromisso
from telas.utils_tela import parse_hora


class TelaAgenda(ctk.CTkFrame):
    def __init__(self, master, agenda, calendario, repositorio):
        super().__init__(master)
        self._agenda = agenda
        self._cal = calendario
        self._repo = repositorio
        self._montar()
        self.atualizar()

    def _montar(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=3)
        self.rowconfigure(2, weight=2)

        # ----- formulário -----
        form = ctk.CTkFrame(self)
        form.grid(row=0, column=0, sticky="ew", padx=12, pady=10)
        self._dia = ctk.StringVar(value=NOMES_DIAS[0])
        self._tipo = ctk.StringVar(value="Compromisso fixo")
        ctk.CTkOptionMenu(form, values=NOMES_DIAS, variable=self._dia, width=110).pack(side="left", padx=4, pady=8)
        self._ini = ctk.CTkEntry(form, placeholder_text="Início HH:MM", width=100)
        self._ini.pack(side="left", padx=4)
        self._fim = ctk.CTkEntry(form, placeholder_text="Fim HH:MM", width=100)
        self._fim.pack(side="left", padx=4)
        self._desc = ctk.CTkEntry(form, placeholder_text="Descrição (ex: estágio)", width=190)
        self._desc.pack(side="left", padx=4)
        ctk.CTkOptionMenu(form, values=["Compromisso fixo", "Horário livre"],
                          variable=self._tipo, width=140).pack(side="left", padx=4)
        ctk.CTkButton(form, text="Adicionar", width=90, command=self._adicionar).pack(side="left", padx=6)

        # ----- semana -----
        semana = ctk.CTkFrame(self)
        semana.grid(row=1, column=0, sticky="nsew", padx=12)
        self._colunas = []
        for i, nome in enumerate(NOMES_DIAS):
            semana.columnconfigure(i, weight=1, uniform="dia")
            semana.rowconfigure(1, weight=1)
            ctk.CTkLabel(semana, text=nome, font=ctk.CTkFont(weight="bold")).grid(row=0, column=i, pady=4)
            col = ctk.CTkScrollableFrame(semana, width=110)
            col.grid(row=1, column=i, sticky="nsew", padx=2, pady=(0, 4))
            self._colunas.append(col)

        # ----- disponibilidade -----
        rodape = ctk.CTkFrame(self)
        rodape.grid(row=2, column=0, sticky="nsew", padx=12, pady=10)
        rodape.columnconfigure(0, weight=1)
        rodape.rowconfigure(1, weight=1)
        ctk.CTkButton(rodape, text="Ver horários disponíveis para estudo",
                      command=self._mostrar_disponibilidade).grid(row=0, column=0, pady=6)
        self._saida = ctk.CTkTextbox(rodape, height=120)
        self._saida.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

    # ---------- atualização ----------
    def atualizar(self):
        self._agenda.sincronizar_aulas(self._cal.aulas())
        for col in self._colunas:
            for w in col.winfo_children():
                w.destroy()
        for aula in self._agenda.aulas:
            ctk.CTkLabel(self._colunas[aula.dia_semana], justify="left", wraplength=110,
                         text=f"[aula] {aula.horario_inicio:%H:%M}-{aula.horario_fim:%H:%M}\n{aula.disciplina.nome}"
                         ).pack(anchor="w", pady=2)
        for comp in self._agenda.compromissos_fixos + self._agenda.horarios_livres:
            self._item(comp)

    def _item(self, comp: Compromisso):
        prefixo = "[livre]" if comp.livre else "[fixo]"
        quadro = ctk.CTkFrame(self._colunas[comp.dia_semana], fg_color="transparent")
        quadro.pack(fill="x", pady=2)
        ctk.CTkLabel(quadro, justify="left", wraplength=80,
                     text=f"{prefixo} {comp.horario_inicio:%H:%M}-{comp.horario_fim:%H:%M}\n{comp.descricao}"
                     ).pack(side="left", anchor="w")
        ctk.CTkButton(quadro, text="x", width=24, fg_color="#a33",
                      command=lambda c=comp: self._remover(c)).pack(side="right")

    # ---------- ações ----------
    def _adicionar(self):
        try:
            comp = Compromisso(NOMES_DIAS.index(self._dia.get()),
                               parse_hora(self._ini.get()), parse_hora(self._fim.get()),
                               self._desc.get().strip(), livre=self._tipo.get() == "Horário livre")
            if comp.livre:
                self._agenda.cadastrar_horario_livre(comp)
            else:
                self._agenda.cadastrar_compromisso(comp)
        except ValueError as erro:
            messagebox.showerror("Não foi possível adicionar", str(erro))
            return
        self._repo.salvar_compromisso(comp)
        for e in (self._ini, self._fim, self._desc):
            e.delete(0, "end")
        self.atualizar()

    def _remover(self, comp: Compromisso):
        self._repo.remover_compromisso(comp)
        self._agenda.remover_compromisso(comp)
        self.atualizar()

    def _mostrar_disponibilidade(self):
        self._saida.delete("1.0", "end")
        for dia, intervalos in self._agenda.identificar_disponibilidade().items():
            faixas = ", ".join(f"{i:%H:%M}-{f:%H:%M}" for i, f in intervalos) or "sem horário livre"
            self._saida.insert("end", f"{NOMES_DIAS[dia]}: {faixas}\n")