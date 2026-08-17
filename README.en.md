# Echoes of Stardust · 星尘回响

> **Language: [English](/README.en.md) | [中文](/README.md)**

> Pixel-art narrative RPG · The farewell journey of the last Stardust Listener
> You travel across memory planets on the brink of extinction, help their memories fulfill final wishes, and play a dirge to send them into stardust.

The universe is a song coming to an end. What you play is not a requiem — it is testimony.

---

## 🔥 Legendary Settings That Make Your Heart Race

> These are the romance unique to Echoes of Stardust — written deep into the code.

### 🎼 Weaving Combat · The Four-Element Counterpoint Law

**J Wind · K Fire · L Water · I Earth** — what you play is not a skill, it is a **movement**.

- **Unison**: identical adjacent notes → +50% damage, pure resonance
- **Counterpoint Fusion**: fire × water → **steam mist**; wind × earth → **sandstorm**
- **Rest & Afterglow**: a note after a rest → damage **×2** — the power of silence

### ⭐ The Ten Memorized Melodies · Legendary Finishers

Witness the stories, then write your **unforgettable memories** into the staff as note sequences to play a legend:

| Memorized Melody | Effect |
|---|---|
| **Nibelungen in the Rainy Night** | Hidden for 15s · double movement |
| **Quasimodo's Bell** | Bronze bell blessing · death-immunity shield |
| **Do Not Go Gentle into That Good Night** | 200% damage · piercing burn |
| **The Letter to Eri** | Falling sakura — she received it |
| **The Answer of the Dark Forest** | Hidden 5s · next hit **×10** |
| **Ango's Revenge** | Folding-knife form · 300% damage |
| **The Unfinished Poem** | Poem-verse form · the enemy leaves on its own |
| **The Lone Traveler's Lantern** | Become a lighthouse for 20s |
| **Dance of the Broken Mirror** | Mirror reflection · bond-shared damage |
| **The Name in the Flower Field** | A guardian spirit appears |

### 🌀 Listening · The Slow-Motion Weakness

Hold **U** — time slows to **30%**. The enemy's rhythm pattern is laid bare on the staff. At that moment you are not just a musician; you are the **seer**.

### 🌌 Memory Planets · Dying Means a Dirge

Every planet is a memory. Advance through **Story / Interaction / Fragments / Listening**; at 100%, play the dirge and the planet turns to stardust. Everyone you bid farewell is someone who refused to be forgotten.

### 🪐 16 Planets · 5 Main Chapters + Free Exploration

Shallows Star → Storm Shadowed City → Notre-Dame → Dimensionally-reduced Ruins → Journey of the Finale. After the 5 chapters, unlock free exploration of 16 planets: Qiantang Temple, Kassel, the Library, Math Wasteland, B-612… each with its own story and NPCs.

---

## ✨ Core Gameplay

- **Free Exploration**: Stardew Valley-style top-down map, WASD to move, press E / click / number keys near exploration points
- **Weaving Combat**: J/K/L/I play four elemental notes (Wind/Fire/Water/Earth) fired in a direction; reproduce the enemy's rhythm pattern to trigger Resonance
- **Improvised Finale**: after 3 spirit rhymes, press Space to fill a score — 8-slot staff free composition; hitting the **Memorized Melody** triggers a legendary finisher
- **Memory Collection**: advance through Story / Interaction / Fragments / Listening; at 100% play the final dirge
- **Save System**: auto-save + **manual save with Ctrl+S**; continue from the title screen via "Continue Listening"
- **All-Night Atmosphere**: every scene shares a unified night mood with dynamic stardust, meteors, a black hole, and a musical staff
- **Character Animation**: 4-direction walking animation for the player; NPC action state machines (fishing / reading / writing / shell-picking / tentacle swaying, etc.)
- **Ambient Sound**: Wind/Fire/Water/Earth keys trigger matching ambient audio (gust / flame / splash / rockslide) plus note feedback

## 🎮 Controls

| Scene | Controls |
|---|---|
| Title Screen | ↑↓ select · Enter confirm · F11 fullscreen |
| Planet Select | ↑↓ select · Enter land · Mouse click |
| Map | WASD move · E / mouse / number keys interact · ESC back |
| Local Scene | WASD to NPC · E talk · walk near to trigger |
| Dialogue | Enter advance · S skip · ESC back |
| Battle | WASD move (sets firing direction) · J/K/L/I play · U listen · Space finale |
| Global | Ctrl+S manual save · F11 fullscreen toggle |

