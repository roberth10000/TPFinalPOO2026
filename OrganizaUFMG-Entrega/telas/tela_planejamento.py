
import customtkinter as ctk
from planejamento import PlanejamentoEstudos
from tkinter import messagebox
from repositorio_sessoes import RepositorioSessoes
from datetime import datetime
from types import SimpleNamespace


class TelaPlanejamento(ctk.CTkFrame):

    
    def __init__(self, master, calendario, agenda, repositorio_sessoes):
        super().__init__(master)

        self.calendario = calendario
        self.agenda = agenda
        self.repositorio_sessoes = repositorio_sessoes 
        self.avaliacoes = {}
        self.planejamento_atual = None

        self.montar_tela()
        self.atualizar_avaliacoes()



    def montar_tela(self):

        # Título
        titulo = ctk.CTkLabel(
            self,
            text="Planejamento de Estudos",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        titulo.pack(pady=20)

        # Formulário para gerar planejamento
        formulario = ctk.CTkFrame(self)
        formulario.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            formulario,
            text="Avaliação:"
        ).pack(side="left", padx=10)

        self.campo_avaliacao = ctk.CTkOptionMenu(
            formulario,
            values=["Selecione uma avaliação"],
            width=250
        )
        self.campo_avaliacao.pack(side="left", padx=10, pady=15)

        self.botao_gerar = ctk.CTkButton(
            formulario,
            text="Gerar planejamento",
            command=self.gerar_planejamento
        )
        
        self.botao_gerar.pack(side="left", padx=10)

        # Área para exibir as sessões de estudo
        self.lista_sessoes = ctk.CTkScrollableFrame(self)
        self.lista_sessoes.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        # Informações do planejamento
        self.label_resumo = ctk.CTkLabel(
            self,
            text="Nenhum planejamento gerado.",
            font=ctk.CTkFont(size=16)
        )
        self.label_resumo.pack(pady=20)

    def atualizar_avaliacoes(self):

        # Busca somente os eventos do tipo avaliação
        avaliacoes = self.calendario.consultar_eventos(
            tipo="avaliacao"
        )

        # Cria as opções do menu
        self.avaliacoes = {}

        for avaliacao in avaliacoes:
            nome = (
                f"{avaliacao.titulo} - "
                f"{avaliacao.disciplina.nome} - "
                f"{avaliacao.data:%d/%m/%Y}"
            )

            self.avaliacoes[nome] = avaliacao

        if self.avaliacoes:
            opcoes = list(self.avaliacoes.keys())
        else:
            opcoes = ["Nenhuma avaliação cadastrada"]

        self.campo_avaliacao.configure(values=opcoes)
        self.campo_avaliacao.set(opcoes[0])
    
    def gerar_planejamento(self):

        # Identifica a avaliação selecionada
        nome = self.campo_avaliacao.get()
        avaliacao = self.avaliacoes.get(nome)

        if avaliacao is None:
            messagebox.showwarning(
                "Atenção",
                "Selecione uma avaliação cadastrada."
            )
            return

        # Obtém os dados da avaliação
        conteudos = avaliacao.conteudos
        dificuldade = avaliacao.dificuldade

        if not conteudos:
            messagebox.showwarning(
                "Atenção",
                "Esta avaliação não possui conteúdos cadastrados."
            )
            return

        # Utiliza a classe
        
        # Consulta se já existem sessões salvas
        sessoes_salvas = self.repositorio_sessoes.listar_sessoes(
            avaliacao.id
        )

        # Cria o objeto de planejamento
        self.planejamento_atual = PlanejamentoEstudos(
            avaliacao=avaliacao,
            conteudos=conteudos,
            dificuldade=dificuldade
        )

        if sessoes_salvas:
            # Recupera o planejamento existente
            self.planejamento_atual.sessoes = sessoes_salvas
            sessoes = sessoes_salvas

        else:
            # Gera um novo planejamento
            resultado = self.planejamento_atual.gerar_planejamento(
                agenda=self.agenda
            )

            sessoes = resultado["sessoes"]

            # Salva as sessões geradas no SQLite
            for sessao in sessoes:
                sessao.id = self.repositorio_sessoes.salvar_sessao(
                    sessao,
                    avaliacao.id
                )


        # Limpa a lista anterior
        for widget in self.lista_sessoes.winfo_children():
            widget.destroy()

        # Exibe as sessões geradas
        
        # Exibe as sessões geradas
        for numero, sessao in enumerate(sessoes, start=1):

            quadro = ctk.CTkFrame(self.lista_sessoes)
            quadro.pack(fill="x", padx=10, pady=6)

            titulo = ctk.CTkLabel(
                quadro,
                text=f"Sessão {numero} — {sessao.conteudo}",
                font=ctk.CTkFont(size=15, weight="bold")
            )
            titulo.pack(anchor="w", padx=15, pady=(10, 3))

            horario = ctk.CTkLabel(
                quadro,
                text=(
                    f"Data: {sessao.data}  |  "
                    f"Horário: {sessao.horario_inicio} "
                    f"às {sessao.horario_fim}"
                ),
                font=ctk.CTkFont(size=13)
            )
            horario.pack(anchor="w", padx=15, pady=(0, 10))
            sessao.label_horario = horario


            label_status = ctk.CTkLabel(
                quadro,
                text=f"Status: {sessao.status}",
                font=ctk.CTkFont(size=13)
            )

            label_status.pack(
                anchor="w",
                padx=15,
                pady=(0, 10)
            )

            # Guarda o componente para atualizar depois
            sessao.label_status = label_status


            segundos = int(sessao.tempo_estudado)
            horas = segundos // 3600
            minutos = (segundos % 3600) // 60
            segundos_restantes = segundos % 60

            label_tempo = ctk.CTkLabel(
                quadro,
                text=(
                    f"Tempo estudado: "
                    f"{horas:02d}:{minutos:02d}:{segundos_restantes:02d}"
                ),
                font=ctk.CTkFont(size=13)
            )

            label_tempo.pack(
                anchor="w",
                padx=15,
                pady=(0, 10)
            )

            sessao.label_tempo = label_tempo


            botao_iniciar = ctk.CTkButton(
                quadro,
                text="Iniciar sessão",
                width=140,
                command=lambda s=sessao: self.iniciar_sessao(s)
            )
            botao_iniciar.pack(
                anchor="w",
                padx=15,
                pady=(0, 12)
            )

        
            botao_pausar = ctk.CTkButton(
                quadro,
                text="Pausar sessão",
                width=140,
                fg_color="#666666",
                command=lambda s=sessao: self.pausar_sessao(s)
            )

            botao_pausar.pack(
                anchor="w",
                padx=15,
                pady=(0, 12)
            )

            botao_concluir = ctk.CTkButton(
                quadro,
                text="Concluir sessão",
                width=140,
                fg_color="#238636",
                command=lambda s=sessao: self.concluir_sessao(s)
            )

            botao_concluir.pack(
                anchor="w",
                padx=15,
                pady=(0, 12)
            )

            botao_alterar = ctk.CTkButton(
                quadro,
                text="Alterar horário",
                width=140,
                fg_color="#555555",
                command=lambda s=sessao: self.alterar_horario_sessao(s)
            )

            botao_alterar.pack(
                anchor="w",
                padx=15,
                pady=(0, 12)
            )

        self.label_resumo.configure(
            text=f"Total de sessões geradas: {len(sessoes)}"
        )

        if not sessoes:
            messagebox.showinfo(
                "Planejamento",
                "Nenhuma sessão foi gerada. Verifique os horários "
                "livres da agenda e a data da avaliação."
            )

    def iniciar_sessao(self, sessao):

        if sessao.status == "Concluída":
            messagebox.showinfo(
                "Sessão concluída",
                "Esta sessão já foi concluída."
            )
            return

        sessao.iniciar_cronometro()
        sessao.status = "Em andamento"
        
        self.repositorio_sessoes.atualizar_sessao(sessao)

        sessao.label_status.configure(
            text=f"Status: {sessao.status}"
        )


        messagebox.showinfo(
            "Cronômetro iniciado",
            f"Sessão iniciada!\n\n"
            f"Conteúdo: {sessao.conteudo}\n\n"
            "O tempo de estudo está sendo contabilizado."
        )


    def pausar_sessao(self, sessao):

        if sessao.status != "Em andamento":
            messagebox.showwarning(
                "Atenção",
                "Esta sessão não está em andamento."
            )
            return

        sessao.pausar_cronometro()
        self.atualizar_tempo_sessao(sessao)
        sessao.status = "Pausada"
        self.repositorio_sessoes.atualizar_sessao(sessao)
        sessao.label_status.configure(
            text=f"Status: {sessao.status}"
        )

        segundos = int(sessao.tempo_estudado)

        minutos = segundos // 60
        segundos_restantes = segundos % 60

        messagebox.showinfo(
            "Sessão pausada",
            f"Sessão pausada com sucesso!\n\n"
            f"Conteúdo: {sessao.conteudo}\n"
            f"Tempo estudado: "
            f"{minutos} min e {segundos_restantes} s"
        )

    def concluir_sessao(self, sessao):

        if sessao.status == "Concluída":
            messagebox.showinfo(
                "Sessão concluída",
                "Esta sessão já foi concluída."
            )
            return

        # Finaliza a contagem do tempo
        sessao.finalizar_cronometro()
        self.atualizar_tempo_sessao(sessao)

        # Atualiza o status da sessão
        sessao.marcar_concluida()
        self.repositorio_sessoes.atualizar_sessao(sessao)

        sessao.label_status.configure(
            text=f"Status: {sessao.status}"
        )


        # Calcula o tempo estudado
        segundos = int(sessao.tempo_estudado)

        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segundos_restantes = segundos % 60

        messagebox.showinfo(
            "Sessão concluída",
            f"Sessão concluída com sucesso!\n\n"
            f"Conteúdo: {sessao.conteudo}\n"
            f"Tempo estudado: "
            f"{horas}h {minutos}min {segundos_restantes}s"
        )


    def atualizar_tempo_sessao(self, sessao):

        segundos = int(sessao.tempo_estudado)

        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segundos_restantes = segundos % 60

        sessao.label_tempo.configure(
            text=(
                f"Tempo estudado: "
                f"{horas:02d}:{minutos:02d}:{segundos_restantes:02d}"
            )
        )

    def alterar_horario_sessao(self, sessao):

        if sessao.status == "Concluída":
            messagebox.showwarning(
                "Atenção",
                "Não é possível alterar uma sessão concluída."
            )
            return

        janela = ctk.CTkInputDialog(
            text="Digite o novo horário de início (HH:MM):",
            title="Alterar horário"
        )

        novo_inicio = janela.get_input()

        if novo_inicio is None:
            return

        janela = ctk.CTkInputDialog(
            text="Digite o novo horário de fim (HH:MM):",
            title="Alterar horário"
        )

        novo_fim = janela.get_input()

        if novo_fim is None:
            return

        # Valida os horários informados
        from datetime import datetime

        try:
            inicio = datetime.strptime(novo_inicio, "%H:%M")
            fim = datetime.strptime(novo_fim, "%H:%M")

            if fim <= inicio:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Horário inválido",
                "Informe horários válidos no formato HH:MM. "
                "O horário final deve ser posterior ao inicial."
            )
            return

       
        # Converte a data e os horários da sessão
        data_sessao = datetime.strptime(
            sessao.data, "%d/%m/%Y"
        ).date()

        # Cria um objeto temporário para consultar conflitos
        horario_proposto = SimpleNamespace(
            dia_semana=data_sessao.weekday(),
            horario_inicio=inicio.time(),
            horario_fim=fim.time()
        )

        # Atualiza as aulas da agenda antes da verificação
        self.agenda.sincronizar_aulas(
            self.calendario.aulas()
        )

        # Verifica conflitos com aulas e compromissos
        if self.agenda.verificar_conflito(horario_proposto):
            messagebox.showwarning(
                "Conflito de horário",
                "O horário escolhido coincide com uma aula "
                "ou outro compromisso cadastrado.\n\n"
                "Escolha outro horário."
            )
            return

       
        # Verifica conflitos com outras sessões de estudo
        sessoes = self.planejamento_atual.sessoes

        for outra_sessao in sessoes:

            # Não compara a sessão com ela mesma
            if outra_sessao is sessao:
                continue

            # Considera apenas sessões da mesma data
            if outra_sessao.data != sessao.data:
                continue

            inicio_outra = datetime.strptime(
                outra_sessao.horario_inicio, "%H:%M"
            )

            fim_outra = datetime.strptime(
                outra_sessao.horario_fim, "%H:%M"
            )

            # Verifica se os horários se sobrepõem
            if inicio < fim_outra and inicio_outra < fim:

                messagebox.showwarning(
                    "Conflito entre sessões",
                    "Já existe outra sessão de estudo "
                    "programada para esse horário.\n\n"
                    "Escolha outro horário."
                )
                return


        # Verifica conflitos com sessões de outras avaliações
        if self.repositorio_sessoes.verificar_conflito_sessao(
            sessao, novo_inicio, novo_fim
        ):
            messagebox.showwarning(
                "Conflito entre planejamentos",
                "Já existe uma sessão de estudo de outra avaliação "
                "programada para esse dia e horário.\n\n"
                "Escolha outro horário."
            )
            return

        
        sessao.alterar_horario(novo_inicio, novo_fim)

        # Salva a alteração no SQLite
        self.repositorio_sessoes.atualizar_sessao(sessao)

        # Atualiza a informação na tela
        sessao.label_horario.configure(
            text=(
                f"Data: {sessao.data}  |  "
                f"Horário: {sessao.horario_inicio} "
                f"às {sessao.horario_fim}"
            )
        )

        messagebox.showinfo(
            "Sucesso",
            "Horário da sessão alterado com sucesso!"
        )


