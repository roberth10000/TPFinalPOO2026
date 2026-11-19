
import sqlite3
from contextlib import closing
from sessaoestudo import SessaoEstudo

class RepositorioSessoes:

    def __init__(self, caminho_banco):
        self._caminho = caminho_banco
        self._criar_tabela()

    def _conn(self):
        conexao = sqlite3.connect(self._caminho)
        conexao.row_factory = sqlite3.Row
        return conexao

    def _criar_tabela(self):
        with closing(self._conn()) as conexao:
            conexao.execute("""
                CREATE TABLE IF NOT EXISTS sessoes_estudo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    avaliacao_id INTEGER NOT NULL,
                    conteudo TEXT NOT NULL,
                    data TEXT NOT NULL,
                    horario_inicio TEXT NOT NULL,
                    horario_fim TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Pendente',
                    tempo_estudado REAL NOT NULL DEFAULT 0
                )
            """)
            conexao.commit()

    def salvar_sessao(self, sessao, avaliacao_id):

        with closing(self._conn()) as conexao:

            cursor = conexao.execute("""
                INSERT INTO sessoes_estudo (
                    avaliacao_id,
                    conteudo,
                    data,
                    horario_inicio,
                    horario_fim,
                    status,
                    tempo_estudado
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                avaliacao_id,
                sessao.conteudo,
                sessao.data,
                sessao.horario_inicio,
                sessao.horario_fim,
                sessao.status,
                sessao.tempo_estudado
            ))

            conexao.commit()

            return cursor.lastrowid


    def listar_sessoes(self, avaliacao_id):

        with closing(self._conn()) as conexao:
            linhas = conexao.execute("""
                SELECT *
                FROM sessoes_estudo
                WHERE avaliacao_id = ?
                ORDER BY id
            """, (avaliacao_id,)).fetchall()

        sessoes = []

        for linha in linhas:

            sessao = SessaoEstudo(
                conteudo=linha["conteudo"],
                data=linha["data"],
                horario_inicio=linha["horario_inicio"],
                horario_fim=linha["horario_fim"],
                status=linha["status"],
                tempo_estudado=linha["tempo_estudado"]
            )

            sessao.id = linha["id"]
            sessoes.append(sessao)

        return sessoes


    def atualizar_sessao(self, sessao):

        with closing(self._conn()) as conexao:

            
            conexao.execute("""
                UPDATE sessoes_estudo
                SET horario_inicio = ?,
                    horario_fim = ?,
                    status = ?,
                    tempo_estudado = ?
                WHERE id = ?
            """, (
                sessao.horario_inicio,
                sessao.horario_fim,
                sessao.status,
                sessao.tempo_estudado,
                sessao.id
            
            ))

            conexao.commit()

    def remover_sessoes_da_avaliacao(self, avaliacao_id):

        with closing(self._conn()) as conexao:
            conexao.execute("""
                DELETE FROM sessoes_estudo
                WHERE avaliacao_id = ?
            """, (avaliacao_id,))

            conexao.commit()


    def remover_sessoes_das_avaliacoes(self, avaliacoes_ids):

        if not avaliacoes_ids:
            return

        with closing(self._conn()) as conexao:

            for avaliacao_id in avaliacoes_ids:
                conexao.execute("""
                    DELETE FROM sessoes_estudo
                    WHERE avaliacao_id = ?
                """, (avaliacao_id,))

            conexao.commit()

    def pausar_sessoes_interrompidas(self):

        with closing(self._conn()) as conexao:
            conexao.execute("""
                UPDATE sessoes_estudo
                SET status = 'Pausada'
                WHERE status = 'Em andamento'
            """)

            conexao.commit()

    def verificar_conflito_sessao(self, sessao, novo_inicio, novo_fim):

        with closing(self._conn()) as conexao:

            conflito = conexao.execute("""
                SELECT id, conteudo, horario_inicio, horario_fim
                FROM sessoes_estudo
                WHERE data = ?
                  AND id != ?
                  AND status != 'Concluída'
                  AND horario_inicio < ?
                  AND horario_fim > ?
                LIMIT 1
            """, (
                sessao.data,
                sessao.id,
                novo_fim,
                novo_inicio
            )).fetchone()

        return conflito is not None
