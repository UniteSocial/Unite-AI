#!/bin/bash

# Security audit script for Python dependencies
# Usage: ./audit-dependencies.sh

set -e

echo "🔍 Running security audit for Python dependencies..."
echo ""

# Check if pip-audit is installed
if ! command -v pip-audit &> /dev/null; then
    echo "📦 Installing pip-audit..."
    pip install pip-audit
fi

# Run audit
echo "🔎 Scanning dependencies for known vulnerabilities..."
pip-audit --requirement requirements.txt --format=json

echo ""
echo "✅ Security audit complete!"
echo ""
echo "💡 To fix vulnerabilities, update affected packages in requirements.txt"

