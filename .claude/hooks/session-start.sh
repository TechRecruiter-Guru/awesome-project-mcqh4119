#!/bin/bash
# Session Start Hook for Claude Code
# This runs automatically when a Claude session begins in this repo

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
CLAUDE_DIR="$REPO_ROOT/.claude"

echo "=================================="
echo "  John Polhill III - Claude Session"
echo "=================================="
echo ""

# Check for CLAUDE.md
if [ -f "$REPO_ROOT/CLAUDE.md" ]; then
    echo "Context loaded: CLAUDE.md"
else
    echo "WARNING: CLAUDE.md not found!"
fi

# Show quick stats
if [ -d "$REPO_ROOT/.resumes" ]; then
    RESUME_COUNT=$(find "$REPO_ROOT/.resumes" -name "*.html" 2>/dev/null | wc -l)
    echo "Resumes on file: $RESUME_COUNT"
fi

# Show last session date
if [ -f "$CLAUDE_DIR/SESSION-TRACKING.md" ]; then
    LAST_SESSION=$(grep -o '[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}' "$CLAUDE_DIR/SESSION-TRACKING.md" | tail -1)
    if [ -n "$LAST_SESSION" ]; then
        echo "Last tracked session: $LAST_SESSION"
    fi
fi

# Application tracker status
if [ -f "$REPO_ROOT/.resumes/APPLICATION-TRACKER.md" ]; then
    ACTIVE_APPS=$(grep -c "^|.*| Active |" "$REPO_ROOT/.resumes/APPLICATION-TRACKER.md" 2>/dev/null || echo "0")
    echo "Active applications: $ACTIVE_APPS"
fi

echo ""
echo "Ready. Say 'audit this session' when done."
echo "=================================="
