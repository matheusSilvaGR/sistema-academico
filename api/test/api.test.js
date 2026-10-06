'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { createApp } = require('../src/app');
const { mediaPonderada, situacao } = require('../src/boletim');

async function iniciar() {
  const server = createApp().listen(0);
  await new Promise((r) => server.once('listening', r));
  const base = `http://127.0.0.1:${server.address().port}`;
  const req = async (method, url, body) => {
    const res = await fetch(base + url, {
      method,
      headers: { 'content-type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
    });
    const text = await res.text();
    return { status: res.status, body: text ? JSON.parse(text) : null };
  };
  return { req, close: () => server.close() };
}

test('regras: média ponderada e situação', () => {
  assert.equal(mediaPonderada([{ valor: 8, peso: 1 }, { valor: 6, peso: 3 }]), 6.5);
  assert.equal(mediaPonderada([]), null);
  assert.equal(situacao(7), 'Aprovado');
  assert.equal(situacao(5), 'Recuperação');
  assert.equal(situacao(4.99), 'Reprovado');
});

test('fluxo completo: aluno, disciplina, notas e boletim', async (t) => {
  const { req, close } = await iniciar();
  t.after(close);

  const aluno = await req('POST', '/alunos', { nome: 'Ana Lima', matricula: '20240001', email: 'ana@uni.br' });
  assert.equal(aluno.status, 201);
  const disc = await req('POST', '/disciplinas', { nome: 'Algoritmos', codigo: 'alg101' });
  assert.equal(disc.body.codigo, 'ALG101');

  await req('POST', '/notas', { alunoId: aluno.body.id, disciplinaId: disc.body.id, valor: 9, peso: 1, avaliacao: 'P1' });
  await req('POST', '/notas', { alunoId: aluno.body.id, disciplinaId: disc.body.id, valor: 7, peso: 1, avaliacao: 'P2' });

  const boletim = await req('GET', `/alunos/${aluno.body.id}/boletim`);
  assert.equal(boletim.status, 200);
  assert.equal(boletim.body.disciplinas[0].media, 8);
  assert.equal(boletim.body.disciplinas[0].situacao, 'Aprovado');
  assert.equal(boletim.body.mediaGeral, 8);
});

test('validações e erros', async (t) => {
  const { req, close } = await iniciar();
  t.after(close);

  assert.equal((await req('POST', '/alunos', { nome: '', matricula: '1' })).status, 400);
  await req('POST', '/alunos', { nome: 'Bia', matricula: '1234' });
  assert.equal((await req('POST', '/alunos', { nome: 'Bia 2', matricula: '1234' })).status, 409);
  assert.equal((await req('GET', '/alunos/999')).status, 404);
  assert.equal((await req('GET', '/alunos/abc')).status, 400);
  assert.equal((await req('POST', '/notas', { alunoId: 1, disciplinaId: 9, valor: 11 })).status, 400);
  assert.equal((await req('POST', '/notas', { alunoId: 1, disciplinaId: 9, valor: 5 })).status, 404);
});

test('não permite nota duplicada para a mesma avaliação', async (t) => {
  const { req, close } = await iniciar();
  t.after(close);
  const a = await req('POST', '/alunos', { nome: 'Dani', matricula: '7777' });
  const d = await req('POST', '/disciplinas', { nome: 'Redes', codigo: 'RD1' });
  const nota = { alunoId: a.body.id, disciplinaId: d.body.id, valor: 8, avaliacao: 'P1' };
  assert.equal((await req('POST', '/notas', nota)).status, 201);
  assert.equal((await req('POST', '/notas', nota)).status, 409);
  assert.equal((await req('POST', '/notas', { ...nota, avaliacao: 'P2' })).status, 201);
});

test('remover aluno apaga suas notas', async (t) => {
  const { req, close } = await iniciar();
  t.after(close);
  const a = await req('POST', '/alunos', { nome: 'Caio', matricula: '5555' });
  const d = await req('POST', '/disciplinas', { nome: 'BD', codigo: 'BD1' });
  await req('POST', '/notas', { alunoId: a.body.id, disciplinaId: d.body.id, valor: 6 });
  assert.equal((await req('DELETE', `/alunos/${a.body.id}`)).status, 204);
  assert.deepEqual((await req('GET', '/notas')).body, []);
});
