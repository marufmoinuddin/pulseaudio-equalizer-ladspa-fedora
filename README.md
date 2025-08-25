# PulseAudio Equalizer LADSPA - PipeWire Compatible

**A 15-band equalizer for PulseAudio/PipeWire with enhanced PipeWire compatibility**

This repository contains a PipeWire-optimized version of the PulseAudio Equalizer LADSPA with improved output device persistence and enhanced compatibility.

## 🎵 Features

- **15-band graphic equalizer** with real-time audio processing
- **PipeWire compatibility** with enhanced output device switching
- **GTK3 interface** built with PyGObject
- **26+ built-in audio presets** (Rock, Classical, Bass Boost, etc.)
- **Persistent output selection** - maintains HDMI/Bluetooth selection
- **Desktop integration** with application launcher

## 📦 Package Information

- **Version**: 2.8.1-pipewire
- **Architecture**: noarch (Python/shell scripts)
- **License**: GPL-3.0-or-later
- **Compatible with**: PulseAudio and PipeWire (with PulseAudio compatibility)

## 🚀 Quick Install

```bash
# Clone the repository
git clone https://github.com/marufmoinuddin/pulseaudio-equalizer-ladspa-fedora.git
cd pulseaudio-equalizer-ladspa-fedora

# Build the RPM package
chmod +x build-fedora-rpm.sh
./build-fedora-rpm.sh

# Install the package
sudo dnf install ~/rpmbuild/RPMS/noarch/pulseaudio-equalizer-ladspa-2.8.1-1.pipewire.*.rpm

# Enable auto-start (optional)
pulseaudio-equalizer-autostart enable

# Run the application
pulseaudio-equalizer-gtk
```

## 🚀 Auto-Start Setup

To automatically load the equalizer on login:

```bash
# Enable auto-start
pulseaudio-equalizer-autostart enable

# Disable auto-start
pulseaudio-equalizer-autostart disable

# Check status
pulseaudio-equalizer-autostart status
```

When auto-start is enabled, the LADSPA equalizer will:
- Automatically load when you log in
- Be set as the default audio sink
- Persist across reboots
- Work with PipeWire-Pulse seamlessly

## 📋 Dependencies

### Runtime Requirements
- `bash` - Shell scripting
- `bc` - Basic calculator for audio math
- `glib2` - GLib library
- `gtk3` - GTK3 GUI toolkit
- `pipewire-pulseaudio` - PipeWire with PulseAudio compatibility
- `python3` - Python 3 interpreter
- `python3-gobject` - Python GObject bindings
- `ladspa-swh-plugins` - SWH LADSPA plugins collection

### Build Dependencies  
- `meson >= 0.46.0` - Build system
- `ninja-build` - Ninja build tool
- `git` - Version control
- `python3-devel` - Python development headers
- `python3-setuptools` - Python setuptools

## ✨ Recent Improvements (v2.8.1)

- **Fixed refresh output sources button** - now persists current selection instead of resetting to laptop
- **Enhanced device persistence** - maintains HDMI and Bluetooth output selection
- **Improved PipeWire compatibility** - better detection of running audio devices
- **Better fallback handling** - smart device selection when devices are disconnected
- **Comprehensive code optimization** and bug fixes

## 🎯 Package Contents

After installation:
- `/usr/bin/pulseaudio-equalizer` - Command-line interface
- `/usr/bin/pulseaudio-equalizer-gtk` - GTK GUI application  
- `/usr/share/applications/` - Desktop application entry
- `/usr/share/pulseaudio-equalizer-ladspa/presets/` - Audio presets
- `/usr/lib/python3.*/site-packages/pulseeq/` - Python modules

## 🐛 Troubleshooting

**Build Issues:**
- Ensure all BuildRequires packages are installed: `sudo dnf builddep pulseaudio-equalizer-ladspa.spec`

**Runtime Issues:**
- Verify PipeWire is running: `systemctl --user status pipewire pipewire-pulse`
- Check SWH plugins are installed: `dnf list ladspa-swh-plugins`
- Don't run the equalizer as root

**Output Device Issues:**
- Use the refresh button to update device list
- The equalizer now properly persists HDMI/Bluetooth selections

## 🤝 Contributing

For upstream issues with the equalizer itself, visit the [original project](https://github.com/pulseaudio-equalizer-ladspa/equalizer).

## 📜 License

GPL-3.0-or-later (same as upstream project)

---

**PipeWire-optimized version - Enhanced for modern Linux audio systems**