> Keep your input method in English mode — a Chinese IME will swallow key presses.

## 🚀 Install & Run

**Requirements**: Windows 10/11 · Python 3.10+ · any GPU (runs fine without GPU, auto-degrades)

### Step 1: Install Python

Download Python 3.10+ from [python.org](https://www.python.org/downloads/).
**Make sure to check "Add Python to PATH"** during installation.

### Step 2: Download & Extract

```bash
git clone https://github.com/jhk0721/echoes-of-stardust.git
cd echoes-of-stardust
```

Or click the green **Code → Download ZIP** button on the repo page and extract.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt    # just pygame
```

### Step 4: Launch

```bash
python run.py                      # first run auto-generates assets + sets MX150 GPU
```

Or simply double-click **`启动游戏.bat`**.

> Tip: if the .bat flashes and closes, use `python run.py` instead — the console will show the error.

### Assets Note

The first run auto-generates all SFX/BGM/planet textures (purely procedural, no downloads needed).
The Kenney asset packs in `assets/` are optional enhancements — the game runs fine without them.

## 🧪 Tests

```bash
python -m tools.smoke_test   # battle loop self-check
python -m tools.map_test     # exploration map full-flow self-check
python -m tools.story_test   # story full-flow self-check
python -m tools.walk_test    # local scene movement self-check
python -m tools.worlds_test  # 16-planet data integrity self-check
```

## 📁 Project Structure

```
core/
├── main.py            # Entry: scene management / title screen / weaving battle
├── config.py          # Central config (paths / colors / keys / battle params)
├── scene_manager.py   # Scene stack management (push/pop/replace/transitions)
├── audio.py           # Procedural SFX + BGM + ambient sounds
├── save.py            # Save system
├── combat/            # Rhythm judge / spirit rhymes / improvised finale
└── story/             # Story scene system
    ├── scene.py       # Dialogue / interaction / battle / dirge
    ├── map_scene.py   # Exploration map (night)
    ├── walk_scene.py  # Local scenes (4-dir animation + NPC FSM)
    ├── planet_select.py # Planet selection
    ├── planet.py      # Story data for 16 planets
    ├── ut.py          # Undertale-style sprite adapter
    └── sd.py          # Stardew Valley asset adapter
tools/                 # Tests & asset generation
native/                # Planet rendering shaders
```

## 🗺 Current Progress

- [x] Title screen (dynamic cosmic movement: stardust / meteors / staff / black hole)
- [x] Tutorial + free exploration map (6 POIs)
- [x] Chapter 1 · Shallows Star "The Boat" full story (dialogue / interaction / battle / fragments / dirge)
- [x] Weaving combat (Resonance / spirit rhymes / improvised / 10 Memorized Melody finishers)
- [x] Save system
- [x] **Planet select screen (all 16 planets landable)**
- [x] Main story 5 chapters: Shallows Star → Storm Shadowed City → Notre-Dame → Dimensionally-reduced Ruins → Journey of the Finale
- [x] Free exploration of 11 planets (Qiantang Temple / Kassel / Friends / Library / Ward / Math Wasteland / To Live / Ditan / Paper Boat / Sea / B-612)
- [x] All-night atmosphere + player 4-dir animation + NPC action FSMs
- [x] Ambient sound (Wind/Fire/Water/Earth) + fishing-net rising animation & particles
- [x] Dialogue auto-wrap / pagination / fullscreen adaptive
- [x] Story chapters: Storm Shadowed City, Notre-Dame, Dimensionally-reduced Ruins, Finale with 4-choice endings
- [ ] Stardust Book codex / Luoshui Bridge easter egg

## 📜 Asset Licenses

| Asset | Source | License |
|---|---|---|
| Fusion Pixel font | TakWolf (GitHub) | OFL-1.1 |
| Particles / UI / SFX / Music | Kenney.nl | CC0 |
| Harp PNG | pngimg.com | CC BY-NC 4.0 (non-commercial) |
| RPG tile pack | Kenney.nl | CC0 |
| Procedural assets (SFX/BGM/planets) | Generated by this project | MIT with project |

> This is a local learning project — non-commercial, not published. All assets are used under their respective licenses. If there are any infringements, please contact me (personal email: <jhk0721@163.com>).

*Poetry written, clouds risen. The universe is a song coming to an end, and you are seeing off every single note.*