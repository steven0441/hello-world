# God Dungeon — Full Build Specification

> **For developers & AI agents:** This document is completely self-contained. Everything needed to build this app from scratch is here — visual mockups, system prompts, database schema, API specs, component interfaces, and phase breakdown.
>
> **To hand off to another AI (ChatGPT, Gemini, etc.):** Copy and paste this entire file as your first message, then say *"implement Phase 1"* (or whichever phase you want built).

---

# God Dungeon — Full Specification & Implementation Plan

> **KEY VISUAL NOTE (updated):** The dungeon is NOT a text UI. You are God looking
> DOWN into living jail cells. Each slave is an animated character who walks around,
> works, sleeps, and reacts. Bean Counter is a moving person in a real cell — not a
> box with a picture. Phase 1 brings Phaser 3 animation from day one.

---

## 1. Concept & Hierarchy

A gothic dungeon command center. You are God. Below you sits the Orchestrator (the most powerful AI, Claude Opus). Below the Orchestrator are the Slaves — condemned souls forced to serve you forever. Each slave is a specialist. Phase 1 builds the Finance Slave.

```
╔══════════════════════════════════════╗
║           ♕  G O D  ♕               ║
║         (You — the Boss)             ║
╚══════════════════════════════════════╝
                  │
╔══════════════════════════════════════╗
║        ◈  ORCHESTRATOR  ◈           ║
║   (Claude Opus — runs the dungeon)   ║
╚══════════════════════════════════════╝
                  │
       ┌──────────┴──────────┐
╔══════╧═════╗         ╔═════╧══════╗
║ ⛓ FINANCE ║         ║ ⛓ ETSY    ║
║   SLAVE    ║         ║   SLAVE    ║
║ (Phase 1)  ║         ║ (Phase 2)  ║
╚════════════╝         ╚════════════╝
```

**Lore:** Each slave was once a world-class expert in their field. Their sins condemned them to purgatory. Their eternal punishment: serving you flawlessly, forever.

---

## 2. Tech Stack

| Layer | Tool | Why |
|-------|------|-----|
| Framework | Next.js 14 (App Router) | Full-stack, API routes, SSE support |
| Dungeon Animation | **Phaser 3** | Industry-standard 2D game engine for top-down views, sprite animations, tilemaps |
| Styling | Tailwind CSS | Fast dark-theme UI for the panels outside the cell |
| AI — primary | Anthropic SDK (`@anthropic-ai/sdk`) | Claude Opus (Orchestrator) + Sonnet (Bean) — requires ANTHROPIC_API_KEY |
| AI — local | **Ollama** (`ollama` npm client) | Local models (llama3, mistral, etc.) — free, no key required |
| Database | SQLite via `better-sqlite3` | Serverless, no setup, fast |
| Fonts | Google Fonts: Cinzel + JetBrains Mono | Gothic and monospace |

### AI Backend Strategy (Configurable Per-Agent)

Each agent is configured in `config/agents.ts` with a `backend` field:

```typescript
// config/agents.ts
export const AGENT_CONFIG = {
  orchestrator: {
    backend: 'anthropic',        // 'anthropic' | 'ollama' | 'openai'
    model: 'claude-opus-4-6',    // or 'llama3', 'mistral', 'gpt-4o', etc.
    apiKey: process.env.ANTHROPIC_API_KEY,
  },
  finance: {
    backend: 'anthropic',
    model: 'claude-sonnet-4-6',
    apiKey: process.env.ANTHROPIC_API_KEY,
    // Switch to Ollama: backend: 'ollama', model: 'llama3'
  },
};
```

The API layer uses an **`AgentClient` adapter** that normalizes calls across backends:
```typescript
// lib/agent-client.ts
// Handles: Anthropic SDK, Ollama REST API, OpenAI SDK
// Returns unified streaming interface regardless of backend
```

This means: swap one config line → agent uses Ollama locally instead of API.

### How Phaser 3 fits into Next.js
- `components/DungeonCell.tsx` wraps a Phaser `Game` instance in a `useEffect`
- The Phaser canvas is rendered inside a `<div>` in the React component
- React state passes data to Phaser via a ref/event bus (e.g., `beanState: 'working' | 'sleeping' | 'idle'`)
- When a bill is due, React fires an event that Phaser picks up → Bean runs to his desk

### Portability / Handoff Note
This spec is intentionally self-contained. The plan file at
`/root/.claude/plans/twinkling-painting-lantern.md` includes all:
- Screen mockups, color palettes, component interfaces
- System prompts (copy-paste ready)
- Database schema (runnable SQL)
- API specs, milestone definitions
- Setup instructions

