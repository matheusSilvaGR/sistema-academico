'use strict';
// Camada de persistência: arquivo JSON com escrita atômica.
// Isolada atrás de uma interface simples para facilitar a troca por um banco real.
const fs = require('node:fs');
const path = require('node:path');

class Store {
  constructor(file) {
    this.file = file; // null => somente memória (usado nos testes)
    this.data = { alunos: [], disciplinas: [], notas: [], seq: { alunos: 0, disciplinas: 0, notas: 0 } };
    if (file && fs.existsSync(file)) this.data = JSON.parse(fs.readFileSync(file, 'utf8'));
  }

  list(col) { return this.data[col]; }
  find(col, id) { return this.data[col].find((x) => x.id === id); }

  insert(col, obj) {
    const item = { id: ++this.data.seq[col], ...obj };
    this.data[col].push(item);
    this._save();
    return item;
  }

  update(col, id, patch) {
    const item = this.find(col, id);
    if (!item) return null;
    Object.assign(item, patch);
    this._save();
    return item;
  }

  remove(col, id) {
    const i = this.data[col].findIndex((x) => x.id === id);
    if (i < 0) return false;
    this.data[col].splice(i, 1);
    this._save();
    return true;
  }

  _save() {
    if (!this.file) return;
    fs.mkdirSync(path.dirname(this.file), { recursive: true });
    const tmp = `${this.file}.tmp`;
    fs.writeFileSync(tmp, JSON.stringify(this.data, null, 2));
    fs.renameSync(tmp, this.file); // escrita atômica
  }
}

module.exports = { Store };
