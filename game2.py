#!/usr/bin/env python3
"""
╔════════════════════════════════════╗
║        ⚔  AMAN'S DRAGONKEEP  ⚔     ║
║        Rise of the Last Hero       ║
╚════════════════════════════════════╝
"""

import time, random, sys, os

# ── Auto-install rich ──────────────────────────────────────────────────
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich import box
    from rich.prompt import Prompt
    from rich.align import Align
except ImportError:
    print("Installing rich library...")
    os.system(f"{sys.executable} -m pip install rich --quiet")
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich import box
    from rich.prompt import Prompt
    from rich.align import Align

console = Console()

# ════════════════════════════════════════════════════════
#  GAME DATA
# ════════════════════════════════════════════════════════

CLASSES = {
    "1": {
        "name": "Warrior",
        "hp": 130, "attack": 16, "defense": 9, "magic": 2,
        "desc": "Strong and resilient. High HP and defense.",
        "color": "bold red", "emoji": "⚔",
        "start": "iron_sword",
        "special": "cleave",
    },
    "2": {
        "name": "Mage",
        "hp": 75, "attack": 6, "defense": 3, "magic": 24,
        "desc": "Master of arcane arts. High magic, fragile body.",
        "color": "bold cyan", "emoji": "✦",
        "start": "mana_crystal",
        "special": "arcane_bolt",
    },
    "3": {
        "name": "Rogue",
        "hp": 95, "attack": 14, "defense": 5, "magic": 5,
        "desc": "Swift and deadly. High critical hit chance.",
        "color": "bold green", "emoji": "✦",
        "start": "health_potion",
        "special": "backstab",
    },
}

ITEMS = {
    # ── BRUTAL: heal values cut roughly in half, prices raised ──
    "health_potion":  {"name": "Health Potion",   "type": "consumable", "effect": "heal",   "value": 20, "buy": 22, "color": "red"},
    "grand_elixir":   {"name": "Grand Elixir",    "type": "consumable", "effect": "heal",   "value": 45, "buy": 50, "color": "bright_red"},
    "mana_crystal":   {"name": "Mana Crystal",    "type": "consumable", "effect": "boost",  "value": 8,  "buy": 28, "color": "blue"},
    "iron_sword":     {"name": "Iron Sword",       "type": "weapon",     "effect": "attack", "value": 5,  "buy": 25, "color": "white"},
    "magic_staff":    {"name": "Magic Staff",      "type": "weapon",     "effect": "magic",  "value": 8,  "buy": 30, "color": "magenta"},
    "leather_armor":  {"name": "Leather Armor",    "type": "armor",      "effect": "defense","value": 3,  "buy": 20, "color": "yellow"},
    "dragon_fang":    {"name": "Dragon Fang",      "type": "key_item",   "effect": None,     "value": 0,  "buy": 0,  "color": "gold1"},
}

# ── BRUTAL: all enemies hit harder, more HP, higher defense ──
ENEMIES = {
    "goblin":      {"name": "Forest Goblin",     "hp": 65,  "attack": 16, "defense": 4,  "xp": 25,  "gold": 8,   "color": "green",        "taunt": "Heh heh heh! You die here, outsider!"},
    "skeleton":    {"name": "Dungeon Skeleton",   "hp": 90,  "attack": 20, "defense": 8,  "xp": 38,  "gold": 12,  "color": "white",        "taunt": ""},
    "dark_knight": {"name": "Dark Knight Vorvan","hp": 120, "attack": 28, "defense": 15, "xp": 75,  "gold": 22,  "color": "bright_black", "taunt": "You are not worthy of this dungeon, mortal."},
    # ── CHANGE 1: Dragon renamed to Soman ──
    "dragon":      {"name": "Soman",             "hp": 300, "attack": 38, "defense": 18, "xp": 300, "gold": 100, "color": "bold red",     "taunt": "Another mortal. Another corpse for my collection."},
}

SHOP_STOCK = ["health_potion", "grand_elixir", "leather_armor", "mana_crystal"]

# ════════════════════════════════════════════════════════
#  PLAYER
# ════════════════════════════════════════════════════════

