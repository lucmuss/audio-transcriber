# PyPI Publishing Guide 📦

Complete guide for publishing audio-transcriber to Python Package Index (PyPI).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Manual Publishing](#manual-publishing)
- [Automated Publishing](#automated-publishing)
- [Version Management](#version-management)
- [Testing on TestPyPI](#testing-on-testpypi)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### 1. PyPI Account

Create accounts on:
- **PyPI:** https://pypi.org/account/register/
- **TestPyPI:** https://test.pypi.org/account/register/

### 2. API Tokens

Generate API tokens for secure authentication:

**PyPI:**
1. Go to https://pypi.org/manage/account/
2. Scroll to "API tokens"
3. Click "Add API token"
4. Name: `audio-transcriber-upload`
5. Scope: "Entire account" or specific project
6. Copy the token (starts with `pypi-`)

**TestPyPI:**
1. Go to https://test.pypi.org/manage/account/
2. Follow same steps as above

### 3. Build Tools (uv)

```bash
uv run --with build --with twine python -m build
uv run --with twine twine check dist/*
```

---

## Manual Publishing

### Step 1: Update Version

Update version in **three places**:

**1. `src/audio_transcriber/__init__.py`:**
```python
__version__ = "1.0.1"
```

**2. `pyproject.toml`:**
```toml
[project]
version = "1.0.1"
```

**3. Create git tag:**
```bash
git tag -a v1.0.1 -m "Release version 1.0.1"
```

### Step 2: Clean Previous Builds

```bash
rm -rf build/ dist/ *.egg-info
```

### Step 3: Build Distribution

```bash
uv run --with build python -m build
```

This creates:
- `dist/audio-transcriber-1.0.1.tar.gz` (source distribution)
- `dist/audio_transcriber-1.0.1-py3-none-any.whl` (wheel distribution)

### Step 4: Check Distribution

```bash
uv run --with twine twine check dist/*
```

Should output: `PASSED` for all files.

### Step 5: Upload to TestPyPI (Optional)

```bash
uv run --with twine twine upload --repository testpypi dist/*
```

When prompted, use:
- Username: `__token__`
- Password: Your TestPyPI token

Verify at: https://test.pypi.org/project/audio-transcriber/

### Step 6: Upload to PyPI

```bash
uv run --with twine twine upload dist/*
```

When prompted, use:
- Username: `__token__`
- Password: Your PyPI token

### Step 7: Verify Publication

```bash
# Install from PyPI
uv tool install audio-transcriber

# Verify version
audio-transcriber --version
```

View on PyPI: https://pypi.org/project/audio-transcriber/

### Step 8: Push Git Tag

```bash
git push origin v1.0.1
```

---

## Automated Publishing

### Using GitHub Actions

The project includes `.github/workflows/publish-to-pypi.yml` for automated publishing.

### Setup

1. **Add PyPI Token to GitHub Secrets:**
   - Go to: `https://github.com/lucmuss/audio-transcriber/settings/secrets/actions`
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI token
   - Click "Add secret"

2. **Optional: Add TestPyPI Token:**
   - Name: `TEST_PYPI_API_TOKEN`
   - Value: Your TestPyPI token

### Trigger Automatic Publish

1. **Update version** in `__init__.py` and `pyproject.toml`

2. **Commit changes:**
```bash
git add src/audio_transcriber/__init__.py pyproject.toml
git commit -m "chore: bump version to 1.0.1"
git push
```

3. **Create and push tag:**
```bash
git tag -a v1.0.1 -m "Release version 1.0.1"
git push origin v1.0.1
```

4. **GitHub Actions will automatically:**
   - Build the package
   - Run tests
   - Publish to PyPI
   - Create GitHub Release

5. **Monitor progress:**
   - Go to: `https://github.com/lucmuss/audio-transcriber/actions`
   - Watch the "Publish to PyPI" workflow

---

## Version Management

### Semantic Versioning (SemVer)

Format: `MAJOR.MINOR.PATCH`

**Examples:**
- `1.0.0` → `1.0.1` - Bug fixes (patch)
- `1.0.1` → `1.1.0` - New features, backward-compatible (minor)
- `1.1.0` → `2.0.0` - Breaking changes (major)

### Version Update Checklist

- [ ] Update `src/audio_transcriber/__init__.py`
- [ ] Update `pyproject.toml`
- [ ] Update `CHANGELOG.md` (if exists)
- [ ] Run all tests: `uv run pytest`
- [ ] Build locally: `uv run --with build python -m build`
- [ ] Check build: `uv run --with twine twine check dist/*`
- [ ] Commit changes
- [ ] Create git tag: `git tag -a v1.0.1 -m "Release 1.0.1"`
- [ ] Push commits: `git push`
- [ ] Push tag: `git push origin v1.0.1`

---

## Testing on TestPyPI

### Why TestPyPI?

- Safe testing ground
- Verify package before production
- Check metadata and description

### Upload to TestPyPI

```bash
# Build
uv run --with build python -m build

# Upload
uv run --with twine twine upload --repository testpypi dist/*
```

### Install from TestPyPI

```bash
# Create test environment
uv venv

# Install from TestPyPI
uv pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    audio-transcriber

# Test
audio-transcriber --help
```

**Note:** `--extra-index-url` allows installing dependencies from regular PyPI.

---

## Troubleshooting

### Problem: Package name already exists

**Error:**
```
HTTPError: 403 Forbidden
The name 'audio-transcriber' is already in use
```

**Solution:**
- Package name is already taken
- Choose a different name in `pyproject.toml`
- Or claim the project if you own it

---

### Problem: Version already exists

**Error:**
```
HTTPError: 400 Bad Request
File already exists
```

**Solution:**
- Cannot re-upload same version
- Increment version number
- Delete old dist files: `rm -rf dist/`

---

### Problem: Authentication failed

**Error:**
```
HTTPError: 403 Forbidden
Invalid or non-existent authentication information
```

**Solutions:**

1. **Use `__token__` as username:**
```bash
uv run --with twine twine upload dist/* -u __token__ -p pypi-your-token-here
```

2. **Store credentials in `~/.pypirc`:**
```ini
[pypi]
username = __token__
password = pypi-your-actual-token

[testpypi]
username = __token__  
password = pypi-your-testpypi-token
```

Then upload without prompts:
```bash
uv run --with twine twine upload dist/*
```

---

### Problem: Wheel build fails

**Error:**
```
error: invalid command 'bdist_wheel'
```

**Solution:**
```bash
uv run --with build python -m build
```

---

### Problem: Long description rendering fails

**Error:**
```
The description failed to render for the following reason:
```

**Solutions:**

1. **Validate README locally:**
```bash
uv run --with readme-renderer python -c "import readme_renderer.rst; print(readme_renderer.rst.render(open('README.md').read()))"
```

2. **Check on TestPyPI first**

3. **Verify markdown syntax in README.md**

---

### Problem: Missing files in distribution

**Symptoms:** Package installs but files are missing

**Solutions:**

1. **Check `MANIFEST.in`:**
```
include README.md
include LICENSE
include requirements.txt
recursive-include src/audio_transcriber *.py
```

2. **Verify package contents:**
```bash
tar -tzf dist/audio-transcriber-1.0.0.tar.gz
```

3. **Ensure `pyproject.toml` includes all necessary files**

---

## Best Practices

### 1. Always Test Locally First

```bash
# Create clean environment
uv venv

# Install locally
uv sync --extra dev

# Run tests
uv run pytest
```

### 2. Use TestPyPI for Major Changes

Upload to TestPyPI before PyPI for:
- First release
- Major version changes
- Significant documentation changes

### 3. Automate with GitHub Actions

- Reduces human error
- Consistent process
- Automatic testing before publish

### 4. Keep Changelog

Create `CHANGELOG.md`:
```markdown
# Changelog

## [1.0.1] - 2024-01-20

### Added
- New feature X

### Fixed
- Bug Y

### Changed
- Improved Z
```

### 5. Version Pinning

In `pyproject.toml`, use version ranges:
```toml
dependencies = [
    "openai>=1.30.0,<2.0.0",
    "pydub>=0.25.1",
]
```

---

## Quick Reference

### Manual Publish

```bash
# 1. Update versions
# 2. Clean
rm -rf build/ dist/ *.egg-info

# 3. Build
uv run --with build python -m build

# 4. Check
uv run --with twine twine check dist/*

# 5. Upload
uv run --with twine twine upload dist/*

# 6. Tag
git tag -a v1.0.1 -m "Release 1.0.1"
git push origin v1.0.1
```

### Automated Publish

```bash
# 1. Update versions
# 2. Commit
git commit -am "chore: bump version to 1.0.1"
git push

# 3. Tag (triggers GitHub Actions)
git tag -a v1.0.1 -m "Release 1.0.1"
git push origin v1.0.1
```

---

## Resources

- **PyPI Help:** https://pypi.org/help/
- **Packaging Tutorial:** https://packaging.python.org/tutorials/packaging-projects/
- **Twine Docs:** https://twine.readthedocs.io/
- **Build Docs:** https://build.pypa.io/

---

**Happy Publishing! 🚀**