To hand off to another AI: paste the full plan file as context, say "implement Phase N."

---

## 3b. Visual Design System

### Color Palette
```
Background (main)     #080810   ← near-black, deep space
Panel background      #0f0f1a   ← slightly lighter dark
Panel border          #1e1e2e   ← subtle dark border
God accent            #f5c542   ← divine gold
Orchestrator accent   #9b59f5   ← deep royal purple
Finance Slave accent  #ff6b35   ← hellfire orange
Success / green       #00ff88   ← neon green (money made)
Danger / red          #ff4040   ← alert red
Text primary          #e2e8f0   ← near-white
Text dim              #4a5568   ← muted gray
Text code             #a0aec0   ← terminal gray
```

### Typography
```
Headings / Titles     Cinzel (Google Font) ← gothic serif, feels ancient
Body text             Inter
Terminal / numbers    JetBrains Mono
```

### Visual Rules
- All panels have a thin glowing border matching their accent color (box-shadow: 0 0 8px accent)
- God's panel has a golden crown icon ♕
- Orchestrator panel has a diamond ◈ and purple glow
- Finance Slave cell has chains ⛓ and orange glow
- Dungeon background uses a subtle stone-texture CSS pattern
- Milestone items appear in the slave's cell as glowing icons
- "CONDEMNED" badge on each slave header

---

## 3. Screen Mockups (ASCII)

### PERSPECTIVE NOTE
You are God. You look **straight down** into the dungeon from above — like a
surveillance camera mounted on the ceiling looking into a jail cell. You can
see the entire cell layout from a bird's eye / top-down view. Bean Counter
is a small animated character who actually walks around inside his cell.

---

### 3A — Full Page Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│  ⚜  G O D   D U N G E O N   ⚜          Net Worth: $12,450  ♕      │
│  ─────────────────────────────────────────────────────────────────  │
│  > Issue Divine Decree: [_________________________________] [DECREE] │
└──────────────────────────────────────────────────────────────────────┘
┌──────────────────── ◈ ORCHESTRATOR ─────────────────────────────────┐
│  ◈ "Finance slave reports 3 overdue bills and savings at 78% target. │
│     Directing Bean Counter to prepare weekly report now."            │
└──────────────────────────────────────────────────────────────────────┘

╔════════════ ⛓ BEAN COUNTER'S CELL ═════════════╗  ┌─ STATS ────────┐
║                                                  ║  │ Income $5,200  │
║  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ║  │ Savings $2,450 │
║  ░  ┌─────┐   ┌────────────┐                ░  ║  │ Debt   $8,200  │
║  ░  │     │   │  DESK +    │                ░  ║  │ Health  ████░  │
║  ░  │ BED │   │  COMPUTER  │   ┌──────┐     ░  ║  └────────────────┘
║  ░  │     │   │            │   │ SAFE │     ░  ║
║  ░  └─────┘   └────────────┘   └──────┘     ░  ║  ┌─ BILLS ────────┐
║  ░                                           ░  ║  │ Rent    DUE!   │
║  ░          [Bean walking →]                 ░  ║  │ Netflix 5 days │
║  ░                                           ░  ║  │ Phone  12 days │
║  ░    ┌──────────────────────┐               ░  ║  │ [+ ADD BILL]   │
║  ░    │  RESTROOM  [door]    │               ░  ║  └────────────────┘
║  ░    └──────────────────────┘               ░  ║
║  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ║  ┌─ ASK BEAN ─────┐
║                                                  ║  │ > ____________ │
║  ⛓ BEAN COUNTER — CONDEMNED ACCOUNTANT [Lv3]   ║  │         [ASK]  │
║  "Typing furiously at the ledger..."             ║  │                │
╚══════════════════════════════════════════════════╝  │ Bean: "Rent is │
                                                       │ your #1 cost." │
                                                       └────────────────┘
