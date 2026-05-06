#!/bin/bash
# Configure git to use tracked hooks from .githooks/
# Run once after cloning: ./setup-hooks.sh

git config core.hooksPath .githooks
echo "✅ Git hooks configured from .githooks/"
echo ""
echo "   pre-commit validates:"
echo "   - .env is not staged"
echo "   - No runtime artifacts staged"
echo "   - No __pycache__ staged"
echo "   - ADR updates for pipeline/web changes"
echo ""
echo "   commit-msg validates:"
echo "   - Conventional commit format (feat:|fix:|docs:|test:|refactor:|chore:|research:)"
echo "   - Merge, revert, fixup, squash commits are exempt"
