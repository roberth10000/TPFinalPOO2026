
import sqlite3
from contextlib import closing

from disciplinas import Disciplina


class RepositorioDisciplinas:

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
                CREATE TABLE IF NOT EXISTS disciplinas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    professor TEXT NOT NULL,
                    nota_atual REAL NOT NULL DEFAULT 0
                )
            """)
            conexao.commit()

    def salvar_disciplina(self, disciplina):
        with closing(self._conn()) as conexao:

            if disciplina.id is None:
                cursor = conexao.execute("""
                    INSERT INTO disciplinas
                    (nome, professor, nota_atual)
                    VALUES (?, ?, ?)
                """, (
                    disciplina.nome,
                    disciplina.professor,
                    disciplina.nota_atual
                ))

                disciplina.id = cursor.lastrowid

            else:
                conexao.execute("""
                    UPDATE disciplinas
                    SET nome = ?, professor = ?, nota_atual = ?
                    WHERE id = ?
                """, (
                    disciplina.nome,
                    disciplina.professor,
                    disciplina.nota_atual,
                    disciplina.id
                ))

            conexao.commit()

    def buscar_disciplina(self, id):
        with closing(self._conn()) as conexao:
            linha = conexao.execute("""
                SELECT * FROM disciplinas
                WHERE id = ?
            """, (id,)).fetchone()

        if linha is None:
            return None

        return Disciplina(
            linha["nome"],
            linha["professor"],
            linha["nota_atual"],
            linha["id"]
        )

    def listar_disciplinas(self):
        with closing(self._conn()) as conexao:
            linhas = conexao.execute(
                "SELECT * FROM disciplinas ORDER BY id"
            ).fetchall()

        disciplinas = []

        for linha in linhas:
            disciplina = Disciplina(
                linha["nome"],
                linha["professor"],
                linha["nota_atual"],
                linha["id"]
            )
            disciplinas.append(disciplina)

        return disciplinas

    def remover_disciplina(self, id):
        with closing(self._conn()) as conexao:
            conexao.execute(
                "DELETE FROM disciplinas WHERE id = ?",
                (id,)
            )
            conexao.commit()
