%global debug_package %{nil}

Name:           pulseaudio-equalizer-ladspa
Version:        4.0.1
Release:        1%{?dist}
Summary:        A 15-band equalizer for PulseAudio/PipeWire
License:        GPL-3.0-or-later
URL:            https://github.com/pulseaudio-equalizer-ladspa/equalizer
Source0:        https://github.com/pulseaudio-equalizer-ladspa/equalizer/archive/v3.0.2.tar.gz#/%{name}-%{version}.tar.gz
Patch0:         pipewire-compatibility.patch

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
%autosetup -n equalizer-3.0.2 -p1

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
* Mon Aug 25 2025 Maruf <maruf@example.com> - 4.0.1-1
- PipeWire compatibility branch
- Updated dependencies to use pipewire-pulseaudio instead of pulseaudio
- Modified description to reflect PipeWire support
- Tested with PipeWire's PulseAudio compatibility layer on Fedora 42

* Tue Aug 19 2025 Maruf <maruf@example.com> - 4.0.1-1
- Test release for CI/CD pipeline validation
- Updated packaging to use remote source URL
- Fixed version alignment for automated builds
- Verified compatibility with Fedora 42
