#!/bin/bash
set -euo pipefail

# Build Fedora RPM for pulseaudio-equalizer-ladspa

PACKAGE_NAME="pulseaudio-equalizer-ladspa"
SPEC_FILE="${PACKAGE_NAME}.spec"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$SCRIPT_DIR"

if ! command -v dnf &>/dev/null; then
    echo "Error: This script requires dnf (Fedora)" >&2
    exit 1
fi

if [ ! -f "$SPEC_FILE" ]; then
    echo "Error: $SPEC_FILE not found in $SCRIPT_DIR" >&2
    exit 1
fi

# Derive version from git commit hash
GIT_HASH=$(git rev-parse --short HEAD)
VERSION="g${GIT_HASH}"

echo "Building $PACKAGE_NAME version $VERSION"
echo ""

# Install RPM build tools if missing
for pkg in rpm-build rpmdevtools meson ninja-build glib2-devel gtk3-devel python3-devel; do
    if ! rpm -q "$pkg" &>/dev/null; then
        echo "Installing $pkg..."
        sudo dnf install -y "$pkg"
    fi
done

# Set up RPM build tree (create ~/rpmbuild if missing)
rpmdev-setuptree 2>/dev/null || {
    mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
}

# Create source tarball from working tree (includes uncommitted, excludes gitignored)
SOURCE_FILE="${PACKAGE_NAME}-${VERSION}.tar.gz"
echo "Creating source archive: $SOURCE_FILE"
git ls-files -z --cached --others --exclude-standard \
  | xargs -0 -r tar czf ~/rpmbuild/SOURCES/"$SOURCE_FILE" \
    --transform "s|^|${PACKAGE_NAME}-${VERSION}-pipewire/|"

# Copy spec file and inject the git-based version
sed "s/^Version:.*/Version:        ${VERSION}/" "$SPEC_FILE" > ~/rpmbuild/SPECS/"$SPEC_FILE"

# Install build dependencies from spec
sudo dnf builddep -y ~/rpmbuild/SPECS/"$SPEC_FILE"

# Build RPM
echo "Building RPM..."
cd ~/rpmbuild/SPECS
rpmbuild -ba "$SPEC_FILE"
cd "$SCRIPT_DIR"

echo ""
echo "Build completed successfully."
echo ""
echo "Built packages:"
find ~/rpmbuild/RPMS/ -name "${PACKAGE_NAME}*.rpm" -ls
find ~/rpmbuild/SRPMS/ -name "${PACKAGE_NAME}*.src.rpm" -ls

BUILT_RPM=$(find ~/rpmbuild/RPMS/ -name "${PACKAGE_NAME}-${VERSION}*.rpm" 2>/dev/null | head -1)
if [ -n "$BUILT_RPM" ]; then
    echo ""
    echo "To install: sudo dnf install $BUILT_RPM"
fi
