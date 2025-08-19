# Version Management Guide

## 🔧 Version Alignment Fix

This document explains how to properly manage version alignment between our Fedora package and the upstream source.

## 📝 Current Setup

**Package Version**: `4.0.1` (our Fedora package version)  
**Source Version**: `3.0.2` (upstream equalizer version)  
**Why Different**: We maintain our own version numbering for Fedora packaging

## 🔄 Version Update Process

### For New Upstream Releases

1. **Check Upstream Versions:**
   ```bash
   curl -s "https://api.github.com/repos/pulseaudio-equalizer-ladspa/equalizer/releases" | grep '"tag_name"'
   ```

2. **Update Spec File:**
   ```bash
   # Edit pulseaudio-equalizer-ladspa.spec
   # Update these lines:
   Version:        X.Y.Z  # Your new package version
   Source0:        https://github.com/pulseaudio-equalizer-ladspa/equalizer/archive/vA.B.C.tar.gz#/%{name}-%{version}.tar.gz
   %autosetup -n equalizer-A.B.C  # Use upstream version in directory name
   ```

3. **Update Build Scripts:**
   ```bash
   # In build-fedora-rpm.sh and CI/CD workflows, update:
   wget "https://github.com/pulseaudio-equalizer-ladspa/equalizer/archive/vA.B.C.tar.gz"
   ```

4. **Update Changelog:**
   ```bash
   # Add entry to %changelog section in spec file
   * Date Name <email> - X.Y.Z-1
   - Update to upstream version A.B.C
   - List of changes
   ```

### For Release Testing

1. **Commit Changes:**
   ```bash
   git add .
   git commit -m "Update to upstream version A.B.C"
   git push origin main
   ```

2. **Create Test Tag:**
   ```bash
   git tag -a vX.Y.Z-test -m "Test release for version X.Y.Z"
   git push origin vX.Y.Z-test
   ```

3. **Monitor CI/CD:**
   - Check GitHub Actions for build status
   - Verify artifacts are created correctly
   - Test RPM installation

4. **Create Official Release:**
   ```bash
   git tag -a vX.Y.Z -m "Release version X.Y.Z"
   git push origin vX.Y.Z
   ```

## 🔍 Troubleshooting

### "Artifact not found" Error

**Cause**: Version mismatch between tag and spec file  
**Fix**: Ensure tag version matches `Version:` field in spec file

### "Source download failed" Error

**Cause**: Upstream version doesn't exist  
**Fix**: Verify upstream version exists:
```bash
curl -I "https://github.com/pulseaudio-equalizer-ladspa/equalizer/archive/vA.B.C.tar.gz"
```

### "Spec file parsing error" Error

**Cause**: Syntax error in spec file  
**Fix**: Test locally:
```bash
rpmlint pulseaudio-equalizer-ladspa.spec
rpmdev-setuptree
spectool -g -R pulseaudio-equalizer-ladspa.spec
```

## 📋 Checklist for New Releases

- [ ] Upstream version verified to exist
- [ ] Spec file `Version:` field updated
- [ ] Spec file `Source0` URL updated with correct upstream version
- [ ] Spec file `%autosetup -n` updated with correct directory name
- [ ] Build script updated with correct download URL
- [ ] CI/CD workflows updated with correct download URL
- [ ] Changelog updated with release notes
- [ ] Local build tested successfully
- [ ] Test tag created and CI/CD pipeline verified
- [ ] Official release tag created

## 🎯 Current Working Example

For the current setup:
```spec
Version:        4.0.1
Source0:        https://github.com/pulseaudio-equalizer-ladspa/equalizer/archive/v3.0.2.tar.gz#/%{name}-%{version}.tar.gz
%autosetup -n equalizer-3.0.2
```

This downloads upstream `v3.0.2` source but packages it as our version `4.0.1`.

## 🚀 Quick Fix Script

```bash
#!/bin/bash
# Quick version update script
NEW_PKG_VERSION="$1"    # e.g., 4.0.2
UPSTREAM_VERSION="$2"   # e.g., 3.0.3

if [ -z "$NEW_PKG_VERSION" ] || [ -z "$UPSTREAM_VERSION" ]; then
    echo "Usage: $0 <new_package_version> <upstream_version>"
    echo "Example: $0 4.0.2 3.0.3"
    exit 1
fi

# Update spec file
sed -i "s/^Version:.*/Version:        $NEW_PKG_VERSION/" pulseaudio-equalizer-ladspa.spec
sed -i "s|archive/v.*\.tar\.gz|archive/v$UPSTREAM_VERSION.tar.gz|" pulseaudio-equalizer-ladspa.spec
sed -i "s/equalizer-.*/equalizer-$UPSTREAM_VERSION/" pulseaudio-equalizer-ladspa.spec

# Update build script
sed -i "s|archive/v.*\.tar\.gz|archive/v$UPSTREAM_VERSION.tar.gz|" build-fedora-rpm.sh

# Update CI/CD workflows
sed -i "s|archive/v.*\.tar\.gz|archive/v$UPSTREAM_VERSION.tar.gz|" .github/workflows/*.yml

echo "Updated to package version $NEW_PKG_VERSION using upstream $UPSTREAM_VERSION"
echo "Please update the changelog manually and test the build!"
```
