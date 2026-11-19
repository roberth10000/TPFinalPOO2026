
import customtkinter as ctk
from tkinter import messagebox
from disciplinas import Disciplina
from repositorio_sessoes import RepositorioSessoes



class TelaDisciplinas(ctk.CTkFrame):

    def __init__(self, master, gerenciador, calendario, agenda, repo_eventos):
        super().__init__(master)

        self.gerenciador = gerenciador
        self.calendario = calendario
        self.agenda = agenda
        self.repo_eventos = repo_eventos

        self.montar_tela()
        self.atualizar()


    def montar_tela(self):

        # Título
        titulo = ctk.CTkLabel(
            self,
            text="Minhas Disciplinas",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        titulo.pack(pady=20)

        # Formulário de cadastro
        formulario = ctk.CTkFrame(self)
        formulario.pack(fill="x", padx=20, pady=10)

        self.campo_nome = ctk.CTkEntry(
            formulario,
            placeholder_text="Nome da disciplina",
            width=250
        )
        self.campo_nome.pack(side="left", padx=10, pady=15)

        self.campo_professor = ctk.CTkEntry(
            formulario,
            placeholder_text="Nome do professor",
            width=250
        )
        self.campo_professor.pack(side="left", padx=10)

        self.campo_nota = ctk.CTkEntry(
            formulario,
            placeholder_text="Nota atual",
            width=120
        )
        self.campo_nota.pack(side="left", padx=10)

        self.botao_cadastrar = ctk.CTkButton(
            formulario,
            text="Cadastrar disciplina",
            command=self.cadastrar_disciplina
        )
        self.botao_cadastrar.pack(side="left", padx=10)

        # Lista de disciplinas
        self.lista_disciplinas = ctk.CTkScrollableFrame(self)
        self.lista_disciplinas.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        # Exibição do NSG
        self.label_nsg = ctk.CTkLabel(
            self,
            text="NSG atual: --",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.label_nsg.pack(pady=20)

    
    def atualizar(self):

        # Limpa a lista antes de atualizar
        for widget in self.lista_disciplinas.winfo_children():
            widget.destroy()

        # Busca as disciplinas no banco de dados
        disciplinas = self.gerenciador.repositorio.listar_disciplinas()

        # Exibe as disciplinas cadastradas
        for disciplina in disciplinas:

            quadro = ctk.CTkFrame(self.lista_disciplinas)
            quadro.pack(fill="x", padx=10, pady=5)

            texto = (
                f"Disciplina: {disciplina.nome}    |    "
                f"Professor: {disciplina.professor}    |    "
                f"Nota atual: {disciplina.nota_atual:.2f}"
            )

            
            ctk.CTkLabel(
                quadro,
                text=texto,
                font=ctk.CTkFont(size=14)
            ).pack(side="left", padx=15, pady=12)

            ctk.CTkButton(
                quadro,
                text="Editar nota",
                width=100,
                command=lambda d=disciplina: self.editar_nota(d)
            ).pack(side="right", padx=15)


            ctk.CTkButton(
                quadro,
                text="Excluir",
                width=80,
                fg_color="#a33",
                command=lambda d=disciplina: self.excluir_disciplina(d)
            ).pack(side="right", padx=5)



        # Calcula e exibe o NSG
        nsg = self.gerenciador.calcular_nsg()

        self.label_nsg.configure(
            text=f"NSG atual: {nsg:.2f}"
        )

    def cadastrar_disciplina(self):

        nome = self.campo_nome.get().strip()
        professor = self.campo_professor.get().strip()
        nota_texto = self.campo_nota.get().strip()

        # Verifica se todos os campos foram preenchidos
        if not nome or not professor or not nota_texto:
            messagebox.showerror(
                "Erro",
                "Preencha todos os campos."
            )
            return

        # Verifica se a nota é um número válido
        try:
            nota = float(nota_texto.replace(",", "."))
        except ValueError:
            messagebox.showerror(
                "Erro",
                "Digite uma nota válida."
            )
            return

        # Verifica se a nota está entre 0 e 100
        if not 0 <= nota <= 100:
            messagebox.showerror(
                "Erro",
                "A nota deve estar entre 0 e 100."
            )
            return

        # Cria e salva a disciplina
        disciplina = Disciplina(nome, professor, nota)

        self.gerenciador.repositorio.salvar_disciplina(disciplina)

        # Limpa os campos
        self.campo_nome.delete(0, "end")
        self.campo_professor.delete(0, "end")
        self.campo_nota.delete(0, "end")

        # Atualiza a lista e o NSG
        self.atualizar()

        messagebox.showinfo(
            "Sucesso",
            "Disciplina cadastrada com sucesso!"
        )

    def editar_nota(self, disciplina):

        janela = ctk.CTkInputDialog(
            text=f"Digite a nova nota de {disciplina.nome}:",
            title="Editar nota"
        )

        nova_nota = janela.get_input()

        # Usuário cancelou a operação
        if nova_nota is None:
            return

        try:
            nota = float(nova_nota.replace(",", "."))

            if not 0 <= nota <= 100:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Erro",
                "Digite uma nota válida entre 0 e 100."
            )
            return

        # Atualiza a nota
        disciplina.nota_atual = nota

        # Salva a alteração no banco
        self.gerenciador.repositorio.salvar_disciplina(
            disciplina
        )

        # Atualiza a interface e o NSG
        self.atualizar()

        messagebox.showinfo(
            "Sucesso",
            "Nota atualizada com sucesso!"
        )

    
    
    
    def excluir_disciplina(self, disciplina):

        confirmar = messagebox.askyesno(
            "Excluir disciplina",
            f"Deseja realmente excluir {disciplina.nome}?\n\n"
            "Todas as aulas, avaliações, trabalhos e atividades "
            "vinculadas a essa disciplina também serão excluídas.\n\n"
            "Esta ação não poderá ser desfeita."
        )

        if not confirmar:
            return

        # Identifica os eventos da disciplina no calendário
        
        eventos_vinculados = [
            evento
            for evento in self.calendario.consultar_eventos()
            if evento.disciplina is not None
            and evento.disciplina.id == disciplina.id
        ]


        # Identifica as avaliações da disciplina
        avaliacoes_ids = [
            evento.id
            for evento in eventos_vinculados
            if evento.TIPO == "avaliacao"
        ]

        # Remove as sessões dessas avaliações
        repo_sessoes = RepositorioSessoes(
            "organizaufmg.db"
        )

        repo_sessoes.remover_sessoes_das_avaliacoes(
            avaliacoes_ids
        )



        # Remove os eventos do banco de dados
        self.repo_eventos.remover_eventos_da_disciplina(
            disciplina.id
        )

        # Remove os eventos do calendário em memória
        for evento in eventos_vinculados:
            self.calendario.remover_evento(evento)

        # Atualiza as aulas da agenda semanal
        self.agenda.sincronizar_aulas(self.calendario.aulas())

        # Remove a disciplina do banco de dados
        self.gerenciador.repositorio.remover_disciplina(
            disciplina.id
        )

        # Atualiza a lista e o NSG
        self.atualizar()

        messagebox.showinfo(
            "Sucesso",
            "Disciplina e eventos vinculados excluídos com sucesso!"
        )



