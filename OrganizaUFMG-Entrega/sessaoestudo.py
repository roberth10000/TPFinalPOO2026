import time

class SessaoEstudo:
    def __init__(self, conteudo, data, horario_inicio, horario_fim, status="Pendente", tempo_estudado=0):
        self.conteudo = conteudo
        self.data = data
        self.horario_inicio = horario_inicio
        self.horario_fim = horario_fim
        self.status = status
        self.tempo_estudado = tempo_estudado

    def iniciar_cronometro(self):
        #Inicia a contagem do tempo de estudo.
        if not hasattr(self, "_inicio_cronometro") or self._inicio_cronometro is None:
            self._inicio_cronometro = time.monotonic()

    def pausar_cronometro(self):
        #Pausa a contagem do tempo de estudo.
        if hasattr(self, "_inicio_cronometro") and self._inicio_cronometro is not None:
            self.tempo_estudado += time.monotonic() - self._inicio_cronometro
            self._inicio_cronometro = None

    def finalizar_cronometro(self):
        #Finaliza a contagem do tempo de estudo e atualiza o tempo estudado.
        self.pausar_cronometro()

    def marcar_concluida(self):
        #Atualiza o estado da sessão para concluída.
        self.status = "Concluída"

    def alterar_horario(self, novo_horario_inicio, novo_horario_fim):
        #Altera os horários de início e fim da sessão.
        self.horario_inicio = novo_horario_inicio
        self.horario_fim = novo_horario_fim