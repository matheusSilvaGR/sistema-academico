'use strict';

class ValidationError extends Error {
  constructor(message) { super(message); this.status = 400; }
}

const isStr = (v) => typeof v === 'string' && v.trim().length > 0;

function validarAluno(b) {
  if (!isStr(b.nome)) throw new ValidationError('nome é obrigatório');
  if (!isStr(b.matricula) || !/^\d{4,12}$/.test(b.matricula)) {
    throw new ValidationError('matricula deve ter de 4 a 12 dígitos');
  }
  if (b.email !== undefined && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(b.email)) {
    throw new ValidationError('email inválido');
  }
  return { nome: b.nome.trim(), matricula: b.matricula, email: b.email ?? null };
}

function validarDisciplina(b) {
  if (!isStr(b.nome)) throw new ValidationError('nome é obrigatório');
  if (!isStr(b.codigo)) throw new ValidationError('codigo é obrigatório');
  const ch = b.cargaHoraria ?? 60;
  if (!Number.isInteger(ch) || ch <= 0) throw new ValidationError('cargaHoraria deve ser inteiro positivo');
  return { nome: b.nome.trim(), codigo: b.codigo.trim().toUpperCase(), cargaHoraria: ch };
}

function validarNota(b) {
  const alunoId = Number(b.alunoId);
  const disciplinaId = Number(b.disciplinaId);
  const valor = Number(b.valor);
  if (!Number.isInteger(alunoId) || !Number.isInteger(disciplinaId)) {
    throw new ValidationError('alunoId e disciplinaId são obrigatórios');
  }
  if (!Number.isFinite(valor) || valor < 0 || valor > 10) {
    throw new ValidationError('valor deve estar entre 0 e 10');
  }
  const peso = b.peso === undefined ? 1 : Number(b.peso);
  if (!Number.isFinite(peso) || peso <= 0) throw new ValidationError('peso deve ser positivo');
  return { alunoId, disciplinaId, valor, peso, avaliacao: isStr(b.avaliacao) ? b.avaliacao.trim() : 'Prova' };
}

module.exports = { ValidationError, validarAluno, validarDisciplina, validarNota };