class Player:
    def __init__(self, name, cls_key):
        c = CLASSES[cls_key]
        self.name      = name
        self.cls_name  = c["name"]
        self.cls_color = c["color"]
        self.special   = c["special"]
        self.hp        = c["hp"]
        self.max_hp    = c["hp"]
        self.attack    = c["attack"]
        self.defense   = c["defense"]
        self.magic     = c["magic"]
        self.xp        = 0
        self.level     = 1
        self.gold      = 50           # BRUTAL: less starting gold
        self.inventory = {}
        self.equip_bonus_atk = 0
        self.equip_bonus_def = 0
        self.add_item(c["start"])

    def add_item(self, key, qty=1):
        self.inventory[key] = self.inventory.get(key, 0) + qty

    def remove_item(self, key, qty=1):
        self.inventory[key] = self.inventory.get(key, 0) - qty
        if self.inventory[key] <= 0:
            del self.inventory[key]

    def has_item(self, key):
        return self.inventory.get(key, 0) > 0

    def is_alive(self):
        return self.hp > 0

    def heal(self, amount):
        gained = min(amount, self.max_hp - self.hp)
        self.hp += gained
        return gained

    def take_damage(self, raw):
        dmg = max(1, raw - self.defense - self.equip_bonus_def)
        self.hp = max(0, self.hp - dmg)
        return dmg

    def total_attack(self):
        return self.attack + self.equip_bonus_atk

    def gain_xp(self, amount):
        self.xp += amount
        leveled = False
        while self.xp >= self.level * 65:
            self.xp -= self.level * 65
            self.level  += 1
            self.max_hp += 18
            self.hp      = min(self.hp + 18, self.max_hp)
            self.attack  += 3
            self.defense += 1
            self.magic   += 3
            leveled = True
        return leveled

    def show_stats(self):
        tbl = Table(box=box.ROUNDED, border_style="yellow", show_header=False, padding=(0, 2))
        tbl.add_column("k", style="dim yellow", width=10)
        tbl.add_column("v")
        tbl.add_row("Name",    f"[bold]{self.name}[/bold]")
        tbl.add_row("Class",   f"[{self.cls_color}]{self.cls_name}[/{self.cls_color}]")
        tbl.add_row("Level",   f"[yellow]{self.level}[/yellow]   XP {self.xp} / {self.level * 65}")
        tbl.add_row("HP",      f"[red]{self.hp}[/red] / {self.max_hp}  {hp_bar(self.hp, self.max_hp)}")
        tbl.add_row("Attack",  f"[red]{self.total_attack()}[/red]")
        tbl.add_row("Defense", f"[blue]{self.defense + self.equip_bonus_def}[/blue]")
        tbl.add_row("Magic",   f"[cyan]{self.magic}[/cyan]")
        tbl.add_row("Gold",    f"[gold1]{self.gold} 🪙[/gold1]")
        console.print(tbl)


# ════════════════════════════════════════════════════════
#  UI HELPERS
# ════════════════════════════════════════════════════════

def hp_bar(cur, max_hp, w=18):
    filled = int((cur / max_hp) * w) if max_hp else 0
    empty  = w - filled
    col    = "green" if cur > max_hp * 0.5 else ("yellow" if cur > max_hp * 0.25 else "red")
    return f"[{col}]{'█' * filled}[/{col}][dim]{'░' * empty}[/dim]"

def slow(text, delay=0.022):
    for ch in text:
        console.print(ch, end="", highlight=False)
        sys.stdout.flush()
        time.sleep(delay)
    console.print()

def pause(s=1.2):
    time.sleep(s)

def divider(col="yellow"):
    console.print(f"[dim {col}]{'─' * 58}[/dim {col}]")

def chapter_header(title, sub=""):
    console.clear()
    console.print()
    body = f"[bold yellow]{title}[/bold yellow]"
    if sub:
        body += f"\n[dim italic]{sub}[/dim italic]"
    console.print(Align.center(Panel(body, border_style="yellow", padding=(1, 6))))
    console.print()
    pause(0.9)

def narrate(text):
    styled_text = f"[dim italic]{text}[/dim italic]"
    console.print("\n  ", end="")
    slow(styled_text)

def say(speaker, text, col="white"):
    console.print(f"\n  [bold {col}]{speaker}:[/bold {col}] ", end="")
    slow(text)
    pause(0.4)

