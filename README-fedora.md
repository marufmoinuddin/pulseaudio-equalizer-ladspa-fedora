# Fedora 42 RPM Package Conversion

This directory contains the Fedora 42 RPM package conversion for `pulseaudio-equalizer-ladspa`.

## Package Information

- **Name**: pulseaudio-equalizer-ladspa
- **Version**: 3.0.2
- **Architecture**: noarch (Python/shell scripts)
- **License**: GPL-3.0-only

## Dependencies Mapping (Arch → Fedora)

### Runtime Dependencies
| Arch Package | Fedora Package | Notes |
|--------------|----------------|-------|
| `bash` | `bash` | Same name |
| `bc` | `bc` | Same name |
| `glib2` | `glib2` | Same name |
| `gtk3` | `gtk3` | Same name |
| `pulseaudio` | `pulseaudio` | Same name |
| `python` | `python3` | Fedora uses python3 explicitly |
| `python-gobject` | `python3-gobject` | Fedora uses python3 prefix |
| `swh-plugins` | `ladspa-swh-plugins` | Different package name |

### Build Dependencies
| Arch Package | Fedora Package | Notes |
|--------------|----------------|-------|
| `git` | `git` | Same name |
| `meson` | `meson` | Same name |
| N/A | `ninja-build` | Required for meson builds |
| N/A | `python3-devel` | Required for Python builds |

## Building the Package

1. **Install build tools**:
   ```bash
   sudo dnf install rpm-build rpmdevtools
   ```

2. **Set up RPM build environment**:
   ```bash
   rpmdev-setuptree
   ```

3. **Copy spec file**:
   ```bash
   cp pulseaudio-equalizer-ladspa.spec ~/rpmbuild/SPECS/
   ```

4. **Download source**:
   ```bash
   cd ~/rpmbuild/SOURCES/
   wget https://github.com/pulseaudio-equalizer-ladspa/equalizer/archive/v3.0.2.tar.gz \
        -O pulseaudio-equalizer-ladspa-3.0.2.tar.gz
   ```

5. **Build the package**:
   ```bash
   cd ~/rpmbuild/SPECS/
   rpmbuild -ba pulseaudio-equalizer-ladspa.spec
   ```

## Installation

After building, install the RPM:
```bash
sudo dnf install ~/rpmbuild/RPMS/noarch/pulseaudio-equalizer-ladspa-3.0.2-1.fc42.noarch.rpm
```

## Usage

After installation, you can run the equalizer with:
```bash
pulseaudio-equalizer-gtk
```

Or use the command-line interface:
```bash
pulseaudio-equalizer --help
```

## Files Included

- `/usr/bin/pulseaudio-equalizer` - Command-line interface
- `/usr/bin/pulseaudio-equalizer-gtk` - GTK GUI application
- `/usr/share/pulseaudio-equalizer-ladspa/` - Data files and presets
- `/usr/share/applications/` - Desktop application entry
- Python modules in `/usr/lib/python3.x/site-packages/pulseeq/`

## Notes

- This is a `noarch` package since it consists of Python scripts and shell scripts
- The package uses meson build system (modern replacement for autotools)
- Requires PulseAudio (not compatible with PipeWire's pulseaudio-compat layer)
- LADSPA SWH plugins are required for the actual audio processing
