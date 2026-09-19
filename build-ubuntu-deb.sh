#!/bin/bash
set -euo pipefail

# =============================================================================
# build-ubuntu-deb.sh - build a .deb package for pulseaudio-equalizer-ladspa
#
# Target distros: Ubuntu 22.04 (jammy) through 26.04 (resolute), Debian 12/13.
#
# What it does (mirrors build-fedora-rpm.sh / PKGBUILD):
#   1. detects the running Debian/Ubuntu release and warns outside 22.04-26.04
#   2. installs the build dependencies with apt
#   3. derives a dpkg-compatible version from meson.build + git
#   4. stages the working tree (tracked + untracked, non-ignored files) into
#      dist/deb/<name>-<version>/ and writes a complete debian/ directory
#   5. builds with dpkg-buildpackage -b (unsigned, no dpkg checker)
#   6. verifies the produced .deb (layout, shebangs, python imports)
#
# Usage:
#   ./build-ubuntu-deb.sh [-h|--help]
#
# Environment overrides:
#   DEB_VERSION    upstream version to use (must start with a digit)
#   PURELIB_REL    python install dir relative to /usr
#                  (default: lib/python3/dist-packages)
#   MAINTAINER     "Name <email>" used in changelog/control
#   SKIP_DEPS=1    do not install build dependencies with apt
#   KEEP_BUILD=1   keep the staged source tree after a successful build
# =============================================================================

PACKAGE_NAME="pulseaudio-equalizer-ladspa"
APP_ID="com.github.pulseaudio-equalizer-ladspa.Equalizer"
FALLBACK_VERSION="2.8.1"
MIN_UBUNTU_MAJOR=22
MAX_UBUNTU_MAJOR=26

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="${SCRIPT_DIR}/dist/deb"
VENV_DIR="${SCRIPT_DIR}/.deb-build-venv"

PURELIB_REL="${PURELIB_REL:-lib/python3/dist-packages}"
MAINTAINER="${MAINTAINER:-maruf <maruf@example.com>}"
HOMEPAGE="https://github.com/marufmoinuddin/pulseaudio-equalizer-ladspa-fedora"

BUILD_DEPS=(
    build-essential
    dpkg-dev
    debhelper
    dh-python
    fakeroot
    meson
    ninja-build
    pkg-config
    python3
    python3-dev
    libglib2.0-dev
    swh-plugins
)

# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------

die() { echo "error: $*" >&2; exit 1; }
info() { echo "==> $*"; }
warn() { echo "warning: $*" >&2; }

CLEANUP_DIRS=()
cleanup() {
    local d
    for d in "${CLEANUP_DIRS[@]}"; do
        [[ -n "$d" ]] && rm -rf "$d"
    done
}
trap cleanup EXIT

usage() {
    awk '/^# =+$/{n++} n>=1 && n<3' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
    exit 0
}

APT_UPDATED=0
apt_update_once() {
    if [[ "$APT_UPDATED" -eq 0 ]]; then
        sudo apt-get update -qq
        APT_UPDATED=1
    fi
}

apt_install() {
    local pkg
    local -a missing=()
    for pkg in "$@"; do
        dpkg -s "$pkg" >/dev/null 2>&1 || missing+=("$pkg")
    done
    [[ "${#missing[@]}" -eq 0 ]] && return 0
    echo "    apt-get install ${missing[*]}"
    apt_update_once
    sudo apt-get install -y --no-install-recommends "${missing[@]}"
}

detect_distro() {
    [[ -r /etc/os-release ]] || die "/etc/os-release not found - not a Debian/Ubuntu system"
    # shellcheck disable=SC1091
    . /etc/os-release
    DISTRO_ID="${ID:-unknown}"
    DISTRO_VERSION="${VERSION_ID:-}"
    DISTRO_PRETTY="${PRETTY_NAME:-${DISTRO_ID} ${DISTRO_VERSION}}"
    CODENAME="${VERSION_CODENAME:-${UBUNTU_CODENAME:-}}"
    CODENAME="${CODENAME:-unstable}"
}

check_supported_release() {
    if [[ "$DISTRO_ID" == "ubuntu" && -n "$DISTRO_VERSION" ]]; then
        local major="${DISTRO_VERSION%%.*}"
        if [[ "$major" -lt "$MIN_UBUNTU_MAJOR" || "$major" -gt "$MAX_UBUNTU_MAJOR" ]]; then
            warn "Ubuntu ${DISTRO_VERSION} is outside the supported range (22.04 - 26.04); continuing anyway"
        fi
    elif [[ "$DISTRO_ID" != "ubuntu" && "$DISTRO_ID" != "debian" ]]; then
        warn "unexpected distribution '${DISTRO_ID}'; this script targets Ubuntu 22.04 - 26.04 and Debian"
    fi
}

