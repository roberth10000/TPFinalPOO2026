import customtkinter as ctk
from tkinter import messagebox

from aula import Aula, NOMES_DIAS
from avaliacao import Avaliacao
from trabalho import Trabalho
from atividade import Atividade
from telas.utils_tela import parse_data, parse_hora, parse_float

TIPOS = ["Aula", "Avaliação", "Trabalho", "Atividade"]


class FormularioEvento(ctk.CTkToplevel):
    """Janela de cadastro/edição. Chama ao_salvar(evento_novo); se lançar ValueError, mostra o erro."""

    def __init__(self, master, disciplinas, ao_salvar, evento=None, data_padrao=None):
        super().__init__(master)
        self.title("Editar evento" if evento else "Novo evento")
        self.geometry("420x560")
        self.transient(master)
        self.after(100, self.grab_set)

        self._ao_salvar = ao_salvar
        self._evento = evento
        self._mapa = {d.nome: d for d in disciplinas}
        if not self._mapa:
            messagebox.showwarning("Sem disciplinas", "Cadastre uma disciplina antes de criar eventos.")
            self.after(150, self.destroy)
            return

        self._campos: dict[str, ctk.CTkEntry] = {}
        corpo = ctk.CTkFrame(self)
        corpo.pack(fill="both", expand=True, padx=12, pady=12)
        corpo.columnconfigure(1, weight=1)

        self._tipo = ctk.StringVar(value=TIPOS[0])
        self._disc = ctk.StringVar(value=next(iter(self._mapa)))
        self._dia = ctk.StringVar(value=NOMES_DIAS[0])

        self._linha(corpo, 0, "Tipo", ctk.CTkOptionMenu(corpo, values=TIPOS, variable=self._tipo,
                                                        command=lambda _: self._mostrar_tipo()))
        self._linha(corpo, 1, "Disciplina", ctk.CTkOptionMenu(corpo, values=list(self._mapa),
                                                              variable=self._disc))
        self._linha(corpo, 2, "Título", self._entry(corpo, "titulo"))
        self._linha(corpo, 3, "Descrição", self._entry(corpo, "descricao"))

        # campos específicos (cada grupo é um frame mostrado/ocultado conforme o tipo)
        self._grupos = {t: ctk.CTkFrame(corpo, fg_color="transparent") for t in TIPOS}
        for g in self._grupos.values():
            g.columnconfigure(1, weight=1)
            g.grid(row=4, column=0, columnspan=2, sticky="ew")

        g = self._grupos["Aula"]
        self._linha(g, 0, "Dia", ctk.CTkOptionMenu(g, values=NOMES_DIAS, variable=self._dia))
        self._linha(g, 1, "Início (HH:MM)", self._entry(g, "inicio"))
        self._linha(g, 2, "Fim (HH:MM)", self._entry(g, "fim"))
        self._linha(g, 3, "Local", self._entry(g, "local"))

        for t in ("Avaliação", "Trabalho", "Atividade"):
            g = self._grupos[t]
            self._linha(g, 0, "Data (dd/mm/aaaa)", self._entry(g, f"data_{t}"))
            self._linha(g, 1, "Horário (opcional)", self._entry(g, f"hora_{t}"))
        g = self._grupos["Avaliação"]
        self._linha(g, 2, "Conteúdos (vírgula)", self._entry(g, "conteudos"))
        self._linha(g, 3, "Dificuldade (1-5)", self._entry(g, "dificuldade"))
        self._linha(g, 4, "Valor", self._entry(g, "valor_Avaliação"))
        self._linha(self._grupos["Trabalho"], 2, "Valor", self._entry(self._grupos["Trabalho"], "valor_Trabalho"))
        self._linha(self._grupos["Atividade"], 2, "Tipo de tarefa", self._entry(self._grupos["Atividade"], "tipo_tarefa"))

        ctk.CTkButton(self, text="Salvar", command=self._salvar).pack(pady=(0, 12))

        self._campos["dificuldade"].insert(0, "3")
        if data_padrao:
            for t in ("Avaliação", "Trabalho", "Atividade"):
                self._campos[f"data_{t}"].insert(0, f"{data_padrao:%d/%m/%Y}")
        if evento:
            self._preencher(evento)
        self._mostrar_tipo()

    # ---------- helpers de layout ----------
    def _entry(self, pai, nome):
        e = ctk.CTkEntry(pai)
        self._campos[nome] = e
        return e

    @staticmethod
    def _linha(pai, linha, rotulo, widget):
        ctk.CTkLabel(pai, text=rotulo, anchor="w").grid(row=linha, column=0, sticky="w", padx=6, pady=4)
        widget.grid(row=linha, column=1, sticky="ew", padx=6, pady=4)

    def _mostrar_tipo(self):
        for nome, g in self._grupos.items():
            g.grid() if nome == self._tipo.get() else g.grid_remove()

    # ---------- edição ----------
    def _preencher(self, ev):
        nome_tipo = {"aula": "Aula", "avaliacao": "Avaliação",
                     "trabalho": "Trabalho", "atividade": "Atividade"}[ev.TIPO]
        self._tipo.set(nome_tipo)
        self._disc.set(ev.disciplina.nome)
        self._campos["titulo"].insert(0, ev.titulo)
        self._campos["descricao"].insert(0, ev.descricao)
        if isinstance(ev, Aula):
            self._dia.set(NOMES_DIAS[ev.dia_semana])
            self._campos["inicio"].insert(0, f"{ev.horario_inicio:%H:%M}")
            self._campos["fim"].insert(0, f"{ev.horario_fim:%H:%M}")
            self._campos["local"].insert(0, ev.local)
        else:
            self._campos[f"data_{nome_tipo}"].delete(0, "end")
            self._campos[f"data_{nome_tipo}"].insert(0, f"{ev.data:%d/%m/%Y}")
            if ev.horario:
                self._campos[f"hora_{nome_tipo}"].insert(0, f"{ev.horario:%H:%M}")
        if isinstance(ev, Avaliacao):
            self._campos["conteudos"].insert(0, ", ".join(ev.conteudos))
            self._campos["dificuldade"].delete(0, "end")
            self._campos["dificuldade"].insert(0, str(ev.dificuldade))
            self._campos["valor_Avaliação"].insert(0, str(ev.valor))
        elif isinstance(ev, Trabalho):
            self._campos["valor_Trabalho"].insert(0, str(ev.valor))
        elif isinstance(ev, Atividade):
            self._campos["tipo_tarefa"].insert(0, ev.tipo_tarefa)
        # o tipo não pode mudar na edição
        self.children  # mantém referência
        for w in self.winfo_children():
            pass

    # ---------- construção do objeto ----------
    def _construir(self):
        tipo = self._tipo.get()
        disc = self._mapa[self._disc.get()]
        titulo = self._campos["titulo"].get()
        desc = self._campos["descricao"].get().strip()

        if tipo == "Aula":
            return Aula(titulo, disc, NOMES_DIAS.index(self._dia.get()),
                        parse_hora(self._campos["inicio"].get()),
                        parse_hora(self._campos["fim"].get()),
                        self._campos["local"].get().strip(), desc)

        data = parse_data(self._campos[f"data_{tipo}"].get())
        txt_hora = self._campos[f"hora_{tipo}"].get().strip()
        hora = parse_hora(txt_hora) if txt_hora else None

        if tipo == "Avaliação":
            conteudos = [c.strip() for c in self._campos["conteudos"].get().split(",") if c.strip()]
            try:
                dif = int(self._campos["dificuldade"].get())
            except ValueError:
                raise ValueError("Dificuldade deve ser um número de 1 a 5.")
            return Avaliacao(titulo, data, hora, disc, conteudos, dif,
                             parse_float(self._campos["valor_Avaliação"].get()), desc)
        if tipo == "Trabalho":
            status = self._evento.status if isinstance(self._evento, Trabalho) else "pendente"
            return Trabalho(titulo, data, hora, disc,
                            parse_float(self._campos["valor_Trabalho"].get()), status, desc)
        status = self._evento.status if isinstance(self._evento, Atividade) else "pendente"
        return Atividade(titulo, data, hora, disc,
                         self._campos["tipo_tarefa"].get().strip() or "exercício", status, desc)

    def _salvar(self):
        try:
            novo = self._construir()
            self._ao_salvar(novo)
        except ValueError as erro:
            messagebox.showerror("Dados inválidos", str(erro), parent=self)
            return
        self.destroy()