# Desenvolvimento e Automação: Sistema Acadêmico

Solução acadêmica com **back-end em Node.js** (API REST de alunos, disciplinas e notas) e **scripts Python** para processamento de dados e automação de tarefas repetitivas, integrados entre si.

**Stack:** Node.js · Express · Python · pandas · Matplotlib · pytest · node:test

## O que o projeto faz

| Componente | Função |
|---|---|
| `api/` (Node.js) | API REST com CRUD de alunos e disciplinas, lançamento de notas, validação de entrada e **boletim** com média ponderada e situação (Aprovado / Recuperação / Reprovado) |
| `python/processar_notas.py` | Lê um CSV de notas, valida, calcula médias ponderadas, estatísticas por disciplina (média, mediana, desvio, taxa de aprovação) e gera relatórios CSV/JSON e gráficos |
| `python/sincronizar_api.py` | Automação que envia alunos, disciplinas e notas de um CSV para a API, de forma idempotente |
| `python/organizar_arquivos.py` | Organiza uma pasta em subpastas por tipo de arquivo, com modo de simulação e sem sobrescrever |
| `python/gerar_dados_exemplo.py` | Gera dados **fictícios** (semente fixa) para demonstração |

```
CSV de notas ──► sincronizar_api.py ──► API Node.js (/alunos, /disciplinas, /notas, /boletim)
      │
      └────────► processar_notas.py ──► relatórios CSV/JSON + gráficos
```

## Estrutura

```
sistema-academico/
├── api/
│   ├── src/
│   │   ├── server.js        # inicialização (porta e arquivo de dados por variável de ambiente)
│   │   ├── app.js           # rotas Express e tratamento de erros
│   │   ├── validators.js    # validação de entrada
│   │   ├── boletim.js       # regras de negócio puras (média ponderada, situação)
│   │   └── store.js         # persistência em JSON com escrita atômica
│   └── test/api.test.js     # testes (node:test + fetch)
├── python/
│   ├── processar_notas.py
│   ├── sincronizar_api.py
│   ├── organizar_arquivos.py
│   ├── gerar_dados_exemplo.py
│   └── tests/test_scripts.py
└── data/entrada/            # CSV de exemplo
```

## Como executar

Pré-requisitos: Node.js 18+ e Python 3.10+.

```bash
# 1. API
cd api
npm install
npm start                       # http://localhost:3000

# 2. Python (em outro terminal)
cd python
pip install -r requirements.txt
python gerar_dados_exemplo.py                                   # cria data/entrada/notas_exemplo.csv
python sincronizar_api.py ../data/entrada/notas_exemplo.csv     # envia para a API
python processar_notas.py ../data/entrada/notas_exemplo.csv     # relatório em python/saida/
python organizar_arquivos.py ~/Downloads                        # simula; adicione --executar para mover
```

Variáveis da API: `PORT` (padrão 3000) e `DB_FILE` (padrão `api/data/db.json`).

### Testes

```bash
cd api && npm test              # 5 testes
cd python && python -m pytest   # 6 testes
```

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/saude` | verificação de funcionamento |
| GET / POST | `/alunos` | listar / cadastrar (nome, matrícula de 4 a 12 dígitos, e-mail opcional) |
| GET / PUT / DELETE | `/alunos/:id` | consultar / atualizar / remover (remove também as notas) |
| GET | `/alunos/:id/boletim` | boletim com média por disciplina e média geral |
| GET / POST | `/disciplinas` | listar / cadastrar (nome, código único, carga horária) |
| DELETE | `/disciplinas/:id` | remover (remove também as notas) |
| GET | `/notas?alunoId=&disciplinaId=` | listar com filtros |
| POST | `/notas` | lançar nota (0 a 10, peso, avaliação) |
| DELETE | `/notas/:id` | remover |

Exemplo:

```bash
curl -X POST localhost:3000/alunos -H "Content-Type: application/json" \
     -d '{"nome":"Ana Lima","matricula":"20240001"}'
curl localhost:3000/alunos/1/boletim
```

Códigos de resposta: `201` criado, `400` validação, `404` não encontrado, `409` conflito (matrícula, código de disciplina ou nota duplicada).

## Decisões técnicas

- **Regras de negócio isoladas** em `boletim.js` (funções puras), testáveis sem subir o servidor.
- **Persistência atrás de uma interface** (`Store`): hoje um arquivo JSON com escrita atômica (grava em arquivo temporário e renomeia); pode ser trocada por SQLite ou MongoDB sem mexer nas rotas.
- **Idempotência:** matrícula, código de disciplina e a tripla (aluno, disciplina, avaliação) são únicos, então rodar a sincronização duas vezes não duplica dados.
- **Validação nas duas pontas:** a API valida a entrada; o script Python descarta linhas inválidas e duplicadas e informa quantas foram removidas.
- **Automação segura:** `organizar_arquivos.py` só simula por padrão e nunca sobrescreve arquivos (`arquivo (1).txt`).
- **Critérios de aprovação:** média ≥ 7 aprova, entre 5 e 7 recuperação, abaixo de 5 reprova (constantes alteráveis).
- **Consistência verificada:** a média de um aluno calculada pela API e a calculada pelo pandas coincidiram nos dados de exemplo.

## Limitações e próximos passos

- Sem autenticação nem controle de perfis (aluno, professor).
- O arquivo JSON não suporta acesso concorrente intenso; para uso real, trocar por um banco de dados.
- Os dados de exemplo são fictícios.
- Ideias: autenticação JWT, banco SQLite/PostgreSQL, documentação OpenAPI, agendamento da sincronização e envio do relatório por e-mail.
