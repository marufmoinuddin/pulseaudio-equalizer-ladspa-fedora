# Maintainer: Your Name <your@email.com>
pkgname=pulseaudio-equalizer-ladspa-pipewire
pkgver=r62.g20ded37
pkgrel=1
pkgdesc="PulseAudio/PipeWire equalizer using LADSPA plugins"
arch=('x86_64' 'aarch64')
url="https://github.com/marufmoinuddin/pulseaudio-equalizer-ladspa-fedora"
license=('GPL')
depends=('libpulse' 'ladspa' 'gtk3' 'glib2' 'python3' 'swh-plugins')
optdepends=('pipewire-pulse: PulseAudio server compatibility layer (recommended)'
            'pulseaudio: Native PulseAudio server')
provides=('pulseaudio-equalizer-ladspa')
conflicts=('pulseaudio-equalizer-ladspa')
makedepends=('meson' 'ninja' 'glib2' 'gtk3' 'python')
source=("$pkgname::git+file://$startdir")
sha256sums=('SKIP')

pkgver() {
    cd "$srcdir/$pkgname"
    printf "r%s.g%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

build() {
    cd "$srcdir/$pkgname"
    meson setup build \
        --prefix=/usr \
        --buildtype=release
    ninja -C build
}

package() {
    cd "$srcdir/$pkgname"
    DESTDIR="$pkgdir" ninja -C build install
}