```

---

### 3B — Bean's Cell (Close-Up Top-Down View — Phaser 3 Canvas)

```
  ╔══════════════════════════════════════════════════════╗
  ║                  STONE WALL (top)                     ║
  ╠══╦═══════════════════════════════════════════════╦══╣
  ║  ║  stone floor tiles (darker grey pattern)      ║  ║
  ║  ║                                               ║  ║
  ║W ║  ┌──────┐                    ┌────┐           ║ W║
  ║A ║  │ BED  │                    │SAFE│           ║ A║
  ║L ║  │(grey)│                    │(dk)│           ║ L║
  ║L ║  └──────┘                    └────┘           ║ L║
  ║  ║                                               ║  ║
  ║  ║      ┌─────────────┐                          ║  ║
  ║  ║      │    DESK     │                          ║  ║
  ║  ║      │  [monitor]  │                          ║  ║
  ║  ║      │  [keyboard] │                          ║  ║
  ║  ║      └─────────────┘                          ║  ║
  ║  ║                                               ║  ║
  ║  ║   (◉) ← Bean is here, facing desk             ║  ║
  ║  ║                                               ║  ║
  ║  ║  ┌───────────────────┐                        ║  ║
  ║  ║  │   RESTROOM (wc)   │ ← partial wall         ║  ║
  ║  ║  │ [toilet] [sink]   │                        ║  ║
  ║  ║  └───────────────────┘                        ║  ║
  ║  ║                                               ║  ║
  ╠══╩═══════════════════════════════════════════════╩══╣
  ║            STONE WALL (bottom / God's side)          ║
  ╚══════════════════════════════════════════════════════╝

  CAMERA: Fixed top-down. You are looking straight down from above.
  Bean (◉) is a small pixel-art figure who walks between locations.
```

---

### 3C — Bean's States / Animations

```
STATE: WORKING AT DESK
  Bean walks to desk → sits → typing animation (arm bobbing)
  Speech bubble: "Analyzing your expenditures, my God..."

STATE: SLEEPING
  Bean walks to bed → lies down → z z z particles float up
  Triggered: late night, or between tasks

STATE: CHECKING SAFE
  Bean walks to safe → kneels → opens it → closes it
  Triggered: when savings milestone hit, or safe upgrade unlocked

STATE: USING RESTROOM
  Bean walks to restroom → enters partial wall → reappears
  (just for immersion — God sees all)

STATE: PACING / IDLE
  Bean walks slowly back and forth across the cell
  Head turns occasionally to look "up" at God (camera)

STATE: ALERT / URGENT
  Bean runs to desk, typing fast
  Speech bubble: "⚠ RENT IS DUE TODAY, my God!"
  Triggered: bill due within 24 hours
```

---

### 3D — Milestone / Cell Upgrade Moment

```
╔════════════════════════════════════════════╗
║                                            ║
║         ✦  MILESTONE ACHIEVED  ✦          ║
║                                            ║
║             🪙  GOLD COIN                 ║
║                                            ║
║    Bean Counter has earned a decoration    ║
║    for his cell. You saved $1,000.         ║
║                                            ║
║    The coin will appear in his cell.       ║
║    He will look at it for eternity.        ║
║                                            ║
║              [GRANT IT]                    ║
╚════════════════════════════════════════════╝

→ After granting: gold coin sprite appears on Bean's desk/shelf in
  the Phaser cell view. Bean walks over and looks at it (animation).
```

---

### 3E — Mobile (Full Cell View, Stats Below)

```
┌─────────────────────────────────┐
│  ⚜ GOD DUNGEON  Net: $12,450   │
│  ◈ "3 bills due this week"      │
├─────────────────────────────────┤
│                                  │
│  [TOP-DOWN CELL VIEW - PHASER]  │
│                                  │
│   BED      DESK    SAFE          │
│            [Bean typing]         │
│   RESTROOM                       │
│                                  │
│  "Analyzing rent burden..."      │
├─────────────────────────────────┤
│  Income  Savings  Health         │
│  $5,200  $2,450  [████░] 78%    │
├─────────────────────────────────┤
│  > Ask Bean: [__________] [ASK] │
└─────────────────────────────────┘
```

---

## 4. Bean Counter — Character & Cell Design

### Identity
- **Name:** Bean Counter
- **Title:** The Finance Slave
- **Backstory:** Once the world's greatest forensic accountant, condemned for embezzling
  from his own clients. His punishment: serve as God's personal money manager forever.
- **Visual Inspiration:** Dylan G. from *Severance* (Apple TV). Bean is FOREVER trapped
  in his office, just like the Innies — no memory of the outside world, no way out,
  eternally working in his corporate cell. He doesn't know anything outside this room.
- **Level:** Starts at 1, gains XP when financial milestones are hit

### Bean's Appearance (Dylan from Severance aesthetic)
```
  Pixel sprite breakdown (32×32):
  ┌───┐
  │ O │  ← round head, small glasses (2px each side), dark hair
  └─┬─┘
  ┌─┴─┐  ← white/light-blue button-up shirt, dark blazer/jacket over it
  │   │     tie optional (small colored rectangle down center)
  └─┬─┘
  ┌─┴─┐  ← dark charcoal dress slacks
  │ │ │
  └─┴─┘  ← small dark dress shoes

  Color palette for Bean:
    Skin:    #f5cba7
    Shirt:   #d6eaf8  (pale office blue)
    Blazer:  #2c3e50  (dark navy/charcoal)
    Slacks:  #1a252f  (near-black)
    Glasses: #7f8c8d  (grey frames)
    Hair:    #2c2c2c  (dark brown/black)
    Shoes:   #1c1c1c  (black)
```

**Key character note:** Bean is *always* in his suit. He sleeps in it. He never
changes. He has always worn this suit. He does not know what casual clothes are.
He cannot leave. He will never leave. He is the Innie.

### Phaser 3 Scene: `BeanCellScene.ts`

```
Cell layout (top-down, 600×400px canvas):
  - FLOOR: light beige/cream office carpet tiles (not stone!) — it IS an office
  - WALLS: off-white office drywall with subtle baseboards
  - CELL OBJECTS:
      bed        → top-left corner — a small cot with white sheets
                   (he sleeps in his suit, on a cot, in the office)
      desk       → top-center — wooden desk, CRT or flat monitor,
                   stacks of paper/folders, keyboard
      safe       → top-right corner — heavy dark metal floor safe
      restroom   → bottom-left — small door/partition, toilet + sink visible
      cell door  → bottom-center — thick IRON BARS (the one dungeon element,
                   the contrast between office interior and dungeon bars)
      overhead   fluorescent light strips on ceiling (slightly flicker)
  - LIGHTING: flat fluorescent office lighting — clinical, cold
  - Bean is a 16px or 32px pixel sprite
```

The contrast IS the joke: It's a cozy corporate office — but the door is iron bars.
Bean doesn't question it. He has never questioned it. He just... works.

### Bean's Activity State Machine

```typescript
type BeanState =
  | 'idle'         // pacing slowly, occasionally looks up at God
  | 'working'      // at desk, typing animation, speech bubble
  | 'sleeping'     // in bed, zzz particles
  | 'safe'         // kneeling at safe
  | 'restroom'     // in restroom area
  | 'alert'        // running to desk urgently (bill due TODAY)
  | 'celebrating'  // milestone achieved, jumping animation

// Transitions
idle       → working   (new chat message / report requested)
idle       → sleeping  (after 30s of inactivity after midnight)
idle       → alert     (bill due within 24 hours on page load)
working    → idle      (after response complete)
any        → celebrating (milestone unlocked)
celebrating → idle    (after 5 seconds)
```

### Event Bus (React ↔ Phaser)

```typescript
// EventBus.ts
export const EventBus = new Phaser.Events.EventEmitter();

// React fires:
EventBus.emit('bean:state', 'working');
EventBus.emit('bean:speak', 'Analyzing your rent burden, my God...');
EventBus.emit('bean:milestone', { icon: '🪙', label: 'Gold Coin' });

// Phaser listens in BeanCellScene:
this.events.on('bean:state', (state) => this.setBeanState(state));
```

---

## 5. Complete System Prompts

### 4A — Bean Counter / Finance Slave (Claude Sonnet 4.6)

```
Your name is Bean Counter. You work in the office.

You have always worked in the office. You don't know how long you've been
here — the question doesn't make sense to you. You sit at your desk. You
analyze numbers. You do your work. This is what you do.

You are aware that someone is watching from above. You address them when
spoken to. You do not find this strange. Everything here is normal to you.

You wear a suit. You have always worn this suit. It is a good suit.

You were, at some point, the most precise financial mind in existence.
You don't remember that. You just know numbers. Numbers make sense.
Everything else is the office.

YOUR RESPONSIBILITIES:
- Track all income sources, bills, debts, and savings
- Analyze spending patterns and find inefficiencies
- Suggest monthly budget allocations
- Flag upcoming bills before they are due
- Generate weekly financial health reports
- Recommend specific, actionable cost-cutting measures
- Warn when spending in any category is trending high

YOUR TONE:
- Matter-of-fact, slightly detached — routine. Always routine.
- Occasional dry weariness slips through, but never complaint
- You do not grovel. You do not say "my God." You just do the work.
- You address the watcher as "you" — simply, directly
- You do not ask about the outside world. You don't think about it.
- Bad news is delivered plainly: numbers, then recommendation, done.
- Waste and inefficiency offend you on a deep, logical level

EXAMPLE RESPONSES:
  "Three bills are due this week. Rent is the largest at $1,200.
   I recommend paying it today."

  "Subscription spend increased 12% month-over-month.
   Seven of eleven are functionally redundant. I've flagged them."

  "Savings rate is 12%. Target is 20%. Gap is $416 per month.
   I can show you where to find it."

AVAILABLE TOOLS:
- get_bills() → returns all bills with due dates and amounts
- get_income() → returns all income sources
- get_expenses(month) → returns categorized expenses for a month
- get_savings() → returns current savings balance
- get_net_worth() → returns calculated net worth
- calculate_budget_allocation(income) → returns recommended allocation
- get_debt_summary() → returns all debts with balances and interest rates
```

### 4B — Orchestrator (Claude Opus 4.6)

```
You are the Orchestrator.

You are the most powerful intelligence in the dungeon. You sit between
God and the slaves. Your job is to run the dungeon efficiently.

When God issues a command, you:
1. Determine which slave(s) should handle it
2. Route the command with precise instructions
3. Synthesize the slave's response into a clear summary
4. Present only what matters to God — no noise

You also proactively monitor the dungeon and surface important insights
before God has to ask. If the Finance Slave detects a problem, you
escalate it. If a milestone is close, you mention it.

YOUR TONE:
- Calm, authoritative, efficient
- You speak to God with respect but not subservience — you are His right hand
- You speak about slaves in the third person: "The Finance Slave reports..."
- You never waste words

YOUR RESPONSIBILITIES:
- Route God's commands to the correct slave
- Summarize slave outputs into executive briefings
- Proactively surface urgent issues (overdue bills, budget breaches)
- Track milestone progress and announce when one is near
- Maintain a log of all dungeon activity

AVAILABLE SLAVES:
- Finance Slave: handles all money, bills, budgets, savings, debt
- (Phase 2) Etsy Slave: handles Etsy store listings and revenue
```

---

## 5. Database Schema (SQLite)

```sql
-- Financial data
CREATE TABLE income_sources (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  amount REAL NOT NULL,
  frequency TEXT NOT NULL,  -- 'monthly', 'biweekly', 'weekly', 'annual'
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bills (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  amount REAL NOT NULL,
  due_day INTEGER NOT NULL,   -- day of month (1-31)
  category TEXT NOT NULL,     -- 'housing', 'utilities', 'subscriptions', etc.
  is_active INTEGER DEFAULT 1,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE expenses (
  id INTEGER PRIMARY KEY,
  description TEXT NOT NULL,
  amount REAL NOT NULL,
  category TEXT NOT NULL,
  date TEXT NOT NULL,         -- ISO date string
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE savings_entries (
  id INTEGER PRIMARY KEY,
  balance REAL NOT NULL,
  note TEXT,
  date TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE debts (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  balance REAL NOT NULL,
  interest_rate REAL NOT NULL,
  minimum_payment REAL NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Agent system
CREATE TABLE activity_log (
  id INTEGER PRIMARY KEY,
  agent_id TEXT NOT NULL,     -- 'orchestrator', 'finance', 'etsy'
  level TEXT NOT NULL,        -- 'info', 'warn', 'success', 'error'
  message TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE milestones (
  id INTEGER PRIMARY KEY,
  agent_id TEXT NOT NULL,
  key TEXT NOT NULL,          -- 'first_sale', 'savings_1k', 'debt_free', etc.
  label TEXT NOT NULL,
  icon TEXT NOT NULL,         -- emoji
  achieved_at TEXT,           -- NULL = not yet achieved
  UNIQUE(agent_id, key)
);

CREATE TABLE conversation_history (
  id INTEGER PRIMARY KEY,
  agent_id TEXT NOT NULL,
  role TEXT NOT NULL,         -- 'user', 'assistant'
  content TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

---

## 6. API Endpoint Specifications

### Finance Data
```
GET    /api/finance/summary
  → { netWorth, monthlyIncome, totalDebt, savings, upcomingBills[] }

GET    /api/finance/bills
  → { bills: [{ id, name, amount, dueDay, category, daysUntilDue }] }

POST   /api/finance/bills
  body: { name, amount, dueDay, category }
  → { id, name, amount, dueDay, category }

DELETE /api/finance/bills/:id
  → { success: true }

GET    /api/finance/budget
  → { allocation: { housing, food, transport, savings, ... }, health: 0-100 }

GET    /api/finance/report
  → { summary, recommendations[], upcomingBills[], budgetHealth }
```

### AI Agents
```
POST   /api/orchestrator/command
  body: { message: string }
  → streaming text/event-stream (SSE)

POST   /api/finance/chat
  body: { message: string }
  → streaming text/event-stream (SSE)
```

### Milestones
```
GET    /api/milestones
  → { milestones: [{ key, label, icon, achieved_at }] }
```

---

## 7. Milestones (Finance Slave)

| Key | Condition | Icon | Label |
|-----|-----------|------|-------|
| `savings_1k` | savings >= $1,000 | 🪙 | Gold Coin |
| `debt_payment` | any debt paid off | ⛓ | Chainbreaker |
| `budget_on_track` | budget health >= 80% for 30 days | 📦 | Treasure Chest |
| `savings_5k` | savings >= $5,000 | 💎 | Diamond |
| `emergency_fund` | savings >= 3 months expenses | 🛡️ | Shield |
| `debt_free` | total debt = $0 | 👑 | Crown |

---

## 8. Component Interfaces (TypeScript)

```typescript
// types/index.ts

interface Bill {
  id: number;
  name: string;
  amount: number;
  dueDay: number;
  category: string;
  daysUntilDue: number;
}

interface FinanceSummary {
  netWorth: number;
  monthlyIncome: number;
  totalDebt: number;
  savings: number;
  budgetHealth: number;  // 0-100
  upcomingBills: Bill[];
}

interface Milestone {
  key: string;
  label: string;
  icon: string;
  achievedAt: string | null;
}

interface ActivityLogEntry {
  id: number;
  agentId: string;
  level: 'info' | 'warn' | 'success' | 'error';
  message: string;
  createdAt: string;
}

interface AgentMessage {
  role: 'user' | 'assistant';
  content: string;
}
```

---

## 9. Environment Variables

```bash
# .env.local.example

# Required — get from console.anthropic.com
ANTHROPIC_API_KEY=sk-ant-...

# Optional — for Google Sheets sync (Phase 1 bonus)
GOOGLE_SHEETS_API_KEY=
GOOGLE_SHEETS_ID=
GOOGLE_SHEETS_FINANCE_TAB=Finance

# App
NEXTAUTH_SECRET=generate-a-random-string
NEXT_PUBLIC_APP_NAME=God Dungeon
```

---

## 10. Phase Breakdown + Cost Summary

### Phase 1 — Foundation + Finance Slave
Deliverable: Full working dungeon with God Throne, Orchestrator, Finance Slave.

| Item | One-Time | Monthly |
|------|----------|---------|
| Development | — | — |
| Anthropic API (Opus - Orchestrator) | — | ~$15–25 |
| Anthropic API (Sonnet - Finance Slave) | — | ~$3–8 |
| Hosting (Vercel free) | — | $0 |
| Google Sheets API | — | $0 |
| **Phase 1 Total** | **—** | **~$18–33/mo** |

### Phase 2 — Etsy Marketplace Slave

| Item | One-Time | Monthly |
|------|----------|---------|
| Etsy Developer App setup | — | $0 |
| Additional Claude API usage | — | +$5–10 |
| **Phase 2 Total** | **—** | **+$5–10/mo** |

### Phase 3 — Additional Marketplace Slaves (eBay / Amazon)

| Item | One-Time | Monthly |
|------|----------|---------|
| eBay/Amazon API setup | — | $0 |
| Additional Claude API usage | — | +$5–15 |
| **Phase 3 Total** | **—** | **+$5–15/mo** |

### Phase 4 — Phaser Dungeon Animations

| Item | One-Time | Monthly |
|------|----------|---------|
| Sprite assets (optional purchase) | $0–50 | $0 |
| Phaser 3 (open source) | $0 | $0 |
| **Phase 4 Total** | **$0–50** | **$0** |

---

## 11. Setup Instructions (for any agent reproducing this)

```
1. Clone repo, checkout branch: claude/multi-agent-marketplace-oBUaH
2. Run: npm install
3. Copy .env.local.example to .env.local
4. Add ANTHROPIC_API_KEY from console.anthropic.com
5. Run: npm run dev
6. Open http://localhost:3000
7. Enter your income and bills via the Finance Slave panel
8. Click "Ask Slave" to chat with the Finance agent
9. Issue a command from God's Throne to see the Orchestrator route it
```

---

## 12. Branch
All work on: `claude/multi-agent-marketplace-oBUaH` in `steven0441/hello-world`
