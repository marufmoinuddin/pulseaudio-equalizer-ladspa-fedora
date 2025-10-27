# Maintainer: Your Name <your.email@example.com>

pkgname=pulseaudio-equalizer-ladspa
pkgver=2.8.1
pkgrel=1
pkgdesc="A 15-band equalizer for PulseAudio/PipeWire (PipeWire-optimized)"
arch=('any')
url="https://github.com/pulseaudio-equalizer-ladspa/equalizer"
license=('GPL3')
depends=(
    'bash'
    'bc'
    'glib2'
    'gtk3'
    'pipewire-pulse'
    'python'
    'python-gobject'
    'swh-plugins'
    'systemd'
)
makedepends=(
    'meson>=0.46.0'
    'ninja'
    'git'
    'python-setuptools'
)
source=("$pkgname::git+file://$PWD")
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
}