install_build_deps() {
    if [[ "${SKIP_DEPS:-0}" == "1" ]]; then
        info "SKIP_DEPS=1 - not touching apt"
        return 0
    fi
    command -v sudo >/dev/null 2>&1 || die "sudo is required to install build dependencies"
    info "Installing build dependencies"
    apt_install "${BUILD_DEPS[@]}"
}

# Ubuntu 22.04 ships meson 0.61, the project wants >= 0.63 -> use a local venv.
ensure_meson() {
    local current=""
    if command -v meson >/dev/null 2>&1; then
        current="$(meson --version)"
        if dpkg --compare-versions "$current" ge 0.63.0; then
            echo "    meson ${current}"
            return 0
        fi
    fi
    info "meson >= 0.63.0 missing (found: ${current:-none}) - bootstrapping a local venv"
    apt_install python3-venv
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --quiet --upgrade pip
    "$VENV_DIR/bin/pip" install --quiet 'meson>=1.3,<2'
    export PATH="${VENV_DIR}/bin:${PATH}"
    echo "    meson $(meson --version) (${VENV_DIR})"
}

compute_version() {
    if [[ -n "${DEB_VERSION:-}" ]]; then
        UPSTREAM_VERSION="$DEB_VERSION"
    else
        local meson_version
        meson_version="$(sed -n "s/^[[:space:]]*version[[:space:]]*:[[:space:]]*'\([^']*\)'.*/\1/p" \
            "${SCRIPT_DIR}/meson.build" | head -n1)"
        UPSTREAM_VERSION="${meson_version:-$FALLBACK_VERSION}"
        # '-' is not allowed in a dpkg upstream version; '~' keeps the ordering sane
        UPSTREAM_VERSION="${UPSTREAM_VERSION//-/\~}"
        if git -C "$SCRIPT_DIR" rev-parse --git-dir >/dev/null 2>&1; then
            local count hash
            count="$(git -C "$SCRIPT_DIR" rev-list --count HEAD)"
            hash="$(git -C "$SCRIPT_DIR" rev-parse --short HEAD)"
            UPSTREAM_VERSION="${UPSTREAM_VERSION}+git${count}.g${hash}"
        fi
    fi
    # Debian policy: the upstream version must start with a digit
    case "$UPSTREAM_VERSION" in
        [0-9]*) ;;
        *) UPSTREAM_VERSION="0~${UPSTREAM_VERSION}" ;;
    esac
}

stage_source() {
    local target="$1"
    git -C "$SCRIPT_DIR" rev-parse --git-dir >/dev/null 2>&1 \
        || die "not a git repository - cannot stage the source tree"

    rm -rf "$target"
    mkdir -p "$target"
    info "Staging source tree -> ${target}"
    git -C "$SCRIPT_DIR" ls-files -z --cached --others --exclude-standard \
        | grep -zvE '^(dist|debian|build|_build|\.deb-build-venv)/' \
        | tar -C "$SCRIPT_DIR" --null -cf - -T - | tar -xf - -C "$target"
}

