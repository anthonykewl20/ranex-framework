# Python Wheels

## Available Wheels

### ✅ Wheel File Created

**File:** `ranex_core-0.0.1-cp312-cp312-linux_x86_64.whl`

**Installation:**
```bash
pip install wheels/ranex_core-0.0.1-cp312-cp312-linux_x86_64.whl
```

**Verification:**
```bash
python3 -c "import ranex_core; print('✅ ranex_core installed')"
```

### Alternative: Manual Installation

If the wheel doesn't work, use the `.so` file:

```bash
# Find Python site-packages
python3 -c "import site; print(site.getsitepackages()[0])"

# Copy .so file
cp wheels/libranex_core.so $(python3 -c "import site; print(site.getsitepackages()[0])")/ranex_core.so
```

## Building Proper Wheels (When Network Available)

For production wheels, use maturin:

```bash
# Install maturin
pip install maturin
# Or: cargo install maturin

# Build wheels
maturin build --release

# Copy to Pre-Release-v0.1
cp target/wheels/ranex_core-0.0.1-*.whl Pre-Release-v0.1/wheels/
```

## Notes

- The wheel file includes the compiled `libranex_core.so`
- Compatible with Python 3.12+ on Linux x86_64
- For other platforms, rebuild with maturin
