# Maintainer: Your Name <your.email@example.com>

pkgname=pulseaudio-equalizer-ladspa
pkgver=3.0.2
pkgrel=11
pkgdesc="A 15-band equalizer for PulseAudio/PipeWire (PipeWire-optimized)"
arch=('any')
url="https://github.com/pulseaudio-equalizer-ladspa/equalizer"
license=('GPL3')
depends=(
    'bash'
    'bc'
    'glib2'
    'gtk3'
    'libpulse'                    # Client library only (works with PipeWire)
    'python'
    'python-gobject'
    # recent Arch renames the old swh-plugins package to ladspa-swh-plugins
    # (same as Fedora); require the new name so the MBEQ plugin is present.
    'ladspa-swh-plugins'
    'systemd'
)
optdepends=(
    'pipewire-pulse: PipeWire PulseAudio compatibility (recommended)'
    'pulseaudio: PulseAudio sound server (alternative)'
)
makedepends=(
    'meson>=0.46.0'
    'ninja'
    'git'
    'python-setuptools'
)
conflicts=('pulseaudio-equalizer')
provides=('pulseaudio-equalizer')
source=("https://github.com/pulseaudio-equalizer-ladspa/equalizer/archive/refs/tags/v${pkgver}.tar.gz")
sha256sums=('SKIP')

build() {
    arch-meson "$pkgname" build
    meson compile -C build
}

package() {
    meson install -C build --destdir="$pkgdir"
    
    # Python byte-compilation
    python -m compileall -q -d /usr/lib \
        "$pkgdir/usr/lib/python$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
    
    # Ensure systemd user service directory exists
    install -dm755 "$pkgdir/usr/lib/systemd/user"
}