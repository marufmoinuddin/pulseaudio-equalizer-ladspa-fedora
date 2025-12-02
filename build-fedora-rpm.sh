#!/bin/bash
# Build script for Fedora RPM package - PipeWire Compatible Version

set -e

# Package information
PACKAGE_NAME="pulseaudio-equalizer-ladspa"
VERSION="2.8.1"
SPEC_FILE="${PACKAGE_NAME}.spec"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building Fedora RPM package for ${PACKAGE_NAME} (PipeWire Compatible)${NC}"

# Check if we're running on Fedora
if ! command -v dnf &> /dev/null; then
    echo -e "${RED}Error: This script is designed for Fedora systems with dnf${NC}"
    exit 1
fi

# Check if spec file exists
if [ ! -f "$SPEC_FILE" ]; then
    echo -e "${RED}Error: Spec file $SPEC_FILE not found${NC}"
    exit 1
fi

# Install build dependencies
echo -e "${YELLOW}Installing build dependencies...${NC}"
sudo dnf install -y rpm-build rpmdevtools meson ninja-build python3-devel python3-setuptools gcc glib2-devel gtk3-devel

# Set up RPM build tree
echo -e "${YELLOW}Setting up RPM build environment...${NC}"
rpmdev-setuptree

# Copy spec file
echo -e "${YELLOW}Copying spec file...${NC}"
cp "$SPEC_FILE" ~/rpmbuild/SPECS/

# Create source archive from current repository
SOURCE_FILE="${PACKAGE_NAME}-${VERSION}.tar.gz"
echo -e "${YELLOW}Creating source archive from current working directory...${NC}"
cd "$(dirname "$0")"
# Remove old tarball to ensure fresh build
rm -f ~/rpmbuild/SOURCES/"$SOURCE_FILE"
# Create tarball from working directory instead of git to include uncommitted changes
tar --transform="s,^,${PACKAGE_NAME}-${VERSION}-pipewire/," \
    --exclude='.git' --exclude='*.pyc' --exclude='__pycache__' \
    --exclude='build' --exclude='*.rpm' --exclude='*.tar.gz' \
    -czf ~/rpmbuild/SOURCES/"$SOURCE_FILE" .
cd - > /dev/null

# Install build-time dependencies
echo -e "${YELLOW}Installing build-time dependencies...${NC}"
sudo dnf builddep -y ~/rpmbuild/SPECS/"$SPEC_FILE"

# Build the package
echo -e "${YELLOW}Building RPM package...${NC}"
cd ~/rpmbuild/SPECS/
rpmbuild -ba "$SPEC_FILE"

# Check if build was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Build completed successfully!${NC}"
    echo -e "${GREEN}Built packages:${NC}"
    find ~/rpmbuild/RPMS/ -name "${PACKAGE_NAME}*.rpm" -ls
    find ~/rpmbuild/SRPMS/ -name "${PACKAGE_NAME}*.src.rpm" -ls
    
    echo -e "${YELLOW}To install the package, run:${NC}"
    BUILT_RPM=$(find ~/rpmbuild/RPMS/ -name "${PACKAGE_NAME}-${VERSION}*.rpm" | head -1)
    echo "sudo dnf install $BUILT_RPM"
    
    echo -e "${YELLOW}To test the application, run:${NC}"
    echo "pulseaudio-equalizer-gtk"
else
    echo -e "${RED}Build failed!${NC}"
    exit 1
fi
