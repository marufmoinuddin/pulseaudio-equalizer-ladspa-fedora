# PipeWire LADSPA Equalizer Branch

This is the **PipeWire-compatible** branch of the pulseaudio-equalizer-ladspa package.

## Changes from Main Branch

### Dependencies
- **Changed**: `pulseaudio` → `pipewire-pulseaudio`
- **Benefit**: Works with PipeWire's PulseAudio compatibility layer
- **Target**: Fedora 42 with PipeWire-only audio systems

### Compatibility
- ✅ **PipeWire + pipewire-pulseaudio**: Full support
- ✅ **Traditional PulseAudio**: Still works (backwards compatible)
- ✅ **Wayland + KDE Plasma**: Screen sharing ready
- ✅ **LADSPA Processing**: Professional 15-band equalizer

## Build Instructions

```bash
# Clone this branch
git checkout pipewire-pulse

# Build the RPM
chmod +x build-fedora-rpm.sh
./build-fedora-rpm.sh

# Install
sudo rpm -ivh ~/rpmbuild/RPMS/noarch/pulseaudio-equalizer-ladspa-4.0.1-1.fc42.noarch.rpm
```

## Alternative: Script-Based Equalizer

For more reliable PipeWire integration, use the script-based approach:

```bash
# Use the provided scripts in the main directory
./pipewire-ladspa-equalizer.sh load
./eq-control.sh bass-boost
```

## Testing

After installation, test with:
```bash
# GUI (may have limitations with PipeWire)
pulseaudio-equalizer-gtk

# Command line
pulseaudio-equalizer status
```

## Notes

- This branch specifically targets PipeWire systems
- GUI application may have session management limitations with PipeWire
- Script-based solution (in parent directory) is recommended for production use
- Maintains full backwards compatibility with traditional PulseAudio systems

## Target Systems

- **Primary**: Fedora 42+ with PipeWire
- **Secondary**: Any Linux distribution using PipeWire with PulseAudio compatibility
- **Desktop**: KDE Plasma Wayland (tested)
- **Audio**: Professional LADSPA processing through PipeWire