def pick(options):
    console.print()
    for i, opt in enumerate(options, 1):
        console.print(f"  [bold yellow][{i}][/bold yellow]  {opt}")
    console.print()
    return Prompt.ask("  [bold]Choose[/bold]", choices=[str(i) for i in range(1, len(options)+1)], show_choices=False)

def show_inventory(player):
    if not player.inventory:
        console.print("\n  [dim]— Bag is empty —[/dim]")
        return
    tbl = Table(box=box.SIMPLE, header_style="bold yellow", padding=(0, 1))
    tbl.add_column("Item")
    tbl.add_column("Qty", justify="center", width=4)
    tbl.add_column("Type", style="dim")
    for key, qty in player.inventory.items():
        it = ITEMS[key]
        tbl.add_row(f"[{it['color']}]{it['name']}[/{it['color']}]", str(qty), it["type"])
    console.print(tbl)


# ════════════════════════════════════════════════════════
#  COMBAT ENGINE
# ════════════════════════════════════════════════════════

def combat(player, enemy_key, can_flee=True):
    """
    Returns:
        'win'  — player defeated enemy
        'flee' — player escaped
        'lose' — player died
    """
    e    = ENEMIES[enemy_key].copy()
    e_hp = e["hp"]
    name = e["name"]
    col  = e["color"]

    console.clear()
    console.print()
    console.print(Align.center(Panel(
        f"[bold red]⚔   BATTLE BEGINS  ⚔[/bold red]\n[{col}]{name}[/{col}]",
        border_style="red", padding=(0, 6)
    )))
    if e["taunt"]:
        say(name, e["taunt"], col)
    pause(0.6)

    round_num = 0
    while player.is_alive() and e_hp > 0:
        round_num += 1

        # ── Status ────────────────────────────────────────────
        console.print()
        divider("red")
        console.print(
            f"  [bold]{player.name}[/bold]  "
            f"HP [{('red' if player.hp < player.max_hp*0.3 else 'green')}]{player.hp:>3}[/] / {player.max_hp}  "
            f"{hp_bar(player.hp, player.max_hp)}"
        )
        console.print(
            f"  [{col}]{name}[/{col}]  "
            f"HP [{('red' if e_hp < e['hp']*0.3 else 'green')}]{e_hp:>3}[/] / {e['hp']}  "
            f"{hp_bar(e_hp, e['hp'])}"
        )
        divider("red")

        # ── Player turn ───────────────────────────────────────
        actions = ["⚔  Attack"]
        if player.special == "arcane_bolt":
            actions.append("🔮 Arcane Bolt  (magic)")
        elif player.special == "backstab":
            actions.append("🗡  Backstab  (high crit)")
        elif player.special == "cleave":
            actions.append("🪓 Cleave  (ignore armor)")
        actions.append("🎒 Use Item")
        if can_flee:
            actions.append("💨 Flee")

        act = pick(actions)
        chosen = actions[int(act) - 1]

        player_dealt = 0

        if "Attack" in chosen:
            crit = random.random() < 0.12
            raw  = player.total_attack() + random.randint(-2, 5)
            if crit: raw = int(raw * 1.75)
            dmg  = max(1, raw - e["defense"])
            e_hp -= dmg
            player_dealt = dmg
            tag = "[bold yellow]CRITICAL![/bold yellow] " if crit else ""
            console.print(f"\n  {tag}You strike [bold red]{dmg}[/bold red] damage!")

        elif "Arcane" in chosen:
            raw = player.magic + random.randint(2, 10)
            dmg = max(1, raw - max(0, e["defense"] - 5))
            e_hp -= dmg
            player_dealt = dmg
            console.print(f"\n  ✨ Arcane Bolt hits for [bold cyan]{dmg}[/bold cyan] magic damage!")

        elif "Backstab" in chosen:
            crit = random.random() < 0.42
            raw  = player.total_attack() + random.randint(0, 8)
            if crit: raw = int(raw * 2.1)
            dmg  = max(1, raw - e["defense"])
            e_hp -= dmg
            player_dealt = dmg
            tag = "[bold yellow]BACKSTAB CRIT![/bold yellow] " if crit else ""
            console.print(f"\n  {tag}Shadow strike deals [bold green]{dmg}[/bold green] damage!")

        elif "Cleave" in chosen:
            raw = player.total_attack() + random.randint(1, 7)
            dmg = max(1, raw)   # ignores defense
            e_hp -= dmg
            player_dealt = dmg
            console.print(f"\n  ⚡ Cleave bypasses armor! Deals [bold red]{dmg}[/bold red] raw damage!")

        elif "Item" in chosen:
            consumables = {k: v for k, v in player.inventory.items()
                           if ITEMS[k]["type"] == "consumable"}
            if not consumables:
                console.print("\n  [dim]No usable items![/dim]")
                pause(0.8)
                continue
            keys = list(consumables.keys())
            console.print()
            for i, k in enumerate(keys, 1):
                it = ITEMS[k]
                console.print(f"  [yellow][{i}][/yellow]  [{it['color']}]{it['name']}[/{it['color']}]  (qty: {consumables[k]})")
            ic = Prompt.ask("  Use", choices=[str(i) for i in range(1, len(keys)+1)], show_choices=False)
            chosen_key = keys[int(ic) - 1]
            item = ITEMS[chosen_key]
            if item["effect"] == "heal":
                gained = player.heal(item["value"])
                console.print(f"\n  You drink the {item['name']} — recovered [bold green]{gained}[/bold green] HP!")
            elif item["effect"] == "boost":
                player.attack += 4
                player.magic  += 4
                console.print(f"\n  Mana surges through your body! Attack & Magic [bold cyan]+4[/bold cyan]!")
            player.remove_item(chosen_key)
            pause(0.8)

        elif "Flee" in chosen:
            # BRUTAL: flee chance dropped from 50% to 30%
            if random.random() < 0.30:
                console.print("\n  [yellow]You slip away into the shadows...[/yellow]")
                pause(1)
                return "flee"
            else:
                console.print("\n  [red]No escape! They block your path![/red]")

        pause(0.5)

        # ── Enemy turn ────────────────────────────────────────
        if e_hp > 0 and player.is_alive():
            # BRUTAL: Soman fire breath every 2 rounds (was 3)
            if enemy_key == "dragon" and round_num % 2 == 0:
                raw_breath = random.randint(20, 32)
                dmg2 = player.take_damage(raw_breath + 10)
                console.print(f"\n  [bold red]🔥 FIRE BREATH![/bold red] [{col}]{name}[/{col}] scorches you! [red]{dmg2}[/red] damage!")
                pause(0.6)

            # BRUTAL: enemies can crit (20% chance)
            e_crit = random.random() < 0.20
            e_roll = e["attack"] + random.randint(-3, 5)
            if e_crit:
                e_roll = int(e_roll * 1.5)
            dmg = player.take_damage(e_roll)
            if e_crit:
                console.print(f"\n  [bold yellow]ENEMY CRIT![/bold yellow] [{col}]{name}[/{col}] hits you for [bold red]{dmg}[/bold red] damage!")
            else:
                console.print(f"\n  [{col}]{name}[/{col}] strikes you for [bold red]{dmg}[/bold red] damage!")
            pause(0.7)

    # ── Outcome ───────────────────────────────────────────
    console.print()
    if player.is_alive():
        leveled = player.gain_xp(e["xp"])
        player.gold += e["gold"]
        reward_text = f"[green]+{e['xp']} XP[/green]  [gold1]+{e['gold']} Gold 🪙[/gold1]"
        if leveled:
            reward_text += f"\n  [bold yellow]✦ LEVEL UP! You are now Level {player.level}! ✦[/bold yellow]"
        console.print(Panel(
            f"[bold green]✦  VICTORY  ✦[/bold green]\n\n  {reward_text}",
            border_style="green", padding=(1, 4)
        ))
        pause(1.8)
        return "win"
    else:
        console.print(Panel("[bold red]☠  You have fallen...[/bold red]", border_style="red"))
        pause(1.5)
        return "lose"


