'use strict';
// Regras de negócio puras (sem I/O): fáceis de testar.
const MEDIA_APROVACAO = 7;
const MEDIA_RECUPERACAO = 5;

const arredonda = (n) => Math.round(n * 100) / 100;

function mediaPonderada(notas) {
  if (notas.length === 0) return null;
  const soma = notas.reduce((s, n) => s + n.valor * n.peso, 0);
  const pesos = notas.reduce((s, n) => s + n.peso, 0);
  return arredonda(soma / pesos);
}

function situacao(media) {
  if (media === null) return 'Sem notas';
  if (media >= MEDIA_APROVACAO) return 'Aprovado';
  if (media >= MEDIA_RECUPERACAO) return 'Recuperação';
  return 'Reprovado';
}

function gerarBoletim(aluno, disciplinas, notas) {
  const itens = disciplinas
    .map((d) => {
      const doAluno = notas.filter((n) => n.alunoId === aluno.id && n.disciplinaId === d.id);
      if (doAluno.length === 0) return null;
      const media = mediaPonderada(doAluno);
      return { disciplina: d.nome, codigo: d.codigo, notas: doAluno.length, media, situacao: situacao(media) };
    })
    .filter(Boolean);
  const medias = itens.map((i) => i.media);
  const mediaGeral = medias.length ? arredonda(medias.reduce((a, b) => a + b, 0) / medias.length) : null;
  return { aluno: { id: aluno.id, nome: aluno.nome, matricula: aluno.matricula }, disciplinas: itens, mediaGeral };
}

module.exports = { mediaPonderada, situacao, gerarBoletim, MEDIA_APROVACAO, MEDIA_RECUPERACAO };
