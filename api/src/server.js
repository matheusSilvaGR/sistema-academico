'use strict';
const path = require('node:path');
const { createApp } = require('./app');
const { Store } = require('./store');

const PORT = process.env.PORT || 3000;
const DB_FILE = process.env.DB_FILE || path.join(__dirname, '..', 'data', 'db.json');

createApp(new Store(DB_FILE)).listen(PORT, () => {
  console.log(`API acadêmica em http://localhost:${PORT}  (dados: ${DB_FILE})`);
});