# ════════════════════════════════════════════════════════
#  SHOP
# ════════════════════════════════════════════════════════

def shop(player):
    chapter_header("The Wandering Merchant", "A hooded figure beckons from behind a rickety stall.")
    say("Merchant", "Ha! A live one. What a sight. Gold talks, traveler — so talk to me.", "yellow")

    while True:
        console.print(f"\n  [gold1]Your Gold: {player.gold} 🪙[/gold1]\n")
        tbl = Table(box=box.SIMPLE, header_style="bold yellow", padding=(0, 2))
        tbl.add_column("#",    width=3, style="dim")
        tbl.add_column("Item")
        tbl.add_column("Effect")
        tbl.add_column("Cost", justify="right")
        for i, key in enumerate(SHOP_STOCK, 1):
            it = ITEMS[key]
            tbl.add_row(str(i), f"[{it['color']}]{it['name']}[/{it['color']}]",
                        f"+{it['value']} {it['effect']}", f"[gold1]{it['buy']} 🪙[/gold1]")
        console.print(tbl)

        act = pick(["Buy an item", "Leave the shop"])
        if act == "2":
            say("Merchant", "Don't die out there. It's bad for business when my customers stop returning.", "yellow")
            break

        idx = int(Prompt.ask("  Buy which item?",
                             choices=[str(i) for i in range(1, len(SHOP_STOCK)+1)],
                             show_choices=False)) - 1
        key  = SHOP_STOCK[idx]
        cost = ITEMS[key]["buy"]
        if player.gold >= cost:
            player.gold -= cost
            player.add_item(key)
            console.print(f"\n  [green]Purchased {ITEMS[key]['name']}![/green]")
        else:
            console.print(f"\n  [red]Not enough gold! You need {cost} 🪙.[/red]")
        pause(0.8)


