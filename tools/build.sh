#!/usr/bin/env bash
# Repacks the EconomyWar map from src/ + data/ + assets/ into a .w3x file.
# Requires libstorm.so (built from StormLib) in the same directory as w3x_tool.py.
# See README.md -> Setup for build instructions.

set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="$REPO_DIR/build"
STAGE_DIR="$BUILD_DIR/stage"
OUT_MAP="$BUILD_DIR/EconomyWar.w3x"
ORIG_MAP="/var/mnt/data_sda/Games/Warcraft III/Maps/DoItYourSelfMaps/EconomyWar 4 Player v.1.8.5.w3x"

mkdir -p "$STAGE_DIR"

# Copy data files
cp "$REPO_DIR/data/"* "$STAGE_DIR/"

# Copy src (text/script files — these override data/)
cp "$REPO_DIR/src/"* "$STAGE_DIR/"

# Copy assets
cp "$REPO_DIR/assets/Dota - 2.mp3" "$STAGE_DIR/" 2>/dev/null || true
mkdir -p "$STAGE_DIR/Lodeingscreen"
cp "$REPO_DIR/assets/og.mdx" "$STAGE_DIR/Lodeingscreen/" 2>/dev/null || true
mkdir -p "$STAGE_DIR/war3mapImported"
cp "$REPO_DIR/assets/imported/Test.mdx" "$STAGE_DIR/war3mapImported/" 2>/dev/null || true

# Prepend original 512-byte WC3 header, then repack MPQ
HEADER_TMP=$(mktemp)
dd if="$ORIG_MAP" bs=512 count=1 of="$HEADER_TMP" 2>/dev/null
MPQ_TMP=$(mktemp --suffix=.mpq)

LD_LIBRARY_PATH="$(dirname "$0")" python3 "$REPO_DIR/tools/w3x_tool.py" repack "$STAGE_DIR" "$MPQ_TMP"

cat "$HEADER_TMP" "$MPQ_TMP" > "$OUT_MAP"
rm -f "$HEADER_TMP" "$MPQ_TMP"

echo "Built: $OUT_MAP"
