# Homebrew Publishing Guide 🍺

Complete guide for publishing audio-transcriber via Homebrew.

## Table of Contents

- [Overview](#overview)
- [Creating a Tap](#creating-a-tap)
- [Formula Creation](#formula-creation)
- [Testing Formula](#testing-formula)
- [Publishing](#publishing)
- [Updating Formula](#updating-formula)
- [Troubleshooting](#troubleshooting)

---

## Overview

### What is Homebrew?

Homebrew is a package manager for macOS and Linux that makes installing software simple:

```bash
brew install audio-transcriber
```

### Distribution Methods

1. **Personal Tap** (Recommended for start)
   - `brew tap lucmuss/tap`
   - `brew install audio-transcriber`
   
2. **Homebrew Core** (Official, requires review)
   - `brew install audio-transcriber`
   - Higher visibility but stricter requirements

---

## Creating a Tap

### Step 1: Create Tap Repository

```bash
# Create new GitHub repository named: homebrew-tap
# URL will be: github.com/lucmuss/homebrew-tap
```

### Step 2: Clone Tap Repository

```bash
git clone https://github.com/lucmuss/homebrew-tap.git
cd homebrew-tap
```

### Step 3: Create Formula Directory

```bash
mkdir -p Formula
```

---

## Formula Creation

### Step 1: Get Package Information

After publishing to PyPI:

```bash
# Get PyPI package URL
URL="https://files.pythonhosted.org/packages/source/a/audio-transcriber/audio-transcriber-1.0.0.tar.gz"

# Calculate SHA256
curl -L $URL | shasum -a 256
```

### Step 2: Create Formula File

Create `Formula/audio-transcriber.rb`:

```ruby
class AudioTranscriber < Formula
  include Language::Python::Virtualenv

  desc "Professional audio transcription tool using OpenAI-compatible Speech-to-Text APIs"
  homepage "https://github.com/lucmuss/audio-transcriber"
  url "https://files.pythonhosted.org/packages/source/a/audio-transcriber/audio-transcriber-1.0.0.tar.gz"
  sha256 "ACTUAL_SHA256_HERE"
  license "MIT"

  depends_on "python@3.11"
  depends_on "ffmpeg"

  resource "openai" do
    url "https://files.pythonhosted.org/packages/source/o/openai/openai-1.30.0.tar.gz"
    sha256 "ACTUAL_SHA256_HERE"
  end

  resource "pydub" do
    url "https://files.pythonhosted.org/packages/source/p/pydub/pydub-0.25.1.tar.gz"
    sha256 "ACTUAL_SHA256_HERE"
  end

  resource "tqdm" do
    url "https://files.pythonhosted.org/packages/source/t/tqdm/tqdm-4.66.1.tar.gz"
    sha256 "ACTUAL_SHA256_HERE"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/audio-transcriber --version")
  end
end
```

### Step 3: Get Dependency SHA256s

For each dependency:

```bash
# OpenAI
curl -L https://files.pythonhosted.org/packages/source/o/openai/openai-1.30.0.tar.gz | shasum -a 256

# pydub
curl -L https://files.pythonhosted.org/packages/source/p/pydub/pydub-0.25.1.tar.gz | shasum -a 256

# tqdm
curl -L https://files.pythonhosted.org/packages/source/t/tqdm/tqdm-4.66.1.tar.gz | shasum -a 256
```

### Step 4: Use brew-pip-audit (Automatic)

Alternatively, use `brew-pip-audit` to auto-generate resources:

```bash
# Install tool
brew install brew-pip-audit

# Generate formula
brew-pip-audit audio-transcriber
```

---

## Testing Formula

### Local Testing

```bash
# Install from local tap
brew install --build-from-source Formula/audio-transcriber.rb

# Test
audio-transcriber --version

# Uninstall
brew uninstall audio-transcriber
```

### Audit Formula

```bash
# Check for issues
brew audit --strict Formula/audio-transcriber.rb

# Test formula
brew test Formula/audio-transcriber.rb
```

### Full Test Cycle

```bash
# Install
brew install Formula/audio-transcriber.rb

# Test basic functionality
audio-transcriber --help
audio-transcriber --version

# Uninstall
brew uninstall audio-transcriber

# Reinstall from tap
brew tap lucmuss/tap
brew install audio-transcriber
```

---

## Publishing

### Step 1: Commit Formula

```bash
cd homebrew-tap
git add Formula/audio-transcriber.rb
git commit -m "Add audio-transcriber formula"
git push origin main
```

### Step 2: Users Install

Users can now install via:

```bash
# Add tap
brew tap lucmuss/tap

# Install
brew install audio-transcriber

# Or one-liner
brew install lucmuss/tap/audio-transcriber
```

### Step 3: Update README

Add to `homebrew-tap/README.md`:

```markdown
# Homebrew Tap for audio-transcriber

## Installation

```bash
brew tap lucmuss/tap
brew install audio-transcriber
```

## Available Formulae

- **audio-transcriber** - Professional audio transcription tool
```

---

## Updating Formula

### When Releasing New Version

1. **Publish new version to PyPI** (see PYPI_PUBLISH.md)

2. **Get new SHA256:**
```bash
URL="https://files.pythonhosted.org/packages/source/a/audio-transcriber/audio-transcriber-1.0.1.tar.gz"
curl -L $URL | shasum -a 256
```

3. **Update formula:**
```ruby
class AudioTranscriber < Formula
  # ...
  url "https://files.pythonhosted.org/packages/source/a/audio-transcriber/audio-transcriber-1.0.1.tar.gz"
  sha256 "NEW_SHA256_HERE"
  # ...
end
```

4. **Update dependency versions if needed:**
```ruby
resource "openai" do
  url "https://files.pythonhosted.org/packages/source/o/openai/openai-1.35.0.tar.gz"
  sha256 "NEW_SHA256_HERE"
end
```

5. **Test locally:**
```bash
brew uninstall audio-transcriber
brew install --build-from-source Formula/audio-transcriber.rb
audio-transcriber --version  # Should show 1.0.1
```

6. **Commit and push:**
```bash
git add Formula/audio-transcriber.rb
git commit -m "Update audio-transcriber to 1.0.1"
git push
```

7. **Users update:**
```bash
brew update
brew upgrade audio-transcriber
```

---

## Submitting to Homebrew Core

### Prerequisites

- Project must be stable and maintained
- Package must work on macOS and Linux
- Good test coverage
- Clear documentation
- Active community

### Process

1. **Ensure formula quality:**
```bash
brew audit --strict --online Formula/audio-transcriber.rb
brew test Formula/audio-transcriber.rb
```

2. **Fork Homebrew/homebrew-core:**
```bash
cd $(brew --repository homebrew/core)
hub fork
```

3. **Create branch:**
```bash
git checkout -b audio-transcriber
```

4. **Add formula:**
```bash
cp /path/to/Formula/audio-transcriber.rb Formula/
```

5. **Test thoroughly:**
```bash
brew install --build-from-source Formula/audio-transcriber.rb
brew test Formula/audio-transcriber.rb
brew audit --strict Formula/audio-transcriber.rb
```

6. **Create PR:**
```bash
git add Formula/audio-transcriber.rb
git commit -m "audio-transcriber 1.0.0 (new formula)"
git push your-username audio-transcriber
hub pull-request
```

7. **Wait for review** (may take days/weeks)

---

## Troubleshooting

### Problem: SHA256 mismatch

**Error:**
```
SHA256 mismatch
Expected: abc123...
Actual: def456...
```

**Solution:**
```bash
# Recalculate SHA256
curl -L URL | shasum -a 256

# Update formula with correct hash
```

---

### Problem: Python dependency conflict

**Error:**
```
Requirement already satisfied
```

**Solution:**

Use `virtualenv_install_with_resources` which handles dependencies properly.

---

### Problem: FFmpeg not found during test

**Error:**
```
FileNotFoundError: ffmpeg not found
```

**Solution:**

Ensure formula includes:
```ruby
depends_on "ffmpeg"
```

---

### Problem: Test fails

**Error:**
```
audio-transcriber: failed
```

**Solution:**

Check test block:
```ruby
test do
  assert_match version.to_s, shell_output("#{bin}/audio-transcriber --version")
  
  # Can add more tests
  system bin/"audio-transcriber", "--help"
end
```

---

## Best Practices

### 1. Pin Python Version

```ruby
depends_on "python@3.11"  # Specific version
# Not: depends_on "python"  # Too generic
```

### 2. Include All Dependencies

List all Python dependencies as resources, not just direct ones.

### 3. Test Before Publishing

```bash
# Always test locally first
brew install --build-from-source Formula/audio-transcriber.rb
brew audit --strict Formula/audio-transcriber.rb
brew test Formula/audio-transcriber.rb
```

### 4. Keep Formula Updated

Update formula when:
- New version released
- Dependencies updated
- Security fixes

### 5. Provide Good Description

```ruby
desc "Clear, concise description under 80 characters"
homepage "https://github.com/user/repo"
```

---

## Automation

### Auto-update formula with GitHub Actions

Create `.github/workflows/update-homebrew.yml`:

```yaml
name: Update Homebrew Formula

on:
  release:
    types: [published]

jobs:
  update-formula:
    runs-on: ubuntu-latest
    steps:
      - name: Get release info
        id: release
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          echo "version=$VERSION" >> $GITHUB_OUTPUT
      
      - name: Update formula
        uses: dawidd6/action-homebrew-bump-formula@v3
        with:
          token: ${{ secrets.HOMEBREW_TAP_TOKEN }}
          formula: audio-transcriber
          tap: lucmuss/homebrew-tap
          tag: ${{ github.ref }}
```

---

## Resources

- **Homebrew Docs:** https://docs.brew.sh/
- **Formula Cookbook:** https://docs.brew.sh/Formula-Cookbook
- **Python Formula:** https://docs.brew.sh/Python-for-Formula-Authors
- **Contributing:** https://docs.brew.sh/How-To-Open-a-Homebrew-Pull-Request

---

## Quick Reference

```bash
# Create tap
git clone https://github.com/lucmuss/homebrew-tap.git

# Add formula
cp Formula/audio-transcriber.rb homebrew-tap/Formula/

# Test
brew install --build-from-source Formula/audio-transcriber.rb
brew audit --strict Formula/audio-transcriber.rb
brew test Formula/audio-transcriber.rb

# Publish
git add Formula/audio-transcriber.rb
git commit -m "Add/Update audio-transcriber"
git push

# Users install
brew tap lucmuss/tap
brew install audio-transcriber
```

---

**Happy Brewing! 🍺**