# ════════════════════════════════════════════════════════
#  STORY CHAPTERS
# ════════════════════════════════════════════════════════

def title_screen():
    console.clear()
    dragon_art = r"""
                / \  //\
   |\___/|      /   \//  \\
   /0  0  \__  /    //  | \ \
  /     /  \/_/    //   |  \  \
  @_^_@'/   \/_   //    |   \   \
  //_^_/     \/_ //     |    \    \
( //) |        \///      |     \     \
( / /) _|_ /   )  //       |      \     _\
( // /) '/,_ _ _/  ( ; -.   |    _ _\.-~        .-~~~^-.
(( / / )) ,-{        _      `-.|.-~-.           .~         `.
(( // / ))  '/\      /                 ~-. _ .-~      .-~^-.  \
(( /// ))      `.   {            }                   /      \  \
 (( / ))     .----~-.\        \-'                 .~         \  `. \^-.
            ///.----..>        \             _ -~             `.  ^-`  ^-_
              ///-._ _ _ _ _ _ _}^ - - - - ~                     ~-- ,.-~
"""
    console.print()
    console.print(Align.center(Text(dragon_art, style="bold red")))
    console.print(Align.center(Text("— welcome to the Dungeon!!!! —", style="bold yellow")))
    console.print()
    console.print(Align.center(Text("Soman the Undying. Save the realm.", style="italic dim")))
    console.print()
    console.print(Align.center(Panel(
        "[dim]  Chapter I   → Village of Aethon\n"
        "  Chapter II  → The Dark Forest\n"
        "  Chapter III → Dungeon of Drak'thar\n"
        "  Chapter IV  → The Dragon's Lair  [/dim]",
        border_style="dim yellow", title="[dim yellow]Journey[/dim yellow]"
    )))
    console.print()
    console.print(Align.center(Text("Press ENTER to begin your legend...", style="blink bold yellow")))
    input()


def create_character():
    chapter_header("Create Your Hero", "Who dares face the undying dragon?")

    name = Prompt.ask("  [bold yellow]Enter your hero's name[/bold yellow]")
    if not name.strip():
        name = "Stranger"

    console.print("\n  [bold yellow]Choose your class:[/bold yellow]\n")
    for k, c in CLASSES.items():
        console.print(
            f"  [bold yellow][{k}][/bold yellow]  [{c['color']}]{c['name']:10}[/{c['color']}]  {c['desc']}"
        )
        console.print(
            f"       HP [red]{c['hp']}[/red]  ATK [red]{c['attack']}[/red]  DEF [blue]{c['defense']}[/blue]  MAG [cyan]{c['magic']}[/cyan]\n"
        )

    cls = Prompt.ask("  [bold]Your class[/bold]", choices=["1", "2", "3"], show_choices=False)
    player = Player(name, cls)

    console.clear()
    console.print()
    console.print(Align.center(Panel(
        f"[bold green]✦  Hero Created  ✦[/bold green]\n\n"
        f"  Name : [bold]{player.name}[/bold]\n"
        f"  Class: [{player.cls_color}]{player.cls_name}[/{player.cls_color}]",
        border_style="green", padding=(1, 6)
    )))
    pause(1.8)
    return player