write_debian_dir() {
    local root="$1"
    local dir="${root}/debian"
    local now
    now="$(date -R)"

    mkdir -p "${dir}/source"
    printf '3.0 (native)\n' > "${dir}/source/format"

    cat > "${dir}/control" <<CONTROL
Source: ${PACKAGE_NAME}
Section: sound
Priority: optional
Maintainer: ${MAINTAINER}
Build-Depends: debhelper-compat (= 13),
               dh-sequence-python3,
               meson,
               ninja-build,
               pkg-config,
               python3,
               python3-dev,
               libglib2.0-dev
Standards-Version: 4.6.2
Homepage: ${HOMEPAGE}
Rules-Requires-Root: no

Package: ${PACKAGE_NAME}
Architecture: all
Depends: \${misc:Depends},
         \${python3:Depends},
         bash,
         python3,
         python3-gi,
         gir1.2-gtk-3.0,
         swh-plugins,
         pipewire-pulse | pulseaudio
Provides: ${PACKAGE_NAME}-pipewire
Conflicts: ${PACKAGE_NAME}-pipewire
Description: 15-band LADSPA equalizer for PulseAudio/PipeWire
 A LADSPA based multiband equalizer for PulseAudio or PipeWire (with the
 PulseAudio compatibility layer). It provides a 15-band graphic equalizer
 interface built with GTK3 and PyGObject, enabling real-time audio
 equalization through PulseAudio's LADSPA sink module or PipeWire's
 PulseAudio compatibility layer.
 .
 This package is the PipeWire optimised build derived from the upstream
 pulseaudio-equalizer-ladspa project.
CONTROL

    cat > "${dir}/changelog" <<CHANGELOG
${PACKAGE_NAME} (${UPSTREAM_VERSION}) ${CODENAME}; urgency=medium

  * Local build for ${DISTRO_PRETTY} (${CODENAME}).
  * Built from git ${GIT_HASH:-unknown}.

 -- ${MAINTAINER}  ${now}
CHANGELOG

    printf '%s\n' 'README.md' 'LICENSE' > "${dir}/docs"

    # Modern debhelper does not copy debian/tmp in automatically - list what
    # meson installs so dh_install picks it up (dh_missing fails otherwise).
    cat > "${dir}/${PACKAGE_NAME}.install" <<INSTALL
usr/bin/pulseaudio-equalizer
usr/bin/pulseaudio-equalizer-gtk
usr/bin/pulseaudio-equalizer-autostart
usr/share/${PACKAGE_NAME}
usr/share/applications/${APP_ID}.desktop
usr/share/icons/hicolor/scalable/apps/${PACKAGE_NAME}.svg
usr/lib/systemd/user/pulseaudio-equalizer.service
usr/lib/python3/dist-packages/pulseeq
INSTALL

    cat > "${dir}/copyright" <<'COPYRIGHT'
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: pulseaudio-equalizer-ladspa
Source: https://github.com/pulseaudio-equalizer-ladspa/equalizer

Files: *
Copyright: upstream pulseaudio-equalizer-ladspa contributors
License: GPL-3+
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 .
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 .
 On Debian systems, the complete text of the GNU General Public License
 version 3 can be found in "/usr/share/common-licenses/GPL-3".
COPYRIGHT

    # debian/rules is generated with printf so the recipe lines keep real tabs.
    {
        printf '%s\n' '#!/usr/bin/make -f' ''
        printf '%s\n' 'export DH_VERBOSE = 1'
        printf '%s\n' 'export DEB_BUILD_MAINT_OPTIONS = hardening=+all' ''
        printf 'PURELIB_REL ?= %s\n\n' "$PURELIB_REL"
        printf '%s\n' '%:'
        printf '\tdh $@\n\n'
        printf '%s\n' '# The project has no C code; meson + ninja are driven directly so that'
        printf '%s\n' '# the python module lands in /usr/lib/python3/dist-packages (Debian layout)'
        printf '%s\n' '# instead of site-packages, and so libdir stays "lib" for the systemd'
        printf '%s\n' '# user unit (/usr/lib/systemd/user).'
        printf '%s\n' 'override_dh_auto_configure:'
        printf '\tmeson setup build --prefix=/usr --libdir=lib --buildtype=plain -Dpurelib=$(PURELIB_REL)\n\n'
        printf '%s\n' 'override_dh_auto_build:'
        printf '\tninja -C build\n\n'
        printf '%s\n' 'override_dh_auto_test:'
        printf '\t@echo "no upstream test suite; the .deb is checked by build-ubuntu-deb.sh"\n\n'
        printf '%s\n' 'override_dh_auto_install:'
        printf '\tDESTDIR=$(CURDIR)/debian/tmp ninja -C build install\n\n'
        printf '%s\n' 'override_dh_auto_clean:'
        printf '\trm -rf build\n\n'
        printf '%s\n' 'override_dh_python3:'
        printf '\tdh_python3 --shebang=/usr/bin/python3\n'
    } > "${dir}/rules"
    chmod 0755 "${dir}/rules"
}

run_build() {
    local root="$1"
    info "Running dpkg-buildpackage (this may take a while)"
    ( cd "$root" && dpkg-buildpackage -us -uc -b -d --no-sign )
}

