from pathlib import Path
import os

if 'XDG_CONFIG_HOME' in os.environ:
    CONFIG_DIR = Path(os.environ['XDG_CONFIG_HOME']) / 'pulse'
else:
    CONFIG_DIR = Path.home() / '.config' / 'pulse'

CONFIG_FILE = CONFIG_DIR / 'equalizerrc'
PRESETS_FILE = CONFIG_DIR / 'equalizerrc.availablepresets'
USER_PRESET_DIR = CONFIG_DIR / 'presets'
SYSTEM_PRESET_DIR = Path('/usr/local/share/pulseaudio-equalizer-ladspa') / 'presets'