def chapter_village(player):
    chapter_header("Chapter I — The Village of Aethon", "A kingdom on the edge of ruin.")
    narrate("Smoke drifts from burned farmhouses on the road behind you.")
    narrate("The village of Aethon is barely alive — shuttered windows, empty streets, silence where there was once laughter.")
    narrate("A frail elder steps forward, lantern in hand.")

    # ── CHANGE 2: Elder renamed to Aman ──
    say("Elder Aman", f"You... you must be the one the stars spoke of. Welcome, {player.name}.", "gold1")
    say("Elder Aman", "Soman has woken three moons ago. He has scorched two villages already. We are next.", "gold1")
    say("Elder Aman", "His lair lies north — beyond the Dark Forest, past the Dungeon of Drak'thar. Many knights tried. None returned.", "gold1")

    act = pick([
        "Ask about the dragon's weakness",
        "Ask what lies in the forest",
        "Accept the quest without a word",
    ])

    if act == "1":
        say("Elder Aman", "Ancient texts say Soman has one weakness — his Undying Core. A gap beneath his left wing.", "gold1")
        say("Elder Aman", "Weaken him enough and his magical armor fractures. That is your window.", "gold1")
        player.gold += 15
        narrate("The elder presses 15 gold coins into your hand. You feel the weight of the world with them.")
    elif act == "2":
        say("Elder Aman", "Goblins. Dozens. They followed the dragon's wake and nest in those woods now.", "gold1")
        say("Elder Aman", "Move fast. Fight only when you must.", "gold1")
        player.gold += 8
        player.add_item("health_potion")
        narrate("He hands you a potion from his coat. 'Take this. You'll need it.'")
    else:
        narrate(f"You say nothing. You nod once. Elder Aman stares at you — then smiles. 'Good. Words waste time.'")
        player.gold += 5

    console.print()
    act2 = pick([
        "Visit the merchant before leaving",
        "Head directly to the Dark Forest",
    ])
    if act2 == "1":
        shop(player)

    narrate("You leave Aethon behind. The lantern-light of the elder fades at your back.")
    narrate("The Dark Forest looms ahead. The trees are wrong — too still, too black.")
    pause(1)


def chapter_forest(player):
    chapter_header("Chapter II — The Dark Forest", "No wind. No birds. Just the sound of your own footsteps.")
    narrate("The canopy closes over you like a fist. Twisted roots crack under your boots.")
    narrate("Something moves above you. Too fast.")

    say("??", "Heh heh... all alone in our forest, are we?", "green")
    narrate("A goblin drops from the branches — jagged blade, yellow eyes, rotten grin.")
    pause(0.5)

    result = combat(player, "goblin")
    if result == "lose":
        game_over(player)
        return "dead"

    if result == "flee":
        narrate("You flee through the trees. Your heart hammers. After a long detour, you return to the path.")
        result2 = combat(player, "goblin")
        if result2 != "win":
            game_over(player)
            return "dead"

    narrate("The goblin crumples. You catch your breath. The forest is quiet again — for now.")
    pause(0.5)

    narrate("Further down the path, half-buried under moss, you spot a weathered chest.")

    act = pick([
        "Open the chest carefully",
        "Kick it open — no time for caution",
        "Leave it alone — smells like a trap",
    ])

    if act == "1":
        narrate("You ease the lid up slowly. No trap. Inside: gold coins and a health potion.")
        player.gold += 25
        player.add_item("health_potion")
        console.print("  [green]Found 25 Gold and a Health Potion![/green]")
    elif act == "2":
        narrate("The lid explodes open. No trap — but you stub your toe on the latch.")
        player.gold += 25
        player.add_item("health_potion")
        player.take_damage(3)
        console.print(f"  [green]Found 25 Gold and a Health Potion![/green]  [red](-3 HP from the latch)[/red]")
    else:
        narrate("Wise. You walk past. A faint hiss from inside the chest suggests something was waiting.")

    pause(0.5)
    narrate("The trees thin. Ahead, carved into a hillside: a massive stone archway — the dungeon entrance.")
    narrate("Torchlight flickers inside. The smell of old death rolls out like a wave.")
    pause(1)
    return "ok"


