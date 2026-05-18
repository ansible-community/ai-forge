#!/bin/bash

# Fix emphasis used as headings (MD036) - change **text:** to proper headings
for file in issue-*/SKILL.md; do
  sed -i '' 's/^\*\*Preferred: GitHub MCP\*\*/#### Preferred: GitHub MCP/' "$file"
  sed -i '' 's/^\*\*Fallback: gh CLI\*\*/#### Fallback: gh CLI/' "$file"
  sed -i '' 's/^\*\*General\*\*/#### General/' "$file"
  sed -i '' 's/^\*\*Step /#### Step /' "$file"
  sed -i '' 's/^\*\*CRITICAL: /#### CRITICAL: /' "$file"
  sed -i '' 's/^\*\*Example: /#### Example: /' "$file"
  sed -i '' 's/^\*\*Critical: /#### Critical: /' "$file"
  sed -i '' 's/^\*\*Implementation is complete/#### Implementation is complete/' "$file"
  sed -i '' 's/^\*\*File: /#### File: /' "$file"
done

# Fix table formatting (MD060) - ensure spaces around pipes
for file in issue-*/SKILL.md; do
  # Fix compact table formatting
  sed -i '' 's/|\([^ ]\)/ | \1/g' "$file"
  sed -i '' 's/\([^ ]\)|/\1 |/g' "$file"
done

echo "Fixed markdown issues"
