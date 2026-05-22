export interface Bill {
  id: number;
  name: string;
  amount: number;
  dueDay: number;
  category: string;
  isActive: number;
  daysUntilDue: number;
}

export interface IncomeSource {
  id: number;
  name: string;
  amount: number;
  frequency: 'monthly' | 'biweekly' | 'weekly' | 'annual';
}

export interface Expense {
  id: number;
  description: string;
  amount: number;
  category: string;
  date: string;
}

export interface Debt {
  id: number;
  name: string;
  balance: number;
  interestRate: number;
  minimumPayment: number;
}

export interface FinanceSummary {
  netWorth: number;
  monthlyIncome: number;
  totalDebt: number;
  savings: number;
  budgetHealth: number;
  upcomingBills: Bill[];
}

export interface Milestone {
  id: number;
  agentId: string;
  key: string;
  label: string;
  icon: string;
  achievedAt: string | null;
}

export interface ActivityLogEntry {
  id: number;
  agentId: string;
  level: 'info' | 'warn' | 'success' | 'error';
  message: string;
  createdAt: string;
}

export interface AgentMessage {
  role: 'user' | 'assistant';
  content: string;
}

export type BeanState =
  | 'idle'
  | 'working'
  | 'sleeping'
  | 'safe'
  | 'restroom'
  | 'alert'
  | 'celebrating';

export type AgentBackend = 'anthropic' | 'ollama' | 'openai';

export interface AgentConfig {
  backend: AgentBackend;
  model: string;
  apiKey?: string;
  baseUrl?: string;
}
