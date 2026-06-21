from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from pulseeq.constants import CONFIG_FILE, PRESETS_FILE


def detect_mbeq_plugin() -> Optional[str]:
    """Return the basename (without .so) of the first MBEQ LADSPA plugin found."""
    for d in ('/usr/lib/ladspa', '/usr/lib64/ladspa'):
        try:
            for entry in os.listdir(d):
                if entry.startswith('mbeq') and entry.endswith('.so'):
                    return entry[:-3]
        except FileNotFoundError:
            continue
    return None


MBEQ_PLUGIN = detect_mbeq_plugin()
if not MBEQ_PLUGIN:
    sys.stderr.write('error: no MBEQ LADSPA plugin found; install swh-plugins\n')
    sys.exit(1)


@dataclass
class EqualizerState:
    mbeq_plugin: str = MBEQ_PLUGIN
    ladspa_filename: str = ''
    ladspa_name: str = ''
    ladspa_label: str = ''
    preamp: str = ''
    preset: str = ''
    status: int = 0
    persistence: int = 0
    ranges: list[str] = field(default_factory=list)
    num_ladspa_controls: int = 0
    ladspa_controls: list[float] = field(default_factory=list)
    ladspa_inputs: list[float] = field(default_factory=list)
    clearpreset: int = 1
    presetmatch: str = ''

    output_selected: int = 0
    num_profiles: int = 0
    profiles: list[str] = field(default_factory=list)
    profile_sinks: list[str] = field(default_factory=list)
    last_selected_sink: Optional[str] = None
    current_active_sink: Optional[str] = None

    rawpresets: list[str] = field(default_factory=list)


def _pactl(args: str, timeout: int = 10) -> subprocess.CompletedProcess:
    """Run a pactl command and return the result."""
    return subprocess.run(
        shlex.split(args), capture_output=True, text=True, timeout=timeout
    )


def _run(cmd: str, timeout: int = 10) -> subprocess.CompletedProcess:
    """Run an arbitrary command via shell (needed for pipeline-style calls)."""
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)


def get_settings(state: EqualizerState) -> None:
    """Read current settings from the equalizer backend and populate *state*."""
    _run('pulseaudio-equalizer interface.getsettings')

    rawdata = CONFIG_FILE.read_text().split('\n')

    rawpresets = PRESETS_FILE.read_text().split('\n')
    if rawpresets and rawpresets[-1] == '':
        rawpresets = rawpresets[:-1]

    state.ladspa_filename = MBEQ_PLUGIN
    state.ladspa_name = str(rawdata[1])
    state.ladspa_label = str(rawdata[2])
    state.preamp = rawdata[3]
    state.preset = str(rawdata[4])
    state.status = int(rawdata[5])
    state.persistence = int(rawdata[6])
    state.ranges = rawdata[7:9]
    state.num_ladspa_controls = int(rawdata[9])
    state.ladspa_controls = [float(v) for v in rawdata[10:10 + state.num_ladspa_controls]]
    state.ladspa_inputs = [float(v) for v in rawdata[10 + state.num_ladspa_controls:10 + state.num_ladspa_controls + state.num_ladspa_controls]]

    state.rawpresets = rawpresets
    state.clearpreset = 1
    state.presetmatch = ''
    for p in rawpresets:
        if p == state.preset:
            state.presetmatch = '1'


