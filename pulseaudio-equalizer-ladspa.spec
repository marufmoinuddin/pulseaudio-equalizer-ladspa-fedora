%global debug_package %{nil}

Name:           pulseaudio-equalizer-ladspa
Version:        2.8.0
Release:        1.pipewire%{?dist}
Summary:        A 15-band equalizer for PulseAudio/PipeWire (PipeWire-optimized)
License:        GPL-3.0-or-later
URL:            https://github.com/pulseaudio-equalizer-ladspa/equalizer
Source0:        pulseaudio-equalizer-ladspa-2.8.0.tar.gz

BuildArch:      noarch

BuildRequires:  meson >= 0.46.0
BuildRequires:  ninja-build
BuildRequires:  git
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

Requires:       bash
Requires:       bc
Requires:       glib2
Requires:       gtk3
Requires:       pipewire-pulseaudio
Requires:       python3
Requires:       python3-gobject
Requires:       ladspa-swh-plugins

%description
A LADSPA based multiband equalizer approach for getting better sound out of 
PulseAudio or PipeWire (with PulseAudio compatibility). This equalizer clearly 
is more potent than the (deprecated), optional one from PulseAudio.

The equalizer provides a 15-band graphic equalizer interface built using 
GTK3 and PyGObject, allowing real-time audio equalization through PulseAudio's
LADSPA sink module or PipeWire's PulseAudio compatibility layer. 
optional one from PulseAudio.

The equalizer provides a 15-band graphic equalizer interface built using 
GTK3 and PyGObject, allowing real-time audio equalization through PulseAudio's
LADSPA sink module.

%prep
%autosetup -n pulseaudio-equalizer-ladspa-2.8.0-pipewire

%build
%meson
%meson_build

%install
%meson_install

%py_byte_compile %{python3} %{buildroot}%{python3_sitelib}

%files
%license LICENSE
%doc README.md
%{_bindir}/pulseaudio-equalizer
%{_bindir}/pulseaudio-equalizer-gtk
%{_datadir}/%{name}/
%{_datadir}/applications/com.github.pulseaudio-equalizer-ladspa.Equalizer.desktop
%{python3_sitelib}/pulseeq/

%changelog
* Mon Aug 26 2024 maruf <maruf@example.com> - 2.8.0-1.pipewire
- Comprehensive code optimization and cleanup
- Fix global variable scope issue in GUI initialization
- Fix GUI initialization to select RUNNING sink device in dropdown
- Fix execute permissions for installed binaries
- Improve output device selection and persistence
- Enhanced GUI output device switching functionality
- Multiple bug fixes and stability improvements

* Thu Jan 09 2025 maruf <maruf@example.com> - 2.7.5-1.pipewire
- Add GUI output device switching functionality
- Enhanced PipeWire compatibility with real-time device switching
- Improved preset discovery and loading capabilities
- Added update-output command for dynamic sink switching