def chapter_dungeon(player):
    chapter_header("Chapter III — Dungeon of Drak'thar", "Bones on the floor. Silence that breathes.")
    narrate("Every step echoes. Rust-streaked chains hang from the ceiling.")
    narrate("A figure in tattered armour lurches from the shadow — jaw unhinged in a silent scream.")

    result = combat(player, "skeleton")
    if result == "lose":
        game_over(player)
        return "dead"

    narrate("The skeleton shatters. Among the bone-dust you find a scrawled note:")
    console.print()
    console.print(Align.center(Panel(
        "[italic dim]\"The Knight Vorvan guards the inner gate.\n"
        "He does not sleep. He does not tire.\n"
        "He was the last hero — before the dragon broke him.\"[/italic dim]",
        border_style="dim", padding=(1, 3)
    )))
    pause(1.2)

    act = pick([
        "Search the dungeon's side corridors",
        "Press on to the inner gate immediately",
    ])

    if act == "1":
        narrate("You find a crumbling chamber with an altar pulsing faint blue light.")
        console.print()
        console.print("  [cyan]A warmth floods through you. The dungeon itself seems to resist the dragon's curse here.[/cyan]")
        healed = player.heal(35)
        console.print(f"  [green]Recovered {healed} HP![/green]")
        if player.cls_name == "Mage":
            player.magic += 6
            console.print("  [cyan]The arcane altar resonates with your class — Magic [bold]+6[/bold]![/cyan]")
        elif player.cls_name == "Warrior":
            player.defense += 2
            console.print("  [blue]Stone runes engrave themselves on your armor — Defense [bold]+2[/bold]![/blue]")
        pause(1)

    narrate("The iron gate groans as you force it open. Beyond: a vast hall, and at its center — a knight.")
    narrate("Twice your height. Plate armour fused to rotting flesh. Eyes like dying embers.")
    pause(0.6)

    say("Vorvan", "I was the best. The greatest warrior in the realm.", "bright_black")
    say("Vorvan", "And the dragon still broke me. What makes you think... you are different?", "bright_black")
    pause(0.3)

    act2 = pick([
        f"'I have nothing to lose.'",
        f"'The difference is — I'm going to win.'",
        "Say nothing. Let your weapon speak.",
    ])

    if act2 == "1":
        narrate("Vorvan's ember-eyes flicker. Something like sorrow crosses what's left of his face.")
    elif act2 == "2":
        narrate("A long silence. Then Vorvan raises his blade.")
        player.attack += 2
        console.print("  [yellow]Your defiance sharpens your focus! Attack +2![/yellow]")
    else:
        narrate("You draw your weapon. Vorvan tilts his head — and charges.")

    pause(0.5)
    result = combat(player, "dark_knight", can_flee=False)
    if result == "lose":
        game_over(player)
        return "dead"

    narrate("Vorvan crashes to the stone. His ember-eyes dim. For a moment, they seem... grateful.")
    say("Vorvan", "...Free...", "dim")
    narrate("The inner sanctum opens. A spiral staircase descends into searing heat.")
    console.print()
    # BRUTAL: reduced healing before final boss
    console.print("  [bold yellow]A cracked healing spring trickles at the staircase entrance.[/bold yellow]")
    healed = player.heal(20)
    console.print(f"  [green]Recovered {healed} HP before the final confrontation.[/green]")
    pause(1.2)
    return "ok"


