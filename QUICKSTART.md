# God Dungeon — Quickstart

## What is this?
A gothic finance command center. You are God. Below you is **Bean Counter** — a condemned accountant trapped forever in his office cell (think Dylan from Severance). He manages your money. He answers your questions. He never leaves.

---

## Requirements
- [Node.js 18+](https://nodejs.org) — download the LTS version
- An [Anthropic API key](https://console.anthropic.com) — free to create

---

## Setup (5 minutes)

### 1. Download the code
```bash
git clone https://github.com/steven0441/hello-world.git
cd hello-world
git checkout claude/multi-agent-marketplace-oBUaH
```

### 2. Install dependencies
```bash
npm install
```

### 3. Add your API key
```bash
cp .env.local.example .env.local
```
Open `.env.local` and replace `sk-ant-...` with your key from [console.anthropic.com](https://console.anthropic.com) → API Keys → Create Key

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 4. Run it
```bash
npm run dev
```

### 5. Open your browser
```
http://localhost:3000
```

---

## Using the Dungeon

| Area | What it does |
|------|-------------|
| **♕ God's Throne** (top bar) | Type a command and hit DECREE — the Orchestrator routes it |
| **◈ Orchestrator** | Claude Opus — manages the dungeon, briefs you on what's happening |
| **⛓ Bean's Cell** | Watch Bean walk around his office. He types, paces, panics when bills are due |
| **Ask Bean** | Chat directly with the Finance Slave about your money |
| **Bills panel** | See upcoming bills, add new ones, delete old ones |
| **Ledger** | Income, savings, debt, net worth, budget health |
| **Milestones** | Unlock achievements as you hit financial goals |

### Example commands to try:
- *"What bills are due this week?"*
- *"How is my budget looking?"*
- *"What should I cut to save more money?"*
- *"Give me a full financial report"*

---

## Want to use Ollama instead of the API? (Free, runs locally)

1. Install [Ollama](https://ollama.ai)
2. Run: `ollama pull llama3`
3. Open `src/config/agents.ts` and change the finance agent:
```typescript
finance: {
  backend: 'ollama',
  model: 'llama3',
}
```

---

## File structure
```
src/
├── app/
│   ├── page.tsx                    # Main dungeon UI
│   └── api/
│       ├── finance/
│       │   ├── summary/            # GET financial overview
│       │   ├── bills/              # GET/POST/DELETE bills
│       │   └── chat/               # POST — chat with Bean (streaming)
│       ├── orchestrator/command/   # POST — God's decree (streaming)
│       └── milestones/             # GET milestone progress
├── components/
│   ├── DungeonCell.tsx             # React wrapper for Phaser
│   └── phaser/
│       └── BeanCellScene.ts        # Bean's animated cell (Phaser 3)
├── config/
│   └── agents.ts                   # AI backend config + system prompts
├── lib/
│   ├── agent-client.ts             # Anthropic / Ollama / OpenAI adapter
│   ├── db.ts                       # SQLite setup + schema
│   └── finance.ts                  # Finance data helpers
└── types/
    └── index.ts                    # TypeScript interfaces
```

---

## Troubleshooting

**Bean's cell is blank / not loading**
- Wait 2-3 seconds — Phaser loads async
- Check browser console for errors

**"Invalid API key" error**
- Double-check your key in `.env.local`
- Make sure there are no spaces around the `=`
- Restart `npm run dev` after changing `.env.local`

**Port 3000 already in use**
```bash
npm run dev -- -p 3001
# then open http://localhost:3001
```

**Want to reset the demo data**
```bash
rm dungeon.db
npm run dev   # re-creates with fresh seed data
```
