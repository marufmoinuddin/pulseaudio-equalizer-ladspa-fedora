from __future__ import annotations

from pathlib import Path
from typing import Optional

from pulseeq.constants import USER_PRESET_DIR, SYSTEM_PRESET_DIR
from pulseeq.pulse import EqualizerState, MBEQ_PLUGIN


def preset_path(name: str) -> Optional[Path]:
    """Return the path to a preset file, checking user dir first, then system dir."""
    user_path = USER_PRESET_DIR / f'{name}.preset'
    if user_path.is_file():
        return user_path
    system_path = SYSTEM_PRESET_DIR / f'{name}.preset'
    if system_path.is_file():
        return system_path
    return None


def load_preset(name: str, state: EqualizerState) -> bool:
    """Load a preset into *state*. Returns True if the preset was found."""
    path = preset_path(name)
    if not path:
        print(f"Can't find {name} preset")
        return False

    rawdata = path.read_text().split('\n')

    state.ladspa_filename = MBEQ_PLUGIN
    state.ladspa_name = str(rawdata[1])
    state.ladspa_label = str(rawdata[2])
    state.preset = str(rawdata[4])
    state.num_ladspa_controls = int(rawdata[5])
    state.ladspa_controls = [float(v) for v in rawdata[6:6 + state.num_ladspa_controls]]
    state.ladspa_inputs = [float(v) for v in rawdata[6 + state.num_ladspa_controls:6 + state.num_ladspa_controls * 2]]
    return True


def save_preset(name: str, state: EqualizerState) -> Path:
    """Write a user preset file and return the path."""
    path = USER_PRESET_DIR / f'{name}.preset'
    data = [
        str(state.ladspa_filename), str(state.ladspa_name),
        str(state.ladspa_label), '',
        str(state.preset), str(state.num_ladspa_controls),
        *(str(v) for v in state.ladspa_controls),
        *(str(v) for v in state.ladspa_inputs),
    ]
    path.write_text('\n'.join(data) + '\n')
    return path


def remove_preset(name: str) -> None:
    """Remove a user preset file."""
    path = USER_PRESET_DIR / f'{name}.preset'
    path.unlink(missing_ok=True)
