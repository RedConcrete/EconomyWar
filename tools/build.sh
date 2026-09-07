#!/usr/bin/env bash
# Baut EconomyWar v1.8.6 und kopiert sie direkt in den WC3-Maps-Ordner.
set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$REPO_DIR/src"
TOOLS="$REPO_DIR/tools"

ORIG_MAP="/var/mnt/data_sda/Games/Warcraft III/Maps/DoItYourSelfMaps/EconomyWar 4 Player v.1.8.5.w3x"
OUT_MAP="/var/mnt/data_sda/Games/Warcraft III/Maps/DoItYourSelfMaps/EconomyWar 4 Player v.1.8.6.w3x"
AI_DEST="/var/mnt/data_sda/Games/Warcraft III/AI Scripts/EconomyWarAI.ai"

echo "==> Kopiere AI Script..."
cp "$SRC/EconomyWarAI.ai" "$AI_DEST"

echo "==> Baue Map v1.8.6..."
LD_LIBRARY_PATH=/var/home/fklose python3 "$TOOLS/w3x_tool.py" patch \
    "$ORIG_MAP" \
    "$OUT_MAP" \
    "war3map.j=$SRC/war3map.j" \
    "war3map.wts=$SRC/war3map.wts" \
    "war3mapMisc.txt=$SRC/war3mapMisc.txt" \
    "war3mapSkin.txt=$SRC/war3mapSkin.txt" \
    "war3mapExtra.txt=$SRC/war3mapExtra.txt"

echo ""
echo "Fertig: $OUT_MAP"
echo "Starte WC3 und oeffne: Maps/DoItYourSelfMaps/EconomyWar 4 Player v.1.8.6"
