'use strict';
const express = require('express');
const { Store } = require('./store');
const { ValidationError, validarAluno, validarDisciplina, validarNota } = require('./validators');
const { gerarBoletim } = require('./boletim');

function createApp(store = new Store(null)) {
  const app = express();
  app.use(express.json());

  const idParam = (req) => {
    const id = Number(req.params.id);
    if (!Number.isInteger(id)) throw new ValidationError('id inválido');
    return id;
  };
  const naoEncontrado = (res, what) => res.status(404).json({ erro: `${what} não encontrado(a)` });

  app.get('/saude', (_req, res) => res.json({ status: 'ok' }));

  // ---------- Alunos ----------
  app.get('/alunos', (_req, res) => res.json(store.list('alunos')));
  app.get('/alunos/:id', (req, res) => {
    const a = store.find('alunos', idParam(req));
    return a ? res.json(a) : naoEncontrado(res, 'Aluno');
  });
  app.post('/alunos', (req, res) => {
    const dados = validarAluno(req.body);
    if (store.list('alunos').some((a) => a.matricula === dados.matricula)) {
      return res.status(409).json({ erro: 'matrícula já cadastrada' });
    }
    return res.status(201).json(store.insert('alunos', dados));
  });
  app.put('/alunos/:id', (req, res) => {
    const id = idParam(req);
    const a = store.update('alunos', id, validarAluno(req.body));
    return a ? res.json(a) : naoEncontrado(res, 'Aluno');
  });
  app.delete('/alunos/:id', (req, res) => {
    const id = idParam(req);
    if (!store.remove('alunos', id)) return naoEncontrado(res, 'Aluno');
    store.data.notas = store.data.notas.filter((n) => n.alunoId !== id); // remove notas órfãs
    store._save();
    return res.status(204).end();
  });
  app.get('/alunos/:id/boletim', (req, res) => {
    const a = store.find('alunos', idParam(req));
    if (!a) return naoEncontrado(res, 'Aluno');
    return res.json(gerarBoletim(a, store.list('disciplinas'), store.list('notas')));
  });

  // ---------- Disciplinas ----------
  app.get('/disciplinas', (_req, res) => res.json(store.list('disciplinas')));
  app.post('/disciplinas', (req, res) => {
    const dados = validarDisciplina(req.body);
    if (store.list('disciplinas').some((d) => d.codigo === dados.codigo)) {
      return res.status(409).json({ erro: 'código já cadastrado' });
    }
    return res.status(201).json(store.insert('disciplinas', dados));
  });
  app.delete('/disciplinas/:id', (req, res) => {
    const id = idParam(req);
    if (!store.remove('disciplinas', id)) return naoEncontrado(res, 'Disciplina');
    store.data.notas = store.data.notas.filter((n) => n.disciplinaId !== id);
    store._save();
    return res.status(204).end();
  });

  // ---------- Notas ----------
  app.get('/notas', (req, res) => {
    let notas = store.list('notas');
    if (req.query.alunoId) notas = notas.filter((n) => n.alunoId === Number(req.query.alunoId));
    if (req.query.disciplinaId) notas = notas.filter((n) => n.disciplinaId === Number(req.query.disciplinaId));
    res.json(notas);
  });
  app.post('/notas', (req, res) => {
    const dados = validarNota(req.body);
    if (!store.find('alunos', dados.alunoId)) return naoEncontrado(res, 'Aluno');
    if (!store.find('disciplinas', dados.disciplinaId)) return naoEncontrado(res, 'Disciplina');
    const duplicada = store.list('notas').some((n) => n.alunoId === dados.alunoId
      && n.disciplinaId === dados.disciplinaId && n.avaliacao === dados.avaliacao);
    if (duplicada) return res.status(409).json({ erro: 'nota já lançada para esta avaliação' });
    return res.status(201).json(store.insert('notas', dados));
  });
  app.delete('/notas/:id', (req, res) =>
    store.remove('notas', idParam(req)) ? res.status(204).end() : naoEncontrado(res, 'Nota'));

  // ---------- Erros ----------
  app.use((err, _req, res, _next) => {
    if (err instanceof ValidationError) return res.status(err.status).json({ erro: err.message });
    if (err.type === 'entity.parse.failed') return res.status(400).json({ erro: 'JSON inválido' });
    console.error(err);
    return res.status(500).json({ erro: 'erro interno' });
  });

  return app;
}

module.exports = { createApp };
