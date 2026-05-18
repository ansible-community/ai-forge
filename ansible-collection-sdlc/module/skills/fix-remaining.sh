#!/bin/bash

# Fix long lines in issue-analyze
sed -i '' '500s/.*/GitHub MCP Advantage: Issues that would be scored MEDIUM with gh CLI (missing info in/' issue-analyze/SKILL.md
sed -i '' '501i\
description) may be scored HIGH with GitHub MCP if the missing information is found in comments, timeline, or linked PRs.
' issue-analyze/SKILL.md

# Fix long line in issue-fix
sed -i '' '23s/.*/- When you launch multiple agents for independent work, send them in a single message/' issue-fix/SKILL.md  
sed -i '' '24i\
with multiple tool uses so they run concurrently
' issue-fix/SKILL.md

# Fix issue-plan ordered list numbering and other issues
# Change steps 12 and 13 to 1 and 2
sed -i '' 's/^12\. \*\*Save plan\*\*/1. **Save plan**/' issue-plan/SKILL.md
sed -i '' 's/^13\. \*\*Report and confirm\*\*/2. **Report and confirm**/' issue-plan/SKILL.md

# Add blank line before **File:**  
sed -i '' '/^   \*\*File: plugins\/modules\/xyz.py\*\*$/{
i\

}' issue-plan/SKILL.md

# Fix emphasis heading to proper heading
sed -i '' 's/^   \*\*File: plugins\/modules\/xyz.py\*\*/#### File: plugins\/modules\/xyz.py/' issue-plan/SKILL.md

# Add blank lines around headings and lists in issue-plan
sed -i '' '/^### Minimal Changes$/a\

' issue-plan/SKILL.md

sed -i '' '/^### Self-Contained$/a\

' issue-plan/SKILL.md

sed -i '' '/^### Code Style Match$/a\

' issue-plan/SKILL.md

sed -i '' '/^### Test Coverage$/a\

' issue-plan/SKILL.md

# Fix table in issue-fix (split Flags & Options row)
sed -i '' '437s/| `--issue N` or URL | GitHub issue number or full URL (required) | `--type bug\\|feature\\|enhance` | Force specific approach (overrides auto-detect) |/| `--issue N` or URL | GitHub issue number or full URL (required) |/' issue-fix/SKILL.md
sed -i '' '438i\
| `--type bug\\|feature\\|enhance` | Force specific approach (overrides auto-detect) |
' issue-fix/SKILL.md

echo "Fixed remaining issues"
