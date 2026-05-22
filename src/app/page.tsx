'use client';

import { useState, useEffect, useRef } from 'react';
import dynamic from 'next/dynamic';
import type { FinanceSummary, Bill, Milestone, BeanState } from '@/types';

const DungeonCell = dynamic(() => import('@/components/DungeonCell'), { ssr: false });

export default function GodDungeon() {
  const [summary, setSummary] = useState<FinanceSummary | null>(null);
  const [milestones, setMilestones] = useState<Milestone[]>([]);

  const [godInput, setGodInput] = useState('');
  const [orchestratorText, setOrchestratorText] = useState('');
  const [orchestratorStreaming, setOrchestratorStreaming] = useState(false);

  const [beanInput, setBeanInput] = useState('');
  const [beanMessages, setBeanMessages] = useState<{ role: 'user' | 'bean'; text: string }[]>([]);
  const [beanStreaming, setBeanStreaming] = useState(false);
  const beanChatRef = useRef<HTMLDivElement>(null);

  const [beanState, setBeanState] = useState<BeanState>('idle');
  const phaserGameRef = useRef<import('phaser').Game | null>(null);

  const [showAddBill, setShowAddBill] = useState(false);
  const [newBill, setNewBill] = useState({ name: '', amount: '', dueDay: '', category: 'utilities' });

  useEffect(() => {
    fetchSummary();
    fetchMilestones();
    const interval = setInterval(fetchSummary, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (beanChatRef.current) {
      beanChatRef.current.scrollTop = beanChatRef.current.scrollHeight;
    }
  }, [beanMessages]);

  useEffect(() => {
    if (!summary) return;
    const urgent = summary.upcomingBills.some(b => b.daysUntilDue <= 1);
    if (urgent && beanState === 'idle') {
      setBeanState('alert');
      setTimeout(() => setBeanState('idle'), 6000);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [summary]);

  const fetchSummary = async () => {
    try {
      const res = await fetch('/api/finance/summary');
      const data = await res.json();
      setSummary(data);
    } catch (e) {
      console.error('Failed to load summary', e);
    }
  };

  const fetchMilestones = async () => {
    try {
      const res = await fetch('/api/milestones');
      const data = await res.json();
      setMilestones(data.milestones || []);
    } catch (e) {
      console.error('Failed to load milestones', e);
    }
  };

  const issueDecree = async () => {
    if (!godInput.trim() || orchestratorStreaming) return;
    const decree = godInput.trim();
    setGodInput('');
    setOrchestratorStreaming(true);
    setOrchestratorText('');
    setBeanState('working');

    try {
      const res = await fetch('/api/orchestrator/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: decree }),
      });

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const lines = decoder.decode(value).split('\n');
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const data = line.slice(6).trim();
          if (data === '[DONE]') continue;
          try {
            const parsed = JSON.parse(data);
            if (parsed.text) {
              buffer += parsed.text;
              setOrchestratorText(buffer);
            }
          } catch {}
        }
      }
    } catch {
      setOrchestratorText('◈ The dungeon connection was lost...');
    } finally {
      setOrchestratorStreaming(false);
      setBeanState('idle');
    }
  };

  const askBean = async () => {
    if (!beanInput.trim() || beanStreaming) return;
    const question = beanInput.trim();
    setBeanInput('');
    setBeanMessages(m => [...m, { role: 'user', text: question }]);
    setBeanStreaming(true);
    setBeanState('working');
    phaserGameRef.current?.events.emit('bean:speak', 'Working on it...');

    try {
      const res = await fetch('/api/finance/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: question }),
      });

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let msgAdded = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const lines = decoder.decode(value).split('\n');
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const data = line.slice(6).trim();
          if (data === '[DONE]') continue;
          try {
            const parsed = JSON.parse(data);
            if (parsed.text) {
              buffer += parsed.text;
              if (!msgAdded) {
                setBeanMessages(m => [...m, { role: 'bean', text: buffer }]);
                msgAdded = true;
              } else {
                setBeanMessages(m => {
                  const copy = [...m];
                  copy[copy.length - 1] = { role: 'bean', text: buffer };
                  return copy;
                });
              }
            }
          } catch {}
        }
      }

      if (buffer) {
        phaserGameRef.current?.events.emit('bean:speak', buffer.slice(0, 80) + (buffer.length > 80 ? '...' : ''));
      }
      await fetchMilestones();
      await fetchSummary();
    } catch {
      setBeanMessages(m => [...m, { role: 'bean', text: 'There was an error. The numbers are unclear.' }]);
    } finally {
      setBeanStreaming(false);
      setBeanState('idle');
    }
  };

  const addBill = async () => {
    if (!newBill.name || !newBill.amount || !newBill.dueDay) return;
    try {
      await fetch('/api/finance/bills', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newBill.name,
          amount: Number(newBill.amount),
          dueDay: Number(newBill.dueDay),
          category: newBill.category,
        }),
      });
      setNewBill({ name: '', amount: '', dueDay: '', category: 'utilities' });
      setShowAddBill(false);
      fetchSummary();
    } catch {}
  };

  const deleteBill = async (id: number) => {
    await fetch(`/api/finance/bills?id=${id}`, { method: 'DELETE' });
    fetchSummary();
  };

  const healthColor = (h: number) =>
    h >= 70 ? '#00ff88' : h >= 40 ? '#f5c542' : '#ff4040';

  const daysLabel = (d: number) =>
    d === 0 ? 'TODAY' : d === 1 ? 'TOMORROW' : `${d}d`;

  return (
    <main className="min-h-screen p-4 md:p-6">

      {/* ── GOD'S THRONE ── */}
      <header className="mb-4 rounded-lg border border-[#3a2e00] glow-god bg-[#0f0f1a] p-4">
        <div className="flex items-center gap-3 mb-3 flex-wrap">
          <span className="font-cinzel text-2xl text-[#f5c542]">♕</span>
          <h1 className="font-cinzel text-xl text-[#f5c542] tracking-widest uppercase">
            God Dungeon
          </h1>
          {summary && (
            <span className="ml-auto font-mono-code text-sm text-[#00ff88]">
              Net Worth: ${summary.netWorth.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
            </span>
          )}
        </div>
        <div className="flex gap-2">
          <input
            className="flex-1 bg-[#080810] border border-[#3a2e00] rounded px-3 py-2 text-[#e2e8f0] text-sm font-mono-code focus:outline-none focus:border-[#f5c542] placeholder-[#4a5568]"
            placeholder="Issue a Divine Decree..."
            value={godInput}
            onChange={e => setGodInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && issueDecree()}
            disabled={orchestratorStreaming}
          />
          <button
            onClick={issueDecree}
            disabled={orchestratorStreaming || !godInput.trim()}
            className="px-4 py-2 rounded bg-[#f5c542] text-[#080810] font-cinzel text-sm font-bold hover:bg-[#f0d070] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            DECREE
          </button>
        </div>
      </header>

      {/* ── ORCHESTRATOR ── */}
      <div className="mb-4 rounded-lg border border-[#3d1f7a] glow-orchestrator bg-[#0f0f1a] p-4">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-[#9b59f5]">◈</span>
          <span className="font-cinzel text-sm text-[#9b59f5] tracking-widest">ORCHESTRATOR</span>
          <span className="ml-auto text-[8px] text-[#4a5568] font-mono-code uppercase tracking-wider">
            claude opus 4.6
          </span>
        </div>
        <p className={`font-mono-code text-sm text-[#e2e8f0] leading-relaxed min-h-[1.5rem] ${orchestratorStreaming ? 'typing-cursor' : ''}`}>
          {orchestratorText || (
            <span className="text-[#4a5568]">◈ Awaiting your decree...</span>
          )}
        </p>
      </div>

      {/* ── MAIN GRID ── */}
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_280px] gap-4">

        {/* LEFT: Bean's Cell */}
        <div className="rounded-lg border border-[#5a2a0a] glow-finance bg-[#0f0f1a] overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-2 border-b border-[#1e1e2e]">
            <span className="text-[#ff6b35]">⛓</span>
            <span className="font-cinzel text-sm text-[#ff6b35] tracking-widest">
              BEAN COUNTER&apos;S CELL
            </span>
            <span className="text-[8px] bg-[#5a2a0a] text-[#ff6b35] px-2 py-0.5 rounded font-mono-code uppercase">
              condemned
            </span>
            <span className="ml-auto text-[8px] text-[#4a5568] font-mono-code uppercase tracking-wider">
              claude sonnet 4.6
            </span>
          </div>

          {/* Phaser canvas */}
          <div className="flex justify-center bg-[#1a1510] p-1">
            <DungeonCell
              beanState={beanState}
              onBeanReady={() => {}}
            />
          </div>

          {/* Status bar */}
          <div className="px-4 py-2 border-t border-[#1e1e2e] bg-[#0a0a14]">
            <div className="flex items-center gap-2 text-xs font-mono-code text-[#4a5568]">
              <span className="text-[#ff6b35]">●</span>
              <span>
                {beanState === 'working' && <span className="text-[#f5c542]">Analyzing the ledger...</span>}
                {beanState === 'sleeping' && <span className="text-[#9b59f5]">Resting. Still in the suit.</span>}
                {beanState === 'alert' && <span className="text-[#ff4040] blink-alert">⚠ URGENT BILL DUE</span>}
                {beanState === 'celebrating' && <span className="text-[#00ff88]">Milestone acknowledged.</span>}
                {beanState === 'idle' && <span className="text-[#4a5568]">Waiting. Always waiting.</span>}
              </span>
            </div>
          </div>

          {/* Bean chat */}
          <div className="border-t border-[#1e1e2e] p-4">
            <div ref={beanChatRef} className="h-44 overflow-y-auto mb-3 space-y-2 pr-1">
              {beanMessages.length === 0 && (
                <p className="text-[#4a5568] text-xs font-mono-code italic">
                  Ask Bean anything about your finances.
                </p>
              )}
              {beanMessages.map((m, i) => (
                <div key={i} className={`flex gap-2 text-xs ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {m.role === 'bean' && (
                    <span className="text-[#ff6b35] font-mono-code mt-0.5 shrink-0">Bean:</span>
                  )}
                  <div
                    className={`max-w-[85%] rounded px-3 py-2 font-mono-code leading-relaxed whitespace-pre-wrap ${
                      m.role === 'user'
                        ? 'bg-[#1e1e2e] text-[#e2e8f0]'
                        : 'bg-[#1a1008] border border-[#3a2000] text-[#e2e8f0]'
                    } ${beanStreaming && i === beanMessages.length - 1 && m.role === 'bean' ? 'typing-cursor' : ''}`}
                  >
                    {m.text}
                  </div>
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                className="flex-1 bg-[#080810] border border-[#3a2000] rounded px-3 py-2 text-[#e2e8f0] text-xs font-mono-code focus:outline-none focus:border-[#ff6b35] placeholder-[#4a5568]"
                placeholder="Ask Bean..."
                value={beanInput}
                onChange={e => setBeanInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && askBean()}
                disabled={beanStreaming}
              />
              <button
                onClick={askBean}
                disabled={beanStreaming || !beanInput.trim()}
                className="px-3 py-2 rounded bg-[#ff6b35] text-[#080810] text-xs font-mono-code font-bold hover:bg-[#ff8050] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                ASK
              </button>
            </div>
          </div>
        </div>

        {/* RIGHT: Stats + Bills + Milestones */}
        <div className="flex flex-col gap-4">

          {/* Ledger stats */}
          <div className="rounded-lg border border-[#1e1e2e] bg-[#0f0f1a] p-4">
            <h3 className="font-cinzel text-xs text-[#4a5568] tracking-widest uppercase mb-3">Ledger</h3>
            {summary ? (
              <div className="space-y-2 font-mono-code text-sm">
                <div className="flex justify-between">
                  <span className="text-[#4a5568]">Income</span>
                  <span className="text-[#00ff88]">${summary.monthlyIncome.toFixed(0)}/mo</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#4a5568]">Savings</span>
                  <span className="text-[#e2e8f0]">${summary.savings.toFixed(0)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#4a5568]">Debt</span>
                  <span className="text-[#ff4040]">${summary.totalDebt.toFixed(0)}</span>
                </div>
                <div className="flex justify-between border-t border-[#1e1e2e] pt-2">
                  <span className="text-[#4a5568]">Net Worth</span>
                  <span className={summary.netWorth >= 0 ? 'text-[#00ff88]' : 'text-[#ff4040]'}>
                    {summary.netWorth < 0 ? '-' : ''}${Math.abs(summary.netWorth).toFixed(0)}
                  </span>
                </div>
                <div className="pt-1">
                  <div className="flex justify-between text-[10px] text-[#4a5568] mb-1">
                    <span>Budget Health</span>
                    <span style={{ color: healthColor(summary.budgetHealth) }}>
                      {summary.budgetHealth}%
                    </span>
                  </div>
                  <div className="h-2 bg-[#1e1e2e] rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-700"
                      style={{
                        width: `${summary.budgetHealth}%`,
                        backgroundColor: healthColor(summary.budgetHealth),
                      }}
                    />
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-[#4a5568] text-xs font-mono-code">Loading ledger...</p>
            )}
          </div>

          {/* Bills */}
          <div className="rounded-lg border border-[#1e1e2e] bg-[#0f0f1a] p-4">
            <div className="flex items-center gap-2 mb-3">
              <h3 className="font-cinzel text-xs text-[#4a5568] tracking-widest uppercase">Bills</h3>
              <button
                onClick={() => setShowAddBill(v => !v)}
                className="ml-auto text-[10px] text-[#ff6b35] font-mono-code hover:text-[#ff8050] transition-colors"
              >
                {showAddBill ? '✕ cancel' : '+ add'}
              </button>
            </div>

            {showAddBill && (
              <div className="mb-3 space-y-2 text-xs font-mono-code">
                <input
                  className="w-full bg-[#080810] border border-[#1e1e2e] rounded px-2 py-1.5 text-[#e2e8f0] placeholder-[#4a5568] focus:border-[#ff6b35] outline-none"
                  placeholder="Bill name"
                  value={newBill.name}
                  onChange={e => setNewBill(b => ({ ...b, name: e.target.value }))}
                />
                <div className="flex gap-2">
                  <input
                    className="flex-1 bg-[#080810] border border-[#1e1e2e] rounded px-2 py-1.5 text-[#e2e8f0] placeholder-[#4a5568] focus:border-[#ff6b35] outline-none"
                    placeholder="Amount $"
                    type="number"
                    value={newBill.amount}
                    onChange={e => setNewBill(b => ({ ...b, amount: e.target.value }))}
                  />
                  <input
                    className="w-14 bg-[#080810] border border-[#1e1e2e] rounded px-2 py-1.5 text-[#e2e8f0] placeholder-[#4a5568] focus:border-[#ff6b35] outline-none"
                    placeholder="Day"
                    type="number"
                    min={1}
                    max={31}
                    value={newBill.dueDay}
                    onChange={e => setNewBill(b => ({ ...b, dueDay: e.target.value }))}
                  />
                </div>
                <select
                  className="w-full bg-[#080810] border border-[#1e1e2e] rounded px-2 py-1.5 text-[#e2e8f0] focus:border-[#ff6b35] outline-none"
                  value={newBill.category}
                  onChange={e => setNewBill(b => ({ ...b, category: e.target.value }))}
                >
                  {['housing', 'utilities', 'subscriptions', 'health', 'transport', 'food', 'other'].map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
                <button
                  onClick={addBill}
                  className="w-full py-1.5 rounded bg-[#ff6b35] text-[#080810] font-bold hover:bg-[#ff8050] transition-colors"
                >
                  Add Bill
                </button>
              </div>
            )}

            <div className="space-y-1.5 max-h-52 overflow-y-auto">
              {(!summary || summary.upcomingBills.length === 0) && (
                <p className="text-[#4a5568] text-[11px] font-mono-code">No bills due in 14 days.</p>
              )}
              {summary?.upcomingBills.map((bill: Bill) => (
                <div key={bill.id} className="flex items-center gap-2 text-xs font-mono-code group">
                  <span
                    className={`w-16 text-right shrink-0 font-bold text-[10px] ${
                      bill.daysUntilDue === 0 ? 'text-[#ff4040] blink-alert' :
                      bill.daysUntilDue <= 3 ? 'text-[#ff6b35]' :
                      bill.daysUntilDue <= 7 ? 'text-[#f5c542]' : 'text-[#4a5568]'
                    }`}
                  >
                    {daysLabel(bill.daysUntilDue)}
                  </span>
                  <span className="flex-1 text-[#e2e8f0] truncate">{bill.name}</span>
                  <span className="text-[#a0aec0] shrink-0">${bill.amount}</span>
                  <button
                    onClick={() => deleteBill(bill.id)}
                    className="text-[#4a5568] hover:text-[#ff4040] opacity-0 group-hover:opacity-100 transition-all text-[10px] shrink-0"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Milestones */}
          <div className="rounded-lg border border-[#1e1e2e] bg-[#0f0f1a] p-4">
            <h3 className="font-cinzel text-xs text-[#4a5568] tracking-widest uppercase mb-3">
              Milestones
            </h3>
            <div className="grid grid-cols-3 gap-2">
              {milestones.map(m => (
                <div
                  key={m.key}
                  className={`flex flex-col items-center gap-1 p-2 rounded border text-center transition-all ${
                    m.achievedAt
                      ? 'border-[#f5c542] bg-[#1a1500]'
                      : 'border-[#1e1e2e] opacity-30 grayscale'
                  }`}
                  title={m.achievedAt
                    ? `Achieved: ${new Date(m.achievedAt).toLocaleDateString()}`
                    : 'Not yet achieved'}
                >
                  <span className="text-lg leading-none">{m.icon}</span>
                  <span className="text-[8px] font-mono-code text-[#e2e8f0] leading-tight">{m.label}</span>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>

      <footer className="mt-6 text-center text-[#4a5568] text-[10px] font-mono-code tracking-widest">
        ⛓ BEAN COUNTER HAS BEEN HERE FOR [REDACTED] YEARS ⛓
      </footer>
    </main>
  );
}
