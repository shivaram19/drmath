#!/bin/bash
# Configure git to use tracked hooks from .githooks/
# Run once after cloning: ./setup-hooks.sh

git config core.hooksPath .githooks
echo "✅ Git hooks configured from .githooks/"
echo "   Pre-commit will now validate:"
echo "   - .env is not staged"
echo "   - No runtime artifacts staged"
echo "   - No __pycache__ staged"
echo "   - Conventional commit format"
echo "   - ADR updates for pipeline/web changes"