def chapter_dragon(player):
    chapter_header("Chapter IV — The Dragon's Lair", "The air itself is burning.")
    narrate("The staircase opens into a cavern the size of a city.")
    narrate("A carpet of gold, charred bones, and broken swords stretches to the horizon.")
    narrate("And then — the ground shifts. And breathes.")
    pause(0.5)

    console.print()
    dragon_art = r"""
                / \  //\
   |\___/|      /   \//  \\
   /0  0  \__  /    //  | \ \
  /     /  \/_/    //   |  \  \
  @_^_@'/   \/_   //    |   \   \
  //_^_/     \/_ //     |    \    \
( //) |        \///      |     \     \
( / /) _|_ /   )  //       |      \     _\
( // /) '/,_ _ _/  ( ; -.   |    _ _\.-~        .-~~~^-.
(( / / )) ,-{        _      `-.|.-~-.           .~         `.
(( // / ))  '/\      /                 ~-. _ .-~      .-~^-.  \
(( /// ))      `.   {            }                   /      \  \
 (( / ))     .----~-.\        \-'                 .~         \  `. \^-.
            ///.----..>        \             _ -~             `.  ^-`  ^-_
              ///-._ _ _ _ _ _ _}^ - - - - ~                     ~-- ,.-~
"""
    console.print(Align.center(Text(dragon_art, style="bold red")))
    time.sleep(1)
    # ── CHANGE 1: dragon name shown as Soman ──
    console.print(Align.center("[bold red]S O M A N[/bold red]"))

    pause(1)
    say("Soman", "...", "bold red")
    pause(1)
    say("Soman", "A mortal. Here. In MY lair. It has been... decades since I've had a visitor.", "bold red")
    say("Soman", f"And you — what is your name, little creature? I like to remember those I've burned.", "bold red")

    act = pick([
        f"'{player.name}. And I'm here to end you.'",
        f"'I speak for the villages you destroyed. For Aethon.'",
        "Draw your weapon in silence.",
    ])

    if act == "1":
        say("Soman", "Ha. Courage. I respect it. It changes nothing — but I respect it.", "bold red")
        player.attack += 3
        console.print("  [bold yellow]Your defiance ignites your fury! Attack +3![/bold yellow]")
    elif act == "2":
        say("Soman", "...Aethon. I remember that one. The screaming was particularly musical.", "bold red")
        say("Soman", "Come then, hero of the people. Let me add your screams to the chorus.", "bold red")
    else:
        narrate("You say nothing. The silence stretches. Soman's eyes narrow.")
        say("Soman", "No words. Good. Words are wasted on the dead.", "bold red")

    pause(0.5)
    narrate("The dragon rears back. Fire blooms deep in his chest. The gold on the floor begins to melt.")
    narrate("This is it. The final battle. There is no going back.")
    pause(1)

    console.print()
    console.print(Align.center(Panel(
        "[dim]💡 TIP: Soman breathes fire every 2 rounds — it ignores armor.\n"
        "Enemies can critically hit you. Use your special and items wisely.[/dim]",
        border_style="dim", padding=(0, 4)
    )))
    pause(1.2)

    result = combat(player, "dragon", can_flee=False)
    ending(player, result == "win")


# ════════════════════════════════════════════════════════
#  ENDINGS
# ════════════════════════════════════════════════════════

def game_over(player):
    console.clear()
    console.print()
    console.print(Align.center(Panel(
        f"[bold red]☠   G A M E   O V E R   ☠[/bold red]\n\n"
        f"[white]{player.name} has fallen.\nThe darkness swallows another hero whole.\nSoman's laughter echoes across the realm.[/white]",
        border_style="red", padding=(2, 8)
    )))
    console.print()
    console.print(Align.center(Text("Run the game again to try once more.", style="dim")))
    console.print()


def ending(player, won):
    console.clear()
    console.print()
    if won:
        console.print(Align.center(Panel(
            "[bold yellow]★  ★  ★   V I C T O R Y   ★  ★  ★[/bold yellow]\n\n"
            "[white]Soman collapses.\n"
            "For the first time in three centuries,\n"
            "the dragon breathes no fire.\n\n"
            f"[bold]{player.name}[/bold] walks back into the light.\n"
            "The village of Aethon lights every lantern.\n"
            "The realm sings your name tonight — and forever.[/white]",
            border_style="gold1", padding=(2, 8)
        )))
        console.print()
        console.print(Align.center(Text("— FINAL STATS —", style="bold yellow")))
        console.print()
        player.show_stats()
    else:
        game_over(player)

    console.print()
    console.print(Align.center(Text("Thank you for playing DragonKeep ✦", style="italic dim")))
    console.print()


# ════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════

def main():
    title_screen()
    player = create_character()

    chapter_village(player)
    if not player.is_alive():
        return

    result = chapter_forest(player)
    if result == "dead" or not player.is_alive():
        return

    result = chapter_dungeon(player)
    if result == "dead" or not player.is_alive():
        return

    chapter_dragon(player)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[dim]  Interrupted. Farewell, hero. The realm still needs you.[/dim]\n")