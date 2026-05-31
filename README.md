# Terminal Games

A growing collection of Python terminal games — from classic board games to full RPG adventures. Each game runs entirely in your terminal with no GUI needed.

---

## 📂 Games

### ⚔️ DragonKeep — Rise of the Last Hero (`game.py`)

A story-driven terminal RPG with rich text rendering, turn-based combat, and branching dialogue.

**Features:**
- 3 playable classes — Warrior, Mage, Rogue — each with unique stats and a special ability
- 4 story chapters: Village → Forest → Dungeon → Dragon's Lair
- Turn-based combat with specials, items, and flee mechanics
- In-game shop, inventory system, XP leveling
- Branching dialogue choices that affect combat stats
- Colorful UI powered by the `rich` library (auto-installs if missing)
- Final boss: Malachar the Undying

**Run:**
```bash
python3 game.py
```

---

### DragonKeep: Brutal Mode (`game2.py`)

A harder remix of DragonKeep with rebalanced enemies, nerfed healing, and a renamed final boss.

**Changes from `game.py`:**
- All enemies have higher HP, attack, and defense
- Healing items restored less; prices raised
- Starting gold reduced
- Dragon fire every 2 rounds instead of 3 (ignores armor)
- Final boss renamed to **Soman**

**Run:**
```bash
python3 game2.py
```

---

###  Tic Tac Toe (`tictactoe.py`)

A classic Tic Tac Toe with two modes — PvP and an unbeatable AI powered by the Minimax algorithm.

**Features:**
- Player vs Player mode
- Player vs AI with perfect Minimax decision making (you can't beat it, you can only draw)
- Malayalam-flavored prompts and funny random result messages
- Clean board rendering in the terminal

**Run:**
```bash
python3 tictactoe.py
```

---

## 🛠️ Requirements

| Game | Dependencies |
|------|-------------|
| `game.py` | Python 3.x, `rich` (auto-installed) |
| `game2.py` | Python 3.x, `rich` (auto-installed) |
| `tictactoe.py` | Python 3.x (stdlib only) |

---

## Getting Started

```bash
# Clone or download the repo, then just run any game:
python3 game.py        # DragonKeep (Normal)
python3 game2.py       # DragonKeep (Brutal)
python3 tictactoe.py   # Tic Tac Toe
```

---

## 🗺️ Roadmap

More games are on the way! This collection will keep growing. Planned additions may include:

- Snake
- Minesweeper
- Card games (Blackjack, etc.)
- Puzzle / word games
- And whatever else sounds fun to build

---

> Built for fun. Runs in your terminal. More coming soon.