verify_package() {
    local deb="$1"
    local root
    local failures=0
    root="$(mktemp -d)"
    CLEANUP_DIRS+=("$root")

    dpkg-deb -x "$deb" "$root"

    info "Checking installed layout"
    local -a expected=(
        "usr/bin/pulseaudio-equalizer"
        "usr/bin/pulseaudio-equalizer-gtk"
        "usr/bin/pulseaudio-equalizer-autostart"
        "usr/share/applications/${APP_ID}.desktop"
        "usr/share/icons/hicolor/scalable/apps/pulseaudio-equalizer-ladspa.svg"
        "usr/share/${PACKAGE_NAME}/${APP_ID}.gresource"
        "usr/share/${PACKAGE_NAME}/presets/Flat.preset"
        "usr/lib/systemd/user/pulseaudio-equalizer.service"
        "usr/lib/python3/dist-packages/pulseeq/constants.py"
        "usr/lib/python3/dist-packages/pulseeq/pulse.py"
        "usr/lib/python3/dist-packages/pulseeq/presets.py"
    )
    local f
    for f in "${expected[@]}"; do
        if [[ -e "${root}/${f}" ]]; then
            printf '    ok      %s\n' "$f"
        else
            printf '    MISSING %s\n' "$f"
            failures=$((failures + 1))
        fi
    done

    info "Checking generated scripts"
    if [[ -x "${root}/usr/bin/pulseaudio-equalizer-gtk" ]]; then
        if grep -q '@[A-Za-z_]*@' "${root}/usr/bin/pulseaudio-equalizer-gtk"; then
            echo "    ERROR: unsubstituted placeholders in pulseaudio-equalizer-gtk"
            failures=$((failures + 1))
        else
            printf '    ok      shebang: %s\n' "$(head -n1 "${root}/usr/bin/pulseaudio-equalizer-gtk")"
        fi
    fi

    info "Checking python modules"
    if PYTHONPATH="${root}/usr/lib/python3/dist-packages" \
        python3 -c "import pulseeq.constants" 2>/dev/null; then
        echo "    ok      pulseeq.constants"
    else
        echo "    ERROR: cannot import pulseeq.constants from the built package"
        failures=$((failures + 1))
    fi

    # pulseeq.pulse exits when no MBEQ LADSPA plugin is present, so only run the
    # deeper check when swh-plugins is installed on this host.
    if compgen -G '/usr/lib*/ladspa/mbeq*.so' >/dev/null; then
        if PYTHONPATH="${root}/usr/lib/python3/dist-packages" \
            python3 -c "from pulseeq.pulse import EqualizerState; EqualizerState()" 2>/dev/null; then
            echo "    ok      pulseeq.pulse (MBEQ plugin detected)"
        else
            echo "    ERROR: pulseeq.pulse failed to import"
            failures=$((failures + 1))
        fi
    else
        echo "    skipped pulseeq.pulse (no MBEQ plugin on this host)"
    fi

    return "$failures"
}

# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------

case "${1:-}" in
    -h|--help) usage ;;
    "") ;;
    *) die "unknown argument: $1 (try --help)" ;;
esac

command -v dpkg-buildpackage >/dev/null 2>&1 || die "dpkg-buildpackage not found (install dpkg-dev)"
command -v git >/dev/null 2>&1 || die "git not found"
[[ -f "${SCRIPT_DIR}/meson.build" ]] || die "meson.build not found in ${SCRIPT_DIR}"

detect_distro
check_supported_release
info "Target: ${DISTRO_PRETTY} (codename: ${CODENAME})"

GIT_HASH=""
if git -C "$SCRIPT_DIR" rev-parse --git-dir >/dev/null 2>&1; then
    GIT_HASH="$(git -C "$SCRIPT_DIR" rev-parse --short HEAD)"
fi

compute_version
info "Version: ${UPSTREAM_VERSION}"
echo "    python modules -> /usr/${PURELIB_REL}/pulseeq"

install_build_deps
ensure_meson

BUILD_ROOT="${DIST_DIR}/${PACKAGE_NAME}-${UPSTREAM_VERSION}"
mkdir -p "$DIST_DIR"
stage_source "$BUILD_ROOT"
write_debian_dir "$BUILD_ROOT"

run_build "$BUILD_ROOT"

DEB_FILE="$(find "$DIST_DIR" -maxdepth 1 -name "${PACKAGE_NAME}_${UPSTREAM_VERSION}_*.deb" -print -quit)"
[[ -n "$DEB_FILE" ]] || die "no .deb produced in ${DIST_DIR}"

verify_package "$DEB_FILE" || die "package verification failed for ${DEB_FILE}"

if [[ "${KEEP_BUILD:-0}" != "1" ]]; then
    rm -rf "$BUILD_ROOT"
fi

echo
info "Build completed successfully."
echo
echo "Package:"
dpkg-deb --info "$DEB_FILE" | sed 's/^/    /'
echo "    size: $(du -h "$DEB_FILE" | cut -f1)"
echo "    files: $(dpkg-deb --contents "$DEB_FILE" | grep -c '^-')"
echo
echo "Install with:"
echo "    sudo apt install ${DEB_FILE}"
echo
echo "Then enable auto-start (optional):"
echo "    pulseaudio-equalizer-autostart enable"
echo
echo "Note: remove a previously installed copy first if it came from pip or a"
echo "      vendor package, e.g.  sudo apt remove ${PACKAGE_NAME}"
