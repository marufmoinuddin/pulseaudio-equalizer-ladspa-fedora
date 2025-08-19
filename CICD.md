# CI/CD Pipeline Documentation

## Overview

This repository includes a comprehensive CI/CD pipeline that automatically builds, tests, and releases Fedora RPM packages for pulseaudio-equalizer-ladspa.

## 🔄 Workflows

### 1. Development Build (`dev-build.yml`)

**Triggers:**
- Push to `main` or `fedora-conversion` branches
- Manual trigger via GitHub Actions UI

**Purpose:**
- Creates development RPMs for testing
- Provides quick feedback on build status

**Artifacts:**
- Development RPMs with commit SHA in version
- Retained for 7 days
- Available for download from Actions tab

**Example Development Version:**
```
Original: 4.0.1-1.fc42
Dev Build: 4.0.1-0.dev20241212.git1a2b3c4d.fc42
```

### 2. Continuous Integration (`ci.yml`)

**Triggers:**
- Pull requests
- Pushes to any branch

**Jobs:**
1. **Spec Linting** - Validates RPM spec file syntax
2. **Build Testing** - Tests builds on Fedora 40, 41, and 42
3. **Shell Linting** - Checks shell scripts with ShellCheck
4. **Documentation Check** - Ensures docs are up-to-date

**Quality Gates:**
- All jobs must pass for PR approval
- Provides build logs for debugging
- Multi-version compatibility verification

### 3. Release Pipeline (`build-and-release.yml`)

**Triggers:**
- Git tags matching pattern `v*` (e.g., `v4.0.1`)

**Process:**
1. **Build RPM** - Creates production packages
2. **Test RPM** - Validates package installation
3. **Create Release** - Publishes GitHub release

**Outputs:**
- Source RPM (SRPM)
- Binary RPM (noarch)
- GitHub release with changelog
- Automated release notes

## 🚀 Usage Guide

### Development Workflow

1. **Make Changes:**
   ```bash
   git checkout -b feature/my-feature
   # Make your changes
   git add .
   git commit -m "Add new feature"
   git push origin feature/my-feature
   ```

2. **Create Pull Request:**
   - CI pipeline automatically runs
   - Check status in GitHub Actions tab
   - Fix any failing tests

3. **Test Development Build:**
   - Merge to main triggers dev build
   - Download RPMs from Actions artifacts
   - Test manually if needed

### Creating Releases

1. **Update Version:**
   ```bash
   # Update version in pulseaudio-equalizer-ladspa.spec
   vim pulseaudio-equalizer-ladspa.spec
   
   # Update CHANGELOG.md with release notes
   vim CHANGELOG.md
   
   git add . && git commit -m "Bump version to 4.0.2"
   ```

2. **Create Release Tag:**
   ```bash
   git tag -a v4.0.2 -m "Release version 4.0.2"
   git push origin v4.0.2
   ```

3. **Monitor Release:**
   - Release pipeline automatically triggers
   - Check GitHub Actions for build status
   - Release appears in GitHub Releases section

### Manual Testing

**Download Development RPM:**
```bash
# From GitHub Actions artifacts
wget https://github.com/marufmoinuddin/pulseaudio-equalizer-ladspa-fedora/actions/runs/[RUN_ID]/artifacts/[ARTIFACT_ID]

# Install and test
sudo dnf install pulseaudio-equalizer-ladspa-*.rpm
```

**Local Build Testing:**
```bash
# Test the build script
chmod +x build-fedora-rpm.sh
./build-fedora-rpm.sh

# Manual spec testing
rpmdev-setuptree
spectool -g -R pulseaudio-equalizer-ladspa.spec
rpmbuild -ba pulseaudio-equalizer-ladspa.spec
```

## 🛠️ Pipeline Configuration

### Environment Variables

The workflows use these automatic variables:
- `GITHUB_SHA` - Commit hash for development versions
- `GITHUB_REF` - Branch/tag reference
- `GITHUB_REPOSITORY` - Repository name for releases

### Fedora Container

All builds use `fedora:42` container with these packages:
- `rpm-build rpmdevtools` - RPM building tools
- `meson ninja-build` - Build system
- `python3-devel python3-setuptools` - Python dependencies
- `glib2-devel bc bash` - Runtime dependencies

### Artifact Retention

- **Development builds**: 7 days
- **Release builds**: Permanent (attached to release)
- **CI logs**: 90 days (GitHub default)

## 📋 Troubleshooting

### Common Issues

1. **Spec File Errors:**
   ```
   Error: Spec file parsing failed
   ```
   - Check spec file syntax with `rpmlint`
   - Verify all dependencies are available in Fedora repos

2. **Build Failures:**
   ```
   Error: Build dependencies not found
   ```
   - Check if package names are correct for target Fedora version
   - Verify BuildRequires section in spec file

3. **Download Failures:**
   ```
   Error: Source download failed
   ```
   - Verify source URL is accessible
   - Check if version tag exists in upstream repository

### Debug Commands

**Check workflow status:**
```bash
gh workflow list
gh run list --workflow=ci.yml
gh run view [RUN_ID] --log
```

**Test locally:**
```bash
# Test in Fedora container
podman run -it --rm -v $(pwd):/workspace fedora:42
cd /workspace
dnf install -y rpm-build rpmdevtools meson ninja-build
./build-fedora-rpm.sh
```

## 📈 Monitoring

### Success Indicators

- ✅ All CI jobs pass (green checkmarks)
- ✅ Development artifacts are created
- ✅ Releases are published automatically
- ✅ RPMs install without dependency issues

### Metrics to Watch

- **Build time**: Should complete in 5-10 minutes
- **Test coverage**: All quality gates passing
- **Artifact size**: RPMs should be ~50-100KB
- **Download success**: Source downloads complete

## 🔧 Maintenance

### Regular Tasks

1. **Update Fedora versions** in CI matrix as new versions release
2. **Review and update dependencies** when Fedora packages change
3. **Monitor upstream changes** for new releases
4. **Update build tools** if meson/ninja requirements change

### Pipeline Updates

To modify workflows:
1. Edit files in `.github/workflows/`
2. Test changes in feature branch
3. Monitor workflow runs for issues
4. Update documentation as needed

This CI/CD pipeline provides automated, reliable packaging for Fedora users while maintaining high quality standards.
