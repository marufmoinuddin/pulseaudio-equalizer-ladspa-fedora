#!/usr/bin/env bash
set -euo pipefail

PKG=$(ls pulseaudio-equalizer-ladspa-*.pkg.tar.zst 2>/dev/null || ls pulseaudio-equalizer-ladspa-*.pkg.tar.xz 2>/dev/null || true)
if [[ -z "$PKG" ]]; then
  echo "ERROR: built package not found"
  exit 1
fi

pacman -U --noconfirm "$PKG" || true

if ! pacman -Qi pulseaudio-equalizer-ladspa | grep -q "Depends On.*libpulse"; then
  echo "ERROR: libpulse not in Depends"
  pacman -Qi pulseaudio-equalizer-ladspa
  exit 1
fi

if pacman -Qi pulseaudio-equalizer-ladspa | grep -q "pulseaudio"; then
  echo "ERROR: pulseaudio found in Depends"
  pacman -Qi pulseaudio-equalizer-ladspa
  exit 1
fi

echo "OK: package depends on libpulse and does not require pulseaudio"
