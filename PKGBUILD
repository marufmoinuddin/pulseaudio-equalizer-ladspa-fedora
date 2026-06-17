# Maintainer: Your Name <your@email.com>
pkgname=pulseaudio-equalizer-ladspa
pkgver=r59.g8433263
pkgrel=1
pkgdesc="PulseAudio equalizer using LADSPA plugins"
arch=('x86_64' 'aarch64')
url="https://github.com/your/repo"
license=('GPL')
depends=('libpulse' 'ladspa' 'gtk3' 'glib2' 'python3')
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
