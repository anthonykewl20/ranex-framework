#!/bin/bash
set -euo pipefail

# Script to fetch latest commit SHAs for GitHub Actions
# Run this to update SHAs in workflows

echo "Fetching latest commit SHAs for GitHub Actions..."
echo ""

# Official actions
echo "actions/checkout@v4:"
curl -s https://api.github.com/repos/actions/checkout/git/refs/tags/v4 | jq -r '.object.sha' || echo "Failed"

echo "actions/setup-python@v5:"
curl -s https://api.github.com/repos/actions/setup-python/git/refs/tags/v5 | jq -r '.object.sha' || echo "Failed"

echo "actions/cache@v4:"
curl -s https://api.github.com/repos/actions/cache/git/refs/tags/v4 | jq -r '.object.sha' || echo "Failed"

echo "actions/upload-artifact@v4:"
curl -s https://api.github.com/repos/actions/upload-artifact/git/refs/tags/v4 | jq -r '.object.sha' || echo "Failed"

# Third-party actions
echo "dtolnay/rust-toolchain@stable:"
curl -s https://api.github.com/repos/dtolnay/rust-toolchain/git/refs/heads/master | jq -r '.object.sha' || echo "Failed"

echo "trufflesecurity/trufflehog@main:"
curl -s https://api.github.com/repos/trufflesecurity/trufflehog/git/refs/heads/main | jq -r '.object.sha' || echo "Failed"

