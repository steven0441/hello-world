import Database from 'better-sqlite3';
import path from 'path';

const DB_PATH = path.join(process.cwd(), 'dungeon.db');

let _db: Database.Database | null = null;

export function getDb(): Database.Database {
  if (_db) return _db;
  _db = new Database(DB_PATH);
  _db.pragma('journal_mode = WAL');
  initSchema(_db);
  return _db;
}

function initSchema(db: Database.Database) {
  db.exec(`
    CREATE TABLE IF NOT EXISTS income_sources (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      amount REAL NOT NULL,
      frequency TEXT NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS bills (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      amount REAL NOT NULL,
      due_day INTEGER NOT NULL,
      category TEXT NOT NULL,
      is_active INTEGER DEFAULT 1,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS expenses (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      description TEXT NOT NULL,
      amount REAL NOT NULL,
      category TEXT NOT NULL,
      date TEXT NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS savings_entries (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      balance REAL NOT NULL,
      note TEXT,
      date TEXT NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS debts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      balance REAL NOT NULL,
      interest_rate REAL NOT NULL,
      minimum_payment REAL NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS activity_log (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      agent_id TEXT NOT NULL,
      level TEXT NOT NULL,
      message TEXT NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS milestones (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      agent_id TEXT NOT NULL,
      key_name TEXT NOT NULL,
      label TEXT NOT NULL,
      icon TEXT NOT NULL,
      achieved_at TEXT,
      UNIQUE(agent_id, key_name)
    );

    CREATE TABLE IF NOT EXISTS conversation_history (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      agent_id TEXT NOT NULL,
      role TEXT NOT NULL,
      content TEXT NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
  `);

  seedIfEmpty(db);
}

function seedIfEmpty(db: Database.Database) {
  const count = (db.prepare('SELECT COUNT(*) as c FROM income_sources').get() as { c: number }).c;
  if (count > 0) return;

  // Seed demo data
  db.prepare(`INSERT INTO income_sources (name, amount, frequency) VALUES (?, ?, ?)`).run('Primary Job', 5200, 'monthly');

  const bills = [
    ['Rent', 1200, 1, 'housing'],
    ['Electricity', 85, 15, 'utilities'],
    ['Internet', 60, 10, 'utilities'],
    ['Netflix', 18, 5, 'subscriptions'],
    ['Spotify', 11, 12, 'subscriptions'],
    ['Phone', 75, 8, 'utilities'],
    ['Gym', 45, 20, 'health'],
  ];
  const billStmt = db.prepare(`INSERT INTO bills (name, amount, due_day, category) VALUES (?, ?, ?, ?)`);
  for (const [name, amount, dueDay, category] of bills) {
    billStmt.run(name, amount, dueDay, category);
  }

  db.prepare(`INSERT INTO savings_entries (balance, note, date) VALUES (?, ?, ?)`).run(2450, 'Initial balance', new Date().toISOString().split('T')[0]);
  db.prepare(`INSERT INTO debts (name, balance, interest_rate, minimum_payment) VALUES (?, ?, ?, ?)`).run('Student Loan', 8200, 5.5, 120);

  // Seed milestones
  const milestones = [
    ['finance', 'savings_1k', 'Gold Coin', '🪙'],
    ['finance', 'debt_payment', 'Chainbreaker', '⛓'],
    ['finance', 'budget_on_track', 'Treasure Chest', '📦'],
    ['finance', 'savings_5k', 'Diamond', '💎'],
    ['finance', 'emergency_fund', 'Shield', '🛡️'],
    ['finance', 'debt_free', 'Crown', '👑'],
  ];
  const msStmt = db.prepare(`INSERT OR IGNORE INTO milestones (agent_id, key_name, label, icon) VALUES (?, ?, ?, ?)`);
  for (const [agentId, key, label, icon] of milestones) {
    msStmt.run(agentId, key, label, icon);
  }

  db.prepare(`INSERT INTO activity_log (agent_id, level, message) VALUES (?, ?, ?)`).run(
    'finance', 'info', 'Bean Counter initialized. Ledger open. The numbers are... familiar.'
  );
}
