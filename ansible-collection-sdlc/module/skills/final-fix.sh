#!/bin/bash

# Fix issue-analyze heading increment - change h4 to h3
sed -i '' 's/^#### Preferred: GitHub MCP$/### Preferred: GitHub MCP/' issue-analyze/SKILL.md
sed -i '' 's/^#### Fallback: gh CLI$/### Fallback: gh CLI/' issue-analyze/SKILL.md  
sed -i '' 's/^#### General$/### General/' issue-analyze/SKILL.md

# Fix issue-fix table - remove the incorrectly added row
sed -i '' '438d' issue-fix/SKILL.md

# Add blank line before table
sed -i '' '437i\

' issue-fix/SKILL.md

# Fix issue-plan multiple blank lines
sed -i '' '460{N;s/\n\n/\n/;}' issue-plan/SKILL.md

# Fix issue-plan code fences - add blank lines around numbered list items with code
# This is complex, let me do it differently - manually add blank lines

# Add blank line after "1. **Save plan**"
sed -i '' '/^1\. \*\*Save plan\*\*$/a\

' issue-plan/SKILL.md

# Add blank line before "2. **Report and confirm**" 
sed -i '' '/^    ```$/a\

' issue-plan/SKILL.md

# Add blank line after integration points
sed -i '' '/^- Can be used standalone for planning$/a\

' issue-plan/SKILL.md

# Add blank line before "### "No issue summary found""
sed -i '' '/^### "No issue summary found"$/i\

' issue-plan/SKILL.md

echo "Final fixes applied"
