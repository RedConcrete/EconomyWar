# EconomyWar 4 Player

A Warcraft III: The Frozen Throne custom map by **RedConcrete**.

4-player economy/base-defense map. Each player manages resources, builds defenses, and attacks opponents. Last base standing wins.

Current version: **v1.8.5**

---

## Repository Structure

```
src/           Text files — edit these directly
  war3map.j        Main JASS script (all game logic)
  war3map.wts      In-game text strings
  war3mapMisc.txt  Game constants (damage, range, etc.)
  war3mapSkin.txt  Unit/building skin overrides
  war3mapExtra.txt Extra map metadata

data/          Binary data — edit via World Editor
  war3map.w3u      Custom units
  war3map.w3t      Custom items
  war3map.w3a      Custom abilities
  war3map.w3b      Custom destructibles
  war3map.w3h      Custom buffs/effects
  war3map.w3q      Custom upgrades
  war3map.w3e      Terrain/environment
  war3map.w3i      Map info (name, players, loading screen)
  war3map.wtg      Trigger GUI data
  war3map.wct      Custom script block
  war3map.doo      Doodad placements
  war3map.w3r      Regions
  war3map.w3c      Cameras
  war3map.wpm      Pathing map
  war3map.shd      Shadow map
  war3map.mmp      Minimap data
  war3mapMap.blp   Minimap image

assets/        Media files
  Dota - 2.mp3     Background music
  og.mdx           Loading screen model
  imported/        Imported models

tools/
  w3x_tool.py  Extract/repack .w3x archives (needs libstorm.so)
  build.sh     Build script — assembles final .w3x
```

---

## Setup (Linux / Bazzite)

### 1. WC3 Installation

Map runs on **Warcraft III: The Frozen Throne v1.26** installed at:
```
/var/mnt/data_sda/Games/Warcraft III/
```
Launched via Lutris (Wine prefix: `~/Games/WarCraft3`, runner: `lutris-7.2-2-x86_64`).

### 2. Build Tool — StormLib

`w3x_tool.py` uses [StormLib](https://github.com/ladislav-zezula/StormLib) to pack/unpack `.w3x` files.
Build it inside distrobox (Bazzite is an immutable OS):

```bash
distrobox enter zerotier-box
sudo dnf install -y cmake gcc-c++ zlib-devel bzip2-devel openssl-devel libtommath-devel libtomcrypt-devel
cd /tmp
git clone --depth=1 https://github.com/ladislav-zezula/StormLib.git
cd StormLib
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON .
make -j4
cp libstorm.so /var/home/fklose/tools/
cp /usr/lib64/libtomcrypt.so.1 /var/home/fklose/tools/
cp /usr/lib64/libtommath.so.1  /var/home/fklose/tools/
```

### 3. Extract map (read current state)

```bash
LD_LIBRARY_PATH=~/tools python3 tools/w3x_tool.py extract \
  "/var/mnt/data_sda/Games/Warcraft III/Maps/DoItYourSelfMaps/EconomyWar 4 Player v.1.8.5.w3x" \
  /tmp/ew_extract
```

### 4. Build map (after editing)

```bash
bash tools/build.sh
# Output: build/EconomyWar.w3x
# Copy to WC3 Maps folder to test
```

---

## Editing Guide

### JASS Script (`src/war3map.j`)

All game logic lives here. Key sections:

| Function | Purpose |
|----------|---------|
| `InitGlobals` | Initialize global variables |
| `InitTrig_Verkaufen` | Sell mechanics |
| `InitTrig_GeldBeute` | Gold from kills |
| `InitTrig_AdminComand` | Admin cheat commands |
| `Trig_Building_Destroyed_Actions` | On building death |
| `Trig_Winners_Declared_Actions` | Win condition check |
| `InitTrig_AIStart` | AI initialization |

Edit `war3map.j` directly in any text editor. JASS syntax is similar to C.

### Strings (`src/war3map.wts`)

Format:
```
STRING 0
Some text shown in-game
```
Change displayed text here without touching the script.

### Binary Data (units, abilities, items)

These require **World Editor** to edit properly:

```bash
WINEPREFIX=~/Games/WarCraft3 \
~/.local/share/lutris/runners/wine/lutris-7.2-2-x86_64/bin/wine \
"/var/mnt/data_sda/Games/Warcraft III/worldedit.exe"
```

Open the `.w3x` from the build output, make changes, save — then re-extract the binary data files and commit them.

---

## Workflow

```
Edit src/war3map.j
       ↓
bash tools/build.sh
       ↓
Copy build/EconomyWar.w3x → WC3 Maps folder
       ↓
Launch WC3, test map
       ↓
git add src/ data/
git commit -m "..."
git push
```

---

## Version History

| Version | Notes |
|---------|-------|
| v1.1    | Initial version |
| v1.7.2  | Fix release |
| v1.8.0  | Major update |
| v1.8.1  | Bugfix |
| v1.8.2  | Bugfix |
| v1.8.5  | Current version (2019-05-14) |
