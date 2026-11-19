
# OrganizaUFMG

Projeto desenvolvido para a disciplina de Programação Orientada a Objetos.

## Sobre o projeto

O OrganizaUFMG é um sistema de organização acadêmica
desenvolvido em Python, com interface gráfica e banco de dados SQLite.

O objetivo é auxiliar estudantes no gerenciamento de
disciplinas, avaliações, compromissos e sessões de estudo.

## Funcionalidades

- Cadastro, edição e exclusão de disciplinas
- Cálculo do NSG
- Calendário de aulas, avaliações e eventos
- Agenda semanal com identificação de horários livres
- Planejamento automático de sessões de estudo
- Verificação de conflitos de horários
- Cronômetro para acompanhamento do tempo estudado
- Registro de sessões concluídas
- Persistência de dados com SQLite

## Tecnologias utilizadas

- Python
- CustomTkinter
- SQLite
- Programação Orientada a Objetos

## Requisitos

- Python 3.14
- Bibliotecas indicadas em requirements.txt

## Como executar

1. Abra o terminal na pasta principal do projeto.

2. Instale as dependências:

   python -m pip install -r requirements.txt

3. Execute o programa:

   python main.py

## Banco de dados

O sistema utiliza o arquivo organizaufmg.db
para armazenar as informações cadastradas.

## Organização do projeto

O código está organizado em classes responsáveis
pelas entidades, regras de negócio, persistência
de dados e interface gráfica.
