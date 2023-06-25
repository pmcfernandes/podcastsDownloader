const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const { CONFIG_PATH } = require('./env');

let db = new sqlite3.Database(path.join(CONFIG_PATH, "podcasts.db"));

module.exports = db;