def initialize_current_output(state: EqualizerState) -> None:
    """Detect the currently running non-LADSPA sink and store it."""
    try:
        # Check if LADSPA module is loaded and extract its master sink
        result = _run(
            "pactl list modules | grep -A 20 'module-ladspa-sink' | "
            "grep 'sink_master=' | head -1"
        )
        if result.returncode == 0 and result.stdout.strip():
            m = re.search(r'sink_master=(\S+)', result.stdout)
            if m:
                master = m.group(1)
                state.last_selected_sink = master
                state.current_active_sink = master
                print(f"Init: detected master sink from equalizer: {master}")
                return

        # No equalizer running; find currently RUNNING non-ladspa sink
        result = _run("pactl list sinks short | grep -v ladspa")
        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                if 'RUNNING' in line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        sink = parts[1]
                        state.last_selected_sink = sink
                        state.current_active_sink = sink
                        return

            first_line = result.stdout.strip().split('\n')[0]
            parts = first_line.split('\t')
            if len(parts) >= 2:
                sink = parts[1]
                state.last_selected_sink = sink
                state.current_active_sink = sink
        else:
            state.last_selected_sink = None
            state.current_active_sink = None
    except Exception as e:
        print(f"Error detecting current output device: {e}")
        state.last_selected_sink = None
        state.current_active_sink = None


def apply_settings(state: EqualizerState) -> None:
    """Write settings and apply them; restore the output device afterwards."""
    data = [
        str(state.ladspa_filename), str(state.ladspa_name),
        str(state.ladspa_label), str(state.preamp),
        str(state.preset), str(state.status), str(state.persistence),
        *map(str, state.ranges), str(state.num_ladspa_controls),
        *(str(v) for v in state.ladspa_controls),
        *(str(v) for v in state.ladspa_inputs),
    ]
    CONFIG_FILE.write_text('\n'.join(data) + '\n')

    if state.status:
        _run('pulseaudio-equalizer interface.applysettings')
    else:
        _run('pulseaudio-equalizer disable')

    if not state.status:
        return

    if state.last_selected_sink and state.last_selected_sink != 'default':
        print(f'Restoring output to: {state.last_selected_sink}')
        try:
            time.sleep(0.5)
            result = _run(
                f"pulseaudio-equalizer update-output {shlex.quote(state.last_selected_sink)}"
            )
            if result.returncode == 0:
                state.current_active_sink = state.last_selected_sink
                print(f"Successfully restored output to: {state.last_selected_sink}")
            else:
                print(f"Warning: Could not restore output device: {result.stderr}")
                _pactl(f"pactl set-default-sink {shlex.quote(state.last_selected_sink)}")
                state.current_active_sink = state.last_selected_sink
                print(f"Fallback: Set default sink to {state.last_selected_sink}")
        except Exception as e:
            print(f"Warning: Error restoring output device: {e}")
    else:
        print(f"No output device to restore (last_selected_sink = {state.last_selected_sink})")


def get_output_devices(state: EqualizerState) -> None:
    """Enumerate non-LADSPA sinks using a single pactl call."""
    state.profiles = []
    state.profile_sinks = []

    try:
        result = _pactl('pactl list sinks')
        if result.returncode != 0:
            raise Exception(f"pactl returned code {result.returncode}")

        sink_name = None
        for line in result.stdout.split('\n'):
            name_match = re.match(r'\s+Name:\s+(.+)', line)
            if name_match and sink_name is None:
                sink_name = name_match.group(1).strip()
                continue

            desc_match = re.match(r'\s+Description:\s+(.+)', line)
            if desc_match and sink_name and 'ladspa' not in sink_name:
                state.profiles.append(desc_match.group(1).strip())
                state.profile_sinks.append(sink_name)
                sink_name = None
            elif name_match and sink_name is not None:
                sink_name = name_match.group(1).strip()
    except Exception as e:
        print(f"Error getting output devices: {e}")

    if not state.profiles:
        state.profiles = ['Default Output']
        state.profile_sinks = ['default']

    state.num_profiles = len(state.profiles)
    print(f"Found {state.num_profiles} output devices: {state.profiles}")


def switch_output(state: EqualizerState, sink_name: str) -> bool:
    """Switch the equalizer to *sink_name*. Returns True on success."""
    try:
        result = _run(
            f"pulseaudio-equalizer update-output {shlex.quote(sink_name)}"
        )
        if result.returncode == 0:
            state.current_active_sink = sink_name
            print(f"Successfully switched equalizer to: {sink_name}")
            return True
        else:
            print(f"Error switching output: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error switching equalizer output: {e}")
        return False
