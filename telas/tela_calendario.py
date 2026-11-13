import calendar
from datetime import date
import customtkinter as ctk
from tkinter import messagebox

from aula import Aula
from telas.formulario_evento import FormularioEvento

MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
         "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
DIAS_CURTOS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]


class TelaCalendario(ctk.CTkFrame):
    def __init__(self, master, calendario, agenda, repositorio, listar_disciplinas):
        super().__init__(master)
        self._cal = calendario
        self._agenda = agenda
        self._repo = repositorio
        self._listar_disciplinas = listar_disciplinas  # função -> lista de Disciplina

        hoje = date.today()
        self._ano, self._mes = hoje.year, hoje.month
        self._selecionado = hoje

        self._montar()
        self.atualizar()

    # ---------- layout ----------
    def _montar(self):
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(2, weight=1)

        self._alertas = ctk.CTkLabel(self, text="", justify="left", anchor="w",
                                     wraplength=700, text_color="#e0a030")
        self._alertas.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(10, 0))

        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.grid(row=1, column=0, sticky="ew", padx=12, pady=8)
        ctk.CTkButton(topo, text="<", width=36, command=lambda: self._mudar_mes(-1)).pack(side="left")
        self._titulo_mes = ctk.CTkLabel(topo, text="", font=ctk.CTkFont(size=18, weight="bold"), width=200)
        self._titulo_mes.pack(side="left", padx=8)
        ctk.CTkButton(topo, text=">", width=36, command=lambda: self._mudar_mes(1)).pack(side="left")
        ctk.CTkButton(topo, text="+ Novo evento", command=self._novo).pack(side="right")

        self._grade = ctk.CTkFrame(self)
        self._grade.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))

        lateral = ctk.CTkFrame(self)
        lateral.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=(0, 12), pady=(8, 12))
        lateral.rowconfigure(1, weight=1)
        lateral.columnconfigure(0, weight=1)
        self._titulo_dia = ctk.CTkLabel(lateral, text="", font=ctk.CTkFont(size=15, weight="bold"))
        self._titulo_dia.grid(row=0, column=0, pady=8)
        self._lista = ctk.CTkScrollableFrame(lateral)
        self._lista.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))

    # ---------- atualização ----------
    def atualizar(self):
        self._agenda.sincronizar_aulas(self._cal.aulas())
        self._titulo_mes.configure(text=f"{MESES[self._mes - 1]} {self._ano}")
        self._desenhar_grade()
        self._desenhar_lista()
        alertas = self._cal.gerar_alertas()
        self._alertas.configure(text=("Avisos:  " + "  |  ".join(alertas)) if alertas else "")

    def _desenhar_grade(self):
        for w in self._grade.winfo_children():
            w.destroy()
        for c in range(7):
            self._grade.columnconfigure(c, weight=1)
            ctk.CTkLabel(self._grade, text=DIAS_CURTOS[c]).grid(row=0, column=c, pady=4)
        for r, semana in enumerate(calendar.monthcalendar(self._ano, self._mes), start=1):
            self._grade.rowconfigure(r, weight=1)
            for c, numero in enumerate(semana):
                if numero == 0:
                    continue
                dia = date(self._ano, self._mes, numero)
                qtd = len(self._cal.listar_eventos_por_data(dia))
                texto = str(numero) if qtd == 0 else f"{numero}\n({qtd})"
                cor = "#1f6aa5" if qtd else "gray30"
                borda = 3 if dia == self._selecionado else 0
                ctk.CTkButton(self._grade, text=texto, fg_color=cor, border_width=borda,
                              border_color="white", height=52,
                              command=lambda d=dia: self._selecionar(d)
                              ).grid(row=r, column=c, sticky="nsew", padx=2, pady=2)

    def _desenhar_lista(self):
        for w in self._lista.winfo_children():
            w.destroy()
        self._titulo_dia.configure(text=f"Eventos de {self._selecionado:%d/%m/%Y}")
        eventos = self._cal.listar_eventos_por_data(self._selecionado)
        if not eventos:
            ctk.CTkLabel(self._lista, text="Nenhum evento neste dia.").pack(pady=10)
        for ev in eventos:
            quadro = ctk.CTkFrame(self._lista)
            quadro.pack(fill="x", pady=4)
            ctk.CTkLabel(quadro, text=ev.exibir_detalhes(), wraplength=260,
                         justify="left", anchor="w").pack(fill="x", padx=8, pady=(6, 2))
            botoes = ctk.CTkFrame(quadro, fg_color="transparent")
            botoes.pack(anchor="e", padx=8, pady=(0, 6))
            ctk.CTkButton(botoes, text="Editar", width=70,
                          command=lambda e=ev: self._editar(e)).pack(side="left", padx=2)
            ctk.CTkButton(botoes, text="Excluir", width=70, fg_color="#a33",
                          command=lambda e=ev: self._excluir(e)).pack(side="left", padx=2)

    # ---------- ações ----------
    def _mudar_mes(self, delta: int):
        m = self._mes + delta
        self._ano += (m - 1) // 12
        self._mes = (m - 1) % 12 + 1
        self.atualizar()

    def _selecionar(self, dia: date):
        self._selecionado = dia
        self.atualizar()

    def _checar_conflito(self, ev, antigo=None):
        if isinstance(ev, Aula) and self._agenda.verificar_conflito(ev, ignorar=antigo):
            raise ValueError("Esta aula conflita com outra aula ou compromisso fixo.")

    def _novo(self):
        def salvar(ev):
            self._checar_conflito(ev)
            self._repo.salvar_evento(ev)
            self._cal.adicionar_evento(ev)
            self.atualizar()
        FormularioEvento(self, self._listar_disciplinas(), salvar, data_padrao=self._selecionado)

    def _editar(self, antigo):
        def salvar(novo):
            self._checar_conflito(novo, antigo)
            novo.id = antigo.id
            self._repo.salvar_evento(novo)
            self._cal.substituir_evento(antigo, novo)
            self.atualizar()
        FormularioEvento(self, self._listar_disciplinas(), salvar, evento=antigo)

    def _excluir(self, ev):
        if messagebox.askyesno("Excluir", f"Excluir '{ev.titulo}'?"):
            self._repo.remover_evento(ev)
            self._cal.remover_evento(ev)
            self.atualizar()