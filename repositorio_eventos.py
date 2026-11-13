import json
import sqlite3
from contextlib import closing
from datetime import date, time

from evento import Evento
from aula import Aula
from avaliacao import Avaliacao
from trabalho import Trabalho
from atividade import Atividade
from compromisso import Compromisso


class RepositorioEventos:
    def __init__(self, caminho_banco: str):
        self._caminho = caminho_banco
        self._criar_tabelas()

    def _conn(self):
        conn = sqlite3.connect(self._caminho)
        conn.row_factory = sqlite3.Row
        return conn

    def _criar_tabelas(self) -> None:
        with closing(self._conn()) as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS eventos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL,
                    titulo TEXT NOT NULL,
                    data TEXT,
                    horario TEXT,
                    horario_fim TEXT,
                    disciplina_id INTEGER,
                    descricao TEXT,
                    dia_semana INTEGER,
                    local TEXT,
                    conteudos TEXT,
                    dificuldade INTEGER,
                    valor REAL,
                    status TEXT,
                    tipo_tarefa TEXT
                )""")
            c.execute("""
                CREATE TABLE IF NOT EXISTS compromissos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dia_semana INTEGER NOT NULL,
                    inicio TEXT NOT NULL,
                    fim TEXT NOT NULL,
                    descricao TEXT,
                    livre INTEGER NOT NULL DEFAULT 0
                )""")
            c.commit()

    # ---------- eventos ----------
    def salvar_evento(self, ev: Evento) -> None:
        """Insere (id None) ou atualiza (id existente)."""
        dados = {
            "id": ev.id, "tipo": ev.TIPO, "titulo": ev.titulo,
            "data": ev.data.isoformat() if ev.data else None,
            "horario": ev.horario.isoformat(timespec="minutes") if ev.horario else None,
            "horario_fim": None,
            "disciplina_id": getattr(ev.disciplina, "id", None),
            "descricao": ev.descricao,
            "dia_semana": None, "local": None, "conteudos": None,
            "dificuldade": None, "valor": None, "status": None, "tipo_tarefa": None,
        }
        if isinstance(ev, Aula):
            dados.update(dia_semana=ev.dia_semana, local=ev.local,
                         horario_fim=ev.horario_fim.isoformat(timespec="minutes"))
        elif isinstance(ev, Avaliacao):
            dados.update(conteudos=json.dumps(ev.conteudos, ensure_ascii=False),
                         dificuldade=ev.dificuldade, valor=ev.valor)
        elif isinstance(ev, Trabalho):
            dados.update(valor=ev.valor, status=ev.status)
        elif isinstance(ev, Atividade):
            dados.update(tipo_tarefa=ev.tipo_tarefa, status=ev.status)

        colunas = ", ".join(dados)
        marcas = ", ".join(f":{k}" for k in dados)
        with closing(self._conn()) as c:
            cur = c.execute(f"INSERT OR REPLACE INTO eventos ({colunas}) VALUES ({marcas})", dados)
            c.commit()
            if ev.id is None:
                ev.id = cur.lastrowid

    def remover_evento(self, ev: Evento) -> None:
        with closing(self._conn()) as c:
            c.execute("DELETE FROM eventos WHERE id = ?", (ev.id,))
            c.commit()

    def listar_eventos(self, resolver_disciplina) -> list[Evento]:
        """resolver_disciplina: função id -> Disciplina (fornecida pelo gerenciador da Isabel)."""
        eventos: list[Evento] = []
        with closing(self._conn()) as c:
            linhas = c.execute("SELECT * FROM eventos ORDER BY id").fetchall()
        for r in linhas:
            disc = resolver_disciplina(r["disciplina_id"])
            hora = time.fromisoformat(r["horario"]) if r["horario"] else None
            data = date.fromisoformat(r["data"]) if r["data"] else None
            desc = r["descricao"] or ""
            if r["tipo"] == "aula":
                ev = Aula(r["titulo"], disc, r["dia_semana"], hora,
                          time.fromisoformat(r["horario_fim"]), r["local"] or "", desc)
            elif r["tipo"] == "avaliacao":
                ev = Avaliacao(r["titulo"], data, hora, disc,
                               json.loads(r["conteudos"] or "[]"),
                               r["dificuldade"] or 3, r["valor"] or 0.0, desc)
            elif r["tipo"] == "trabalho":
                ev = Trabalho(r["titulo"], data, hora, disc,
                              r["valor"] or 0.0, r["status"] or "pendente", desc)
            else:
                ev = Atividade(r["titulo"], data, hora, disc,
                               r["tipo_tarefa"] or "exercício", r["status"] or "pendente", desc)
            ev.id = r["id"]
            eventos.append(ev)
        return eventos

    # ---------- compromissos ----------
    def salvar_compromisso(self, comp: Compromisso) -> None:
        with closing(self._conn()) as c:
            cur = c.execute(
                "INSERT OR REPLACE INTO compromissos (id, dia_semana, inicio, fim, descricao, livre)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (comp.id, comp.dia_semana,
                 comp.horario_inicio.isoformat(timespec="minutes"),
                 comp.horario_fim.isoformat(timespec="minutes"),
                 comp.descricao, int(comp.livre)))
            c.commit()
            if comp.id is None:
                comp.id = cur.lastrowid

    def remover_compromisso(self, comp: Compromisso) -> None:
        with closing(self._conn()) as c:
            c.execute("DELETE FROM compromissos WHERE id = ?", (comp.id,))
            c.commit()

    def listar_compromissos(self) -> list[Compromisso]:
        with closing(self._conn()) as c:
            linhas = c.execute("SELECT * FROM compromissos ORDER BY id").fetchall()
        res = []
        for r in linhas:
            comp = Compromisso(r["dia_semana"], time.fromisoformat(r["inicio"]),
                               time.fromisoformat(r["fim"]), r["descricao"] or "",
                               bool(r["livre"]))
            comp.id = r["id"]
            res.append(comp)
        return res