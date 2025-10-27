# Maintainer: maruf <maruf@example.com>

pkgname=pulseaudio-equalizer-ladspa-pipewire
_pkgname=pulseaudio-equalizer-ladspa
pkgver=2.8.1
pkgrel=1
pkgdesc="PipeWire-optimized 15-band equalizer with LADSPA processing"
url="https://github.com/pulseaudio-equalizer-ladspa/equalizer"
license=('GPL3')
arch=('any')
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
  'git'
  'meson'
  'ninja'
)
provides=("${_pkgname}")
conflicts=("${_pkgname}")
source=("${_pkgname}::git+https://github.com/marufmoinuddin/pulseaudio-equalizer-ladspa-fedora.git#commit=8e8c95fa87c1bc14f16cd6ddfef9c53823819244")
b2sums=('SKIP')

build() {
  cd "${_pkgname}"

  local purelib
  purelib=$(python - <<'EOF'
import sysconfig
print(sysconfig.get_path('purelib'))
EOF
  )

  arch-meson -Dpurelib="${purelib}" build
  meson compile -C build
}

package() {
  cd "${_pkgname}"

  meson install -C build --destdir "${pkgdir}"

  install -Dm644 LICENSE "${pkgdir}/usr/share/licenses/${pkgname}/LICENSE"
  install -Dm644 README.md "${pkgdir}/usr/share/doc/${pkgname}/README.md"

  local purelib
  purelib=$(python - <<'EOF'
import sysconfig
print(sysconfig.get_path('purelib'))
EOF
  )

  if [[ -d "${pkgdir}${purelib}" ]]; then
    python -m compileall -d "${purelib}" "${pkgdir}${purelib}"
    python -O -m compileall -d "${purelib}" "${pkgdir}${purelib}"
  fi
}

# vim:set sw=2 sts=-1 et:
