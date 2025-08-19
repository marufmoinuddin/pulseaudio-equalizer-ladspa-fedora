# Manual Release Guide

## 🎯 Overview

The Manual Build and Release workflow allows you to create custom RPM releases on-demand without requiring git tag pushes. This gives you full control over version numbering, release timing, and release content.

## 🚀 Quick Start

### Access the Workflow
1. Go to your GitHub repository
2. Click **Actions** tab
3. Select **Manual Build and Release** from the workflow list
4. Click **Run workflow** button

### Basic Release Example
```
Release Tag: v4.0.2
Package Version: 4.0.2
Upstream Version: 3.0.2
Release Title: Fedora 42 Package v4.0.2
```

## 📋 Input Parameters

### Required Inputs

| Parameter | Description | Example | Notes |
|-----------|-------------|---------|-------|
| **Release Tag** | Git tag for the release | `v4.0.2` | Must start with 'v' and follow semver |
| **Package Version** | Version in RPM spec file | `4.0.2` | Should match tag without 'v' prefix |
| **Upstream Version** | Source version to download | `3.0.2` | Must exist in upstream repository |

### Optional Inputs

| Parameter | Description | Default | Notes |
|-----------|-------------|---------|-------|
| **Release Title** | Custom release title | `Release {tag}` | Shown in GitHub release |
| **Release Notes** | Changelog/description | Auto-generated | Markdown supported |
| **Create Draft** | Make draft release | `false` | Draft allows review before publishing |
| **Skip Tests** | Skip RPM testing | `false` | Use for known-good builds only |

## 🔧 Usage Examples

### Standard Release
```yaml
Release Tag: v4.0.3
Package Version: 4.0.3
Upstream Version: 3.0.2
Release Title: "Fedora Package Update v4.0.3"
Release Notes: |
  ## Changes
  - Updated packaging for Fedora 42
  - Fixed dependency issues
  - Improved installation process
Create Draft: false
Skip Tests: false
```

### Beta Release
```yaml
Release Tag: v4.1.0-beta1
Package Version: 4.1.0.beta1
Upstream Version: 3.0.2
Release Title: "Beta Release v4.1.0-beta1"
Release Notes: |
  ## Beta Release
  ⚠️ This is a beta release for testing purposes.
  
  ## New Features
  - Feature A
  - Feature B
  
  ## Testing Needed
  - Test installation on clean Fedora 42
  - Verify equalizer functionality
Create Draft: true
Skip Tests: false
```

### Quick Rebuild
```yaml
Release Tag: v4.0.2-hotfix
Package Version: 4.0.2
Upstream Version: 3.0.2
Release Title: "Hotfix: Rebuild for Fedora updates"
Release Notes: "Rebuilt package with latest Fedora 42 dependencies"
Create Draft: false
Skip Tests: true
```

## 🔍 Workflow Process

### 1. Input Validation
- ✅ **Tag Format**: Validates semver format (v1.2.3)
- ✅ **Version Format**: Checks package version format
- ✅ **Upstream Check**: Verifies upstream version exists
- ✅ **Availability**: Confirms source tarball is downloadable

### 2. RPM Build Process
- 🔧 **Spec Generation**: Creates custom spec file with your versions
- 📥 **Source Download**: Downloads upstream source tarball
- 🔨 **Build**: Compiles RPM using rpmbuild
- 📦 **Artifacts**: Creates binary and source RPMs

### 3. Quality Testing (unless skipped)
- 🧪 **Installation Test**: Verifies RPM installs correctly
- 🔍 **Integrity Check**: Validates RPM signatures and metadata
- ⚙️ **Functionality**: Basic command availability checks

### 4. Release Creation
- 🏷️ **Tag Management**: Creates/updates git tag
- 📝 **Release Notes**: Generates or uses provided notes
- 📤 **Asset Upload**: Attaches RPM files to release
- 🎉 **Publication**: Publishes release (or creates draft)

## 🛠️ Advanced Features

### Version Mapping
The workflow handles version mismatches between your package and upstream:
```
Your Package: v4.0.2 (Fedora packaging version)
Upstream: v3.0.2 (Original software version)
Source: Downloads v3.0.2, packages as v4.0.2
```

### Tag Management
- **Existing Tags**: Automatically overwrites existing tags
- **Remote Sync**: Pushes tags to GitHub repository
- **Release Linking**: Links releases to correct git commits

### Draft Releases
- Create releases for review before publishing
- Test download links and installation
- Edit release notes before making public
- Publish when ready via GitHub UI

### Pre-release Detection
Automatically marks releases as pre-release for:
- Tags containing `beta`, `alpha`, `rc`
- Example: `v4.1.0-beta1` → Pre-release ✅

## 📊 Build Outputs

### Artifacts Created
- **Binary RPM**: `pulseaudio-equalizer-ladspa-{version}-1.fc42.noarch.rpm`
- **Source RPM**: `pulseaudio-equalizer-ladspa-{version}-1.fc42.src.rpm`
- **Build Logs**: Available in GitHub Actions

### Release Assets
- RPMs automatically attached to GitHub release
- Direct download links provided
- Installation commands included in release notes

## ⚠️ Important Notes

### Version Consistency
- Package version should match release tag (without 'v')
- Upstream version must exist in source repository
- Build will fail if versions are inconsistent

### Tag Overwrites
- Workflow will overwrite existing tags with same name
- Use unique tags to avoid conflicts
- Consider using build numbers for iterations

### Testing Recommendations
- Always test with draft releases first
- Verify installation on clean Fedora system
- Check that equalizer starts and functions correctly

## 🔧 Troubleshooting

### Common Issues

**"Invalid tag format" Error**
```
❌ Problem: Tag doesn't follow v1.2.3 format
✅ Solution: Use proper semver format (v4.0.2, v4.1.0-beta1)
```

**"Upstream version not found" Error**
```
❌ Problem: Specified upstream version doesn't exist
✅ Solution: Check available versions:
curl -s "https://api.github.com/repos/pulseaudio-equalizer-ladspa/equalizer/releases" | grep tag_name
```

**"Build dependencies failed" Error**
```
❌ Problem: Missing build dependencies for Fedora 42
✅ Solution: Check spec file BuildRequires section matches Fedora 42 packages
```

**"RPM test failed" Error**
```
❌ Problem: Package doesn't install or run correctly
✅ Solution: Enable "Skip Tests" for urgent releases, fix issues later
```

### Debug Steps

1. **Check Workflow Run**: View detailed logs in GitHub Actions
2. **Download Artifacts**: Test RPM installation manually
3. **Verify Spec File**: Check generated spec file in build logs
4. **Test Locally**: Use local build script for debugging

## 📚 Examples Gallery

### Security Update
```yaml
Release Tag: v4.0.4-security
Package Version: 4.0.4
Upstream Version: 3.0.2
Release Title: "Security Update v4.0.4"
Release Notes: |
  ## 🔒 Security Update
  
  This release rebuilds the package with updated dependencies to address:
  - CVE-2024-XXXX (if applicable)
  - Updated system libraries
  
  ## Installation
  ```bash
  sudo dnf update pulseaudio-equalizer-ladspa
  ```
```

### Feature Release
```yaml
Release Tag: v5.0.0
Package Version: 5.0.0
Upstream Version: 4.0.0
Release Title: "Major Update v5.0.0"
Release Notes: |
  ## 🎉 Major Update v5.0.0
  
  ### New Features
  - Updated to upstream version 4.0.0
  - Enhanced UI improvements
  - Better Fedora integration
  
  ### Breaking Changes
  - Configuration file format updated
  - See migration guide in documentation
  
  ### Installation
  ```bash
  wget https://github.com/marufmoinuddin/pulseaudio-equalizer-ladspa-fedora/releases/download/v5.0.0/pulseaudio-equalizer-ladspa-5.0.0-1.fc42.noarch.rpm
  sudo dnf install pulseaudio-equalizer-ladspa-*.rpm
  ```
```

### Maintenance Release
```yaml
Release Tag: v4.0.3-maint
Package Version: 4.0.3
Upstream Version: 3.0.2
Release Title: "Maintenance Release"
Release Notes: "Rebuilt for Fedora 42 package updates and dependency refreshes"
Create Draft: false
Skip Tests: true
```

## 🎯 Best Practices

1. **Test First**: Use draft releases for testing
2. **Version Increment**: Always increment version numbers
3. **Clear Notes**: Provide meaningful release notes
4. **Consistent Naming**: Use consistent tag naming scheme
5. **Backup**: Keep track of working configurations

This manual workflow gives you complete control over your release process while maintaining automation and quality assurance! 🚀
