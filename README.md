# pulseaudio-equalizer-ladspa-fedora

**Fedora 42 RPM Package for PulseAudio Equalizer LADSPA**

This repository contains the Fedora 42 RPM package conversion of `pulseaudio-equalizer-ladspa`, originally converted from the Arch Linux package.

## 🎵 About

A LADSPA based multiband equalizer approach for getting better sound out of PulseAudio. This equalizer is more potent than the deprecated optional one from PulseAudio.

**Features:**
- 15-band graphic equalizer interface
- Built with GTK3 and PyGObject 
- Real-time audio equalization through PulseAudio's LADSPA sink module
- 26+ built-in audio presets (Rock, Classical, Bass Boost, etc.)
- Desktop integration with application launcher

## 📦 Package Information

- **Name**: pulseaudio-equalizer-ladspa
- **Version**: 3.0.2
- **Architecture**: noarch (Python/shell scripts)
- **License**: GPL-3.0-or-later
- **Target**: Fedora 42

## 🚀 Quick Build & Install

```bash
# Clone the repository
git clone <your-repo-url>
cd pulseaudio-equalizer-ladspa-fedora

# Build the RPM package (automated)
chmod +x build-fedora-rpm.sh
./build-fedora-rpm.sh

# Install the package
sudo dnf install ~/rpmbuild/RPMS/noarch/pulseaudio-equalizer-ladspa-3.0.2-1.fc42.noarch.rpm

# Run the application
pulseaudio-equalizer-gtk
```

## 📋 Dependencies

### Runtime Dependencies
- `bash` - Shell scripting
- `bc` - Basic calculator for audio math
- `glib2` - GLib library
- `gtk3` - GTK3 GUI toolkit
- `pulseaudio` - PulseAudio sound server
- `python3` - Python 3 interpreter
- `python3-gobject` - Python GObject bindings
- `ladspa-swh-plugins` - SWH LADSPA plugins collection

### Build Dependencies  
- `meson >= 0.46.0` - Build system
- `ninja-build` - Ninja build tool
- `git` - Version control
- `python3-devel` - Python development headers
- `python3-setuptools` - Python setuptools

## 📁 Repository Structure

```
├── pulseaudio-equalizer-ladspa.spec  # RPM spec file
├── build-fedora-rpm.sh               # Automated build script
├── README-fedora.md                  # Detailed Fedora documentation
├── SUMMARY.md                        # Conversion summary
├── PKGBUILD                          # Original Arch Linux package
├── LICENSE                           # GPL-3.0 license
└── share/                            # Shared data files
```

## 📖 Documentation

- **[README-fedora.md](README-fedora.md)** - Comprehensive Fedora packaging guide
- **[SUMMARY.md](SUMMARY.md)** - Detailed conversion summary from Arch to Fedora
- **[CICD.md](CICD.md)** - Complete CI/CD pipeline documentation
- **[MANUAL-RELEASE.md](MANUAL-RELEASE.md)** - Manual release workflow guide
- **[VERSION-MANAGEMENT.md](VERSION-MANAGEMENT.md)** - Version alignment and management

## 🚀 CI/CD & Release Management

This repository includes comprehensive automation:

### 🔄 Automated Workflows
- **Development Build** - Creates test RPMs on every push
- **Continuous Integration** - Quality checks and multi-version testing
- **Release Pipeline** - Automated releases on git tags
- **Manual Release** - On-demand release creation with custom versions

### 📦 Manual Release Creation
Create custom releases without git tag pushes:

1. Go to **Actions** → **Manual Build and Release**
2. Click **Run workflow**
3. Specify your parameters:
   ```
   Release Tag: v4.0.3
   Package Version: 4.0.3
   Upstream Version: 3.0.2
   Release Title: Custom Release v4.0.3
   ```
4. Click **Run workflow** to build and publish

See **[MANUAL-RELEASE.md](MANUAL-RELEASE.md)** for complete usage guide.

### 🎯 Quick Release Examples
```bash
# Standard release
Release Tag: v4.0.3, Package: 4.0.3, Upstream: 3.0.2

# Beta release  
Release Tag: v4.1.0-beta1, Package: 4.1.0.beta1, Upstream: 3.0.2

# Hotfix release
Release Tag: v4.0.2-hotfix, Package: 4.0.2, Upstream: 3.0.2
```

## 🔧 Manual Build Process

If you prefer to build manually:

```bash
# Set up RPM build environment
rpmdev-setuptree

# Copy spec file
cp pulseaudio-equalizer-ladspa.spec ~/rpmbuild/SPECS/

# Download source
cd ~/rpmbuild/SOURCES/
wget https://github.com/pulseaudio-equalizer-ladspa/equalizer/archive/v3.0.2.tar.gz \
     -O pulseaudio-equalizer-ladspa-3.0.2.tar.gz

# Install build dependencies
sudo dnf builddep ~/rpmbuild/SPECS/pulseaudio-equalizer-ladspa.spec

# Build package
cd ~/rpmbuild/SPECS/
rpmbuild -ba pulseaudio-equalizer-ladspa.spec
```

## 🎯 Package Contents

After installation, you'll have:

- `/usr/bin/pulseaudio-equalizer` - Command-line interface
- `/usr/bin/pulseaudio-equalizer-gtk` - GTK GUI application  
- `/usr/share/applications/` - Desktop application entry
- `/usr/share/pulseaudio-equalizer-ladspa/presets/` - Audio presets
- `/usr/lib/python3.13/site-packages/pulseeq/` - Python modules

## ⚠️ Important Notes

- **PulseAudio Required**: This package requires actual PulseAudio, not PipeWire's compatibility layer
- **LADSPA Plugins**: The `ladspa-swh-plugins` package is essential for audio processing
- **Python 3.13**: Built for Python 3.13 (Fedora 42)

## 🐛 Troubleshooting

If you encounter issues:

1. **Build Failures**: Ensure all BuildRequires packages are installed
2. **Runtime Issues**: Verify PulseAudio is running and SWH plugins are available
3. **Permission Issues**: Don't run the equalizer as root

## 🤝 Contributing

This is a packaging repository. For upstream issues with the equalizer itself, please visit:
- **Upstream Project**: https://github.com/pulseaudio-equalizer-ladspa/equalizer
- **Original Arch Package**: https://gitlab.archlinux.org/archlinux/packaging/packages/pulseaudio-equalizer-ladspa

## 📜 License

GPL-3.0-or-later (same as upstream project)

## 🏷️ Tags

`fedora` `rpm` `pulseaudio` `equalizer` `ladspa` `audio` `gtk3` `python` `packaging`

---

**Converted from Arch Linux to Fedora 42 RPM on August 19, 2025**
