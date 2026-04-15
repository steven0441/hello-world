import { getDb } from './db';
import type { Bill, FinanceSummary, Debt } from '@/types';

function getDaysUntilDue(dueDay: number): number {
  const today = new Date();
  const currentDay = today.getDate();
  const daysInMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate();

  if (dueDay >= currentDay) {
    return dueDay - currentDay;
  } else {
    return daysInMonth - currentDay + dueDay;
  }
}

export function getBills(): Bill[] {
  const db = getDb();
  const rows = db.prepare('SELECT * FROM bills WHERE is_active = 1 ORDER BY due_day ASC').all() as Array<{
    id: number; name: string; amount: number; due_day: number; category: string; is_active: number;
  }>;
  return rows.map(r => ({
    id: r.id,
    name: r.name,
    amount: r.amount,
    dueDay: r.due_day,
    category: r.category,
    isActive: r.is_active,
    daysUntilDue: getDaysUntilDue(r.due_day),
  }));
}

export function getMonthlyIncome(): number {
  const db = getDb();
  const sources = db.prepare('SELECT amount, frequency FROM income_sources').all() as Array<{ amount: number; frequency: string }>;
  return sources.reduce((total, s) => {
    switch (s.frequency) {
      case 'monthly': return total + s.amount;
      case 'biweekly': return total + (s.amount * 26) / 12;
      case 'weekly': return total + (s.amount * 52) / 12;
      case 'annual': return total + s.amount / 12;
      default: return total;
    }
  }, 0);
}

export function getLatestSavings(): number {
  const db = getDb();
  const row = db.prepare('SELECT balance FROM savings_entries ORDER BY date DESC LIMIT 1').get() as { balance: number } | undefined;
  return row?.balance ?? 0;
}

export function getTotalDebt(): number {
  const db = getDb();
  const row = db.prepare('SELECT SUM(balance) as total FROM debts').get() as { total: number | null };
  return row.total ?? 0;
}

export function getDebts(): Debt[] {
  const db = getDb();
  const rows = db.prepare('SELECT * FROM debts ORDER BY balance DESC').all() as Array<{
    id: number; name: string; balance: number; interest_rate: number; minimum_payment: number;
  }>;
  return rows.map(r => ({
    id: r.id,
    name: r.name,
    balance: r.balance,
    interestRate: r.interest_rate,
    minimumPayment: r.minimum_payment,
  }));
}

export function calculateBudgetHealth(monthlyIncome: number, bills: Bill[]): number {
  if (monthlyIncome === 0) return 0;
  const totalBills = bills.reduce((sum, b) => sum + b.amount, 0);
  const ratio = totalBills / monthlyIncome;
  // 50% bills = 100% health, 80%+ bills = 0% health
  return Math.max(0, Math.min(100, Math.round((1 - (ratio - 0.5) / 0.3) * 100)));
}

export function getFinanceSummary(): FinanceSummary {
  const bills = getBills();
  const monthlyIncome = getMonthlyIncome();
  const savings = getLatestSavings();
  const totalDebt = getTotalDebt();
  const netWorth = savings - totalDebt;
  const budgetHealth = calculateBudgetHealth(monthlyIncome, bills);
  const upcomingBills = bills.filter(b => b.daysUntilDue <= 14).sort((a, b) => a.daysUntilDue - b.daysUntilDue);

  return { netWorth, monthlyIncome, totalDebt, savings, budgetHealth, upcomingBills };
}

export function addBill(name: string, amount: number, dueDay: number, category: string): Bill {
  const db = getDb();
  const stmt = db.prepare('INSERT INTO bills (name, amount, due_day, category) VALUES (?, ?, ?, ?)');
  const result = stmt.run(name, amount, dueDay, category);
  return {
    id: result.lastInsertRowid as number,
    name, amount, dueDay, category, isActive: 1,
    daysUntilDue: getDaysUntilDue(dueDay),
  };
}

export function deleteBill(id: number): boolean {
  const db = getDb();
  const result = db.prepare('UPDATE bills SET is_active = 0 WHERE id = ?').run(id);
  return result.changes > 0;
}

export function logActivity(agentId: string, level: string, message: string) {
  const db = getDb();
  db.prepare('INSERT INTO activity_log (agent_id, level, message) VALUES (?, ?, ?)').run(agentId, level, message);
}

export function getConversationHistory(agentId: string, limit = 20) {
  const db = getDb();
  return db.prepare(
    'SELECT role, content FROM conversation_history WHERE agent_id = ? ORDER BY created_at ASC LIMIT ?'
  ).all(agentId, limit) as Array<{ role: string; content: string }>;
}

export function saveMessage(agentId: string, role: string, content: string) {
  const db = getDb();
  db.prepare('INSERT INTO conversation_history (agent_id, role, content) VALUES (?, ?, ?)').run(agentId, role, content);
}

export function checkMilestones(): void {
  const db = getDb();
  const savings = getLatestSavings();
  const totalDebt = getTotalDebt();

  const achieve = (key: string) => {
    db.prepare(
      "UPDATE milestones SET achieved_at = ? WHERE agent_id = 'finance' AND key_name = ? AND achieved_at IS NULL"
    ).run(new Date().toISOString(), key);
  };

  if (savings >= 1000) achieve('savings_1k');
  if (savings >= 5000) achieve('savings_5k');
  if (totalDebt === 0) achieve('debt_free');
}
