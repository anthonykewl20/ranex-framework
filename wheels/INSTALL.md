# Installing Ranex Core

## Option 1: Install from Wheel (Recommended)

**Note:** Wheels need to be built with maturin. If wheels are not available, use Option 2.

```bash
pip install wheels/ranex_core-0.0.1-*.whl
```

## Option 2: Manual Installation (If wheels not available)

If wheels are not built, you can manually install the compiled module:

```bash
# Copy the .so file to Python's site-packages
python3 -c "import site; print(site.getsitepackages()[0])"
# Copy libranex_core.so to that directory
cp wheels/libranex_core.so $(python3 -c "import site; print(site.getsitepackages()[0])")/ranex_core.so
```

## Option 3: Build Wheels Yourself

If you have maturin installed:

```bash
# Install maturin
pip install maturin

# Build wheels
cd Pre-Release-v0.1
maturin build --release

# Install the built wheel
pip install target/wheels/ranex_core-0.0.1-*.whl
```

## Verification

After installation:

```bash
python3 -c "import ranex_core; print('✅ ranex_core installed')"
python3 -c "import ranex; print('✅ ranex package installed')"
ranex --help
```

