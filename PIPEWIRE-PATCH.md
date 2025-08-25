# PipeWire Compatibility Patch for pulseaudio-equalizer

This patch replaces `pacmd` commands with `pactl` equivalents for PipeWire compatibility.

## Changes needed:

1. `pacmd stat` → `pactl info`
2. `pacmd list` → `pactl list`
3. `pacmd list-sinks` → `pactl list sinks`
4. `pacmd info` → `pactl list sinks`

## Create patched source files
