# God Dungeon — Art & Design Direction

> This document is for designers, artists, and AI image tools. It describes the full visual language of the dungeon — mood, references, character design, environment, and UI. Use the AI prompts at the end of each section to generate concept art in Midjourney, DALL-E, or Stable Diffusion.

---

## PART 1 — Mood, Vibe & Overall Aesthetic

### The Feeling
Imagine you're a surveillance camera mounted on the ceiling of a corporate office — except the office is inside a dungeon, and the person working there has been there for so long they've forgotten there's an outside world. Cold fluorescent light. Beige carpet. The faint sound of typing. Iron bars on the door.

This is not horror. It is not comedy. It is **mundane dread** — the kind that comes from normalcy taken too far. Bean Counter doesn't know he's trapped. He's just... at work.

The dungeon exterior — the frame around his cell, the God interface — is gothic and grand. Deep black, gold accents, glowing borders. It feels like a fantasy RPG villain's command center crossed with a Bloomberg terminal.

### Visual References
| Reference | What to steal from it |
|-----------|----------------------|
| **Severance** (Apple TV) | The office — clinical, beige, fluorescent. Workers who don't question anything |
| **Hades** (the game) | Dark UI with glowing accent colors, mythological grandeur, readable at a glance |
| **Papers Please** | Top-down bureaucratic dread, tiny character in a small room, watched from above |
| **Disco Elysium** | Rich dark UI, gothic serif fonts, text that feels ancient and important |
| **Bloomberg Terminal** | Dense financial data presented as if it matters more than everything |
| **Dungeon Keeper** | You are the evil overlord watching minions work from above |

### Two Worlds in One Screen

The screen is split into **two visual languages that should NOT match** — that contrast is the whole joke:

```
┌─────────────────────────────────────────────────────┐
│  GOTHIC DUNGEON UI  (dark, gold, purple, dramatic)  │  ← God's world
│  Cinzel font. Glowing borders. "CONDEMNED" badges.  │
├─────────────────────────────────────────────────────┤
│                                                      │
│   FLUORESCENT OFFICE  (beige, clinical, mundane)    │  ← Bean's world
│   Carpet tiles. Motivational poster. Iron bar door. │
│                                                      │
└─────────────────────────────────────────────────────┘
```

The god panels feel like a villain's lair. Bean's cell feels like a WeWork office in 2019. The iron bars are the only thing connecting the two.

---

## PART 2 — Color Palette

### God's Interface (The Dark Frame)

These colors are used for all UI panels OUTSIDE Bean's cell:

| Name | Hex | Looks Like | Used For |
|------|-----|-----------|----------|
| **Void** | `#080810` | Deep space, almost black with a blue tinge | Main background |
| **Abyss** | `#0f0f1a` | Slightly lighter void | Panel backgrounds |
| **Shadow** | `#1e1e2e` | Dark navy-grey | Panel borders, dividers |
| **Divine Gold** | `#f5c542` | Warm ancient gold, like candlelight | God's throne accent, crown ♕ |
| **Royal Purple** | `#9b59f5` | Deep electric purple | Orchestrator accent, ◈ symbol |
| **Hellfire Orange** | `#ff6b35` | Burning ember, not neon | Bean's cell frame, ⛓ chains |
| **Neon Green** | `#00ff88` | Matrix green, money green | Positive numbers, milestones achieved |
| **Alert Red** | `#ff4040` | Pure danger | Overdue bills, negative values |
| **Ghost White** | `#e2e8f0` | Off-white, slightly cool | Primary text |
| **Dungeon Grey** | `#4a5568` | Faded stone | Secondary text, labels |
| **Terminal Grey** | `#a0aec0` | Old CRT monitor text | Numbers, code, monospace content |

### Bean's Cell (The Office Interior)

These colors only appear INSIDE the Phaser canvas — Bean's cell:

| Name | Hex | Used For |
|------|-----|----------|
| **Office Carpet** | `#e8e0d0` | Floor tile base — warm beige |
| **Carpet Grid** | `#d4c9b0` | Subtle tile lines |
| **Drywall** | `#f0ebe0` | Walls — slightly warmer than white |
| **Baseboard** | `#c8b89a` | Where wall meets floor |
| **Desk Wood** | `#8b6914` | Bean's desk surface |
| **Monitor Dark** | `#1a1a2e` | Monitor bezel |
| **Monitor Screen** | `#0d4f8b` | Screen glow — deep blue |
| **Safe Metal** | `#2c3040` | Heavy dark floor safe |
| **Fluorescent** | `#f5f0e0` | Ceiling light strips — warm white |
| **Iron Bar** | `#2a2a2a` | Door bars — near black |
| **Bar Sheen** | `#606060` | Light reflection on bars |

### Glow Effects
Every panel border pulses with a soft glow matching its accent color:
```css
/* God's Throne */
box-shadow: 0 0 12px rgba(245, 197, 66, 0.25);

/* Orchestrator */
box-shadow: 0 0 12px rgba(155, 89, 245, 0.25);

/* Bean's Cell */
box-shadow: 0 0 12px rgba(255, 107, 53, 0.25);
```
The glow is subtle — a whisper, not a shout. Like something ancient quietly radiating power.

---

## PART 3 — Typography

### Font Stack
| Role | Font | Style | Feels Like |
|------|------|-------|-----------|
| **Titles / Headers** | Cinzel | Regular / Bold | Ancient Roman inscriptions. Eternal. Serious. |
| **Body text** | Inter | Regular | Clean, modern, readable |
| **Numbers / Terminal** | JetBrains Mono | Regular | Code editor. Financial terminal. Precise. |

### Usage Rules
- **DECREE** button, panel headers, milestone names → Cinzel, all-caps, wide letter-spacing
- All dollar amounts, dates, percentages → JetBrains Mono
- Bean's speech bubbles → monospace, small, slightly dim
- "CONDEMNED" badges → Cinzel, tiny, uppercase, orange

### Hierarchy Example
```
♕  GOD DUNGEON                    ← Cinzel 24px, gold
─────────────────────────────
◈ ORCHESTRATOR                    ← Cinzel 13px, purple, letter-spacing: 4px
"Finance slave reports 3 bills..." ← Inter 14px, ghost white
─────────────────────────────
⛓ BEAN COUNTER'S CELL            ← Cinzel 13px, orange
[CONDEMNED]                       ← Cinzel 8px, orange badge
Income    $5,200/mo               ← JetBrains Mono 14px
```

---

## AI Image Generation Prompts (Part 1)

Use these in Midjourney, DALL-E 3, or Stable Diffusion to generate concept art:

### Overall Dungeon UI Mood
```
dark gothic command center UI screenshot, deep black background, glowing gold 
and purple panel borders, ancient serif fonts, financial data displayed like 
a villain's war room, Bloomberg terminal meets fantasy RPG, dramatic lighting, 
near-black color palette with neon accent colors, professional concept art
```

### The Office-Inside-a-Dungeon Concept
```
top-down view of a small office room with beige carpet, fluorescent ceiling 
lights, wooden desk with CRT monitor, filing cabinet, safe, small cot in 
corner — but the only door is made of thick iron prison bars. Corporate 
mundane meets gothic dungeon. Isometric pixel art style. Warm office lighting 
contrasted with cold dark stone walls outside the bars.
```

### Mood Board — The Two Worlds
```
split screen concept art: left side is a dark gothic villain UI with gold 
glowing borders and purple accents, right side is a mundane fluorescent-lit 
beige office with carpet tiles and a desk — both are the same "room" viewed 
differently. Atmospheric concept art for a video game.
```
