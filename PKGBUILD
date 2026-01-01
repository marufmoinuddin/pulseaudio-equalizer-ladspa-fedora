# Maintainer: Your Name <your.email@example.com>

pkgname=pulseaudio-equalizer-ladspa
pkgver=3.0.2
pkgrel=12
pkgdesc="A 15-band equalizer for PulseAudio/PipeWire (PipeWire-compatible)"
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
    'swh-plugins'
    'systemd'
)

# Make pulseaudio optional to avoid forcing it on systems running PipeWire
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
sha256sums=('2dd14d7bdbc806bfa239bae49dbeef8ccd8bbdb53a413bd83d0ca32390ceae6f')

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