from datetime import datetime, timedelta, date
from sessaoestudo import SessaoEstudo

class PlanejamentoEstudos:
    def __init__(self, avaliacao, conteudos, dificuldade, sessoes=None):
        self.avaliacao = avaliacao
        self.conteudos = conteudos if isinstance(conteudos, list) else [conteudos]
        self.dificuldade = dificuldade
        self.sessoes = sessoes if sessoes is not None else []
        self.etapas = []

    def dividir_conteudos_em_etapas(self):

        # Divide os conteúdos em etapas de aprendizagem (Teoria, Prática e Revisão)
        # O número de etapas e a duração de cada uma dependem da dificuldade do conteúdo.
        # Dificil: 3 etapas (Teoria, Prática, Revisão) com 1 hora cada
        # Médio: 2 etapas (Teoria, Prática/Revisão) com 1 hora cada
        # Fácil: 1 etapa (Estudo e Revisão) com 1 hora

        self.etapas = []
        nivel = str(self.dificuldade).strip().lower()

        if nivel in ["alta", "difícil", "dificil", "3"]:
            fator_horas = 3
        elif nivel in ["média", "media", "2"]:
            fator_horas = 2
        else:
            fator_horas = 1

        for conteudo in self.conteudos:
            if fator_horas == 3:
                self.etapas.append({"descricao": f"Teoria: {conteudo}", "horas": 1.0})
                self.etapas.append({"descricao": f"Exercícios: {conteudo}", "horas": 1.0})
                self.etapas.append({"descricao": f"Revisão: {conteudo}", "horas": 1.0})
            elif fator_horas == 2:
                self.etapas.append({"descricao": f"Estudo Teórico: {conteudo}", "horas": 1.0})
                self.etapas.append({"descricao": f"Prática e Revisão: {conteudo}", "horas": 1.0})
            else:
                self.etapas.append({"descricao": f"Estudo e Revisão: {conteudo}", "horas": 1.0})

        return self.etapas

    
    
    def _obter_data_limite(self):

        # Obtém a data cadastrada para a avaliação
        data_raw = getattr(self.avaliacao, "data", None)

        if data_raw is None and isinstance(self.avaliacao, dict):
            data_raw = self.avaliacao.get("data")

        # Quando a data já é um objeto datetime
        if isinstance(data_raw, datetime):
            return data_raw.date()

        # Quando a data é um objeto date
        if isinstance(data_raw, date):
            return data_raw

        # Quando a data está armazenada como texto
        if isinstance(data_raw, str):
            for formato in ("%d/%m/%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(
                        data_raw, formato
                    ).date()
                except ValueError:
                    continue

        raise ValueError("Data da avaliação inválida.")


        raise ValueError("Data da avaliação inválida.")


    
    def _extrair_horarios_livres(self, agenda):

        # Obtém os horários livres da agenda semanal
        if agenda is None:
            return []

        if hasattr(agenda, "identificar_disponibilidade"):
            disponiveis = agenda.identificar_disponibilidade()

        elif hasattr(agenda, "horarios_livres"):
            disponiveis = agenda.horarios_livres

        elif isinstance(agenda, (list, dict)):
            disponiveis = agenda

        else:
            return []

        # Converte o dicionário da agenda para uma lista
        if isinstance(disponiveis, dict):

            horarios = []

            for dia_semana, intervalos in disponiveis.items():

                for inicio, fim in intervalos:

                    horarios.append({
                        "dia_semana": int(dia_semana),
                        "inicio": inicio,
                        "fim": fim
                    })

            return horarios

        return disponiveis or []


    def distribuir_sessoes(self, agenda=None, data_inicio=None):

        # Distribui as etapas de estudo nos horários disponíveis da agenda
        # até a véspera da data da avaliação, criando objetos SessaoEstudo.

        if not self.etapas:
            self.dividir_conteudos_em_etapas()

        self.sessoes = []
        hoje = data_inicio if data_inicio else datetime.now().date()
        data_prova = self._obter_data_limite()
        horarios_livres = self._extrair_horarios_livres(agenda)

        if not horarios_livres:
            return self.sessoes

        dias_semana_map = {
            "segunda": 0, "segunda-feira": 0, "seg": 0,
            "terça": 1, "terca": 1, "terça-feira": 1, "ter": 1,
            "quarta": 2, "quarta-feira": 2, "qua": 2,
            "quinta": 3, "quinta-feira": 3, "qui": 3,
            "sexta": 4, "sexta-feira": 4, "sex": 4,
            "sábado": 5, "sabado": 5, "sab": 5,
            "domingo": 6, "dom": 6
        }

        etapa_idx = 0
        dia_atual = hoje

        while dia_atual < data_prova and etapa_idx < len(self.etapas):
            dia_semana_atual = dia_atual.weekday()

            for slot in horarios_livres:
                if etapa_idx >= len(self.etapas):
                    break

                dia_slot = slot.get("dia_semana") if isinstance(slot, dict) else getattr(slot, "dia_semana", None)
                inicio_slot = slot.get("inicio") if isinstance(slot, dict) else getattr(slot, "horario_inicio", getattr(slot, "inicio", "18:00"))
                fim_slot = slot.get("fim") if isinstance(slot, dict) else getattr(slot, "horario_fim", getattr(slot, "fim", "19:00"))

                if isinstance(dia_slot, str):
                    dia_slot = dias_semana_map.get(dia_slot.strip().lower())

                if dia_slot == dia_semana_atual:
                    etapa = self.etapas[etapa_idx]
                    data_formatada = dia_atual.strftime("%d/%m/%Y")

                    
                    # Calcula o horário final conforme a duração da etapa
                    from datetime import time

                    def converter_hora(valor):
                        if isinstance(valor, time):
                            return datetime.combine(dia_atual, valor)
                        return datetime.combine(
                            dia_atual,
                            datetime.strptime(valor, "%H:%M").time()
                        )

                    inicio = converter_hora(inicio_slot)
                    fim_disponivel = converter_hora(fim_slot)

                    duracao = timedelta(hours=etapa["horas"])
                    fim_sessao = inicio + duracao

                    # Só agenda se houver tempo suficiente
                    if fim_sessao <= fim_disponivel:
                        nova_sessao = SessaoEstudo(
                            conteudo=etapa["descricao"],
                            data=data_formatada,
                            horario_inicio=inicio.strftime("%H:%M"),
                            horario_fim=fim_sessao.strftime("%H:%M")
                        )

                        self.sessoes.append(nova_sessao)
                        etapa_idx += 1

                        # Impede a criação de outra sessão no mesmo dia
                        break


            dia_atual += timedelta(days=1)

        return self.sessoes

    def gerar_planejamento(self, agenda=None, data_inicio=None):

        # Orquestra a divisão de conteúdos e a distribuição das sessões.

        self.dividir_conteudos_em_etapas()
        self.distribuir_sessoes(agenda=agenda, data_inicio=data_inicio)
        return self.consultar_planejamento()

    def alterar_sessao(self, sessao, novos_dados):

        # Altera os detalhes de uma sessão de estudo específica.

        alvo = None
        if isinstance(sessao, int) and 0 <= sessao < len(self.sessoes):
            alvo = self.sessoes[sessao]
        elif sessao in self.sessoes:
            alvo = sessao

        if alvo is None:
            raise ValueError("Sessão de estudo não encontrada no planejamento.")

        if "conteudo" in novos_dados:
            alvo.conteudo = novos_dados["conteudo"]
        if "data" in novos_dados:
            alvo.data = novos_dados["data"]
        if "horario_inicio" in novos_dados and "horario_fim" in novos_dados:
            alvo.alterar_horario(novos_dados["horario_inicio"], novos_dados["horario_fim"])
        else:
            if "horario_inicio" in novos_dados:
                alvo.horario_inicio = novos_dados["horario_inicio"]
            if "horario_fim" in novos_dados:
                alvo.horario_fim = novos_dados["horario_fim"]
        if "status" in novos_dados:
            if novos_dados["status"] == "Concluída":
                alvo.marcar_concluida()
            else:
                alvo.status = novos_dados["status"]

        return alvo

    def consultar_planejamento(self):
        
        # Retorna os detalhes completos do planejamento de estudos.

        return {
            "avaliacao": self.avaliacao,
            "conteudos": self.conteudos,
            "dificuldade": self.dificuldade,
            "etapas": self.etapas,
            "sessoes": self.sessoes
        }