---
name: issue-analyze
description: Fetch and analyze any GitHub issue (bug/feature/enhancement). Extracts issue details, detects type, validates actionability, and prepares for implementation. Use when starting work on an issue, or when asked to "analyze issue", "check issue #123", or "pull issue".
triggers:
  - "analyze issue"
  - "check issue"
  - "pull issue"
  - "fetch issue"
---

# Issue Analyze Skill

Fetch a GitHub issue and analyze whether it's actionable (bug, feature, or enhancement).

## Author

**Alina Buzachis (alinabuzachis)** - Ansible Cloud Content Team

## Purpose

Retrieves a GitHub issue, validates it's actionable, extracts key information, and determines if it's ready for implementation. First step in the bug-fix workflow.

## When to Use This Skill

- Starting bug fix work
- Analyzing whether an issue is fixable
- Extracting issue details before planning
- Validating bug reports
- Part of automated bug-fix workflows

## Prerequisites

**Preferred (GitHub MCP):**

- GitHub MCP server configured (see `GITHUB_MCP_SETUP.md`)
- Provides richer issue data (comments, timeline, linked PRs)

**Fallback (gh CLI):**

- `gh` CLI installed and authenticated
- Used when GitHub MCP is not available

**Auto-detection:** Skill will use MCP if available, otherwise fallback to gh CLI.

## Usage Examples

```bash
# Analyze issue with full GitHub URL (recommended - copy/paste from browser)
/issue-analyze https://github.com/ansible-collections/amazon.aws/issues/2755

# Or with just issue number (detects repo from current directory)
/issue-analyze --issue 2755

# Analyze issue from specific repo
/issue-analyze --issue 456 --repo ansible-collections/amazon.aws

# Force gh CLI (skip MCP)
/issue-analyze https://github.com/owner/repo/issues/123 --use-cli

# Just show issue info (no validation)
/issue-analyze https://github.com/owner/repo/issues/123 --info-only
```

**Tip:** Using full URLs is recommended - just copy/paste from your browser!

## Expected Behavior

When this skill is invoked:

1. **Detect GitHub access method**

   ```python
   # Check if GitHub MCP is available
   try:
       # Try to use GitHub MCP tool
       use_mcp = True
   except ToolNotAvailable:
       # Fall back to gh CLI
       use_mcp = False
       
   if use_mcp:
       echo "✓ Using GitHub MCP (richer data)"
   else:
       echo "ℹ Using gh CLI (fallback)"
   ```

2. **Parse issue URL or number**

   ```bash
   # Check if full GitHub URL was provided
   if [[ "$INPUT" =~ ^https://github.com/([^/]+)/([^/]+)/issues/([0-9]+) ]]; then
       # Parse URL
       OWNER="${BASH_REMATCH[1]}"
       REPO_NAME="${BASH_REMATCH[2]}"
       ISSUE_NUMBER="${BASH_REMATCH[3]}"
       echo "Parsed URL: https://github.com/$OWNER/$REPO_NAME/issues/$ISSUE_NUMBER"
   elif [[ "$INPUT" =~ ^[0-9]+$ ]]; then
       # Just issue number - detect repo from current directory
       ISSUE_NUMBER="$INPUT"
       REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
       OWNER=$(echo $REPO | cut -d'/' -f1)
       REPO_NAME=$(echo $REPO | cut -d'/' -f2)
       echo "Detected repo: $OWNER/$REPO_NAME"
   elif [[ -n "$REPO_FLAG" ]]; then
       # Issue number with --repo flag
       ISSUE_NUMBER="$INPUT"
       OWNER=$(echo $REPO_FLAG | cut -d'/' -f1)
       REPO_NAME=$(echo $REPO_FLAG | cut -d'/' -f2)
   else
       echo "Error: Please provide GitHub URL or issue number"
       echo "Examples:"
       echo "  /issue-analyze https://github.com/owner/repo/issues/123"
       echo "  /issue-analyze --issue 123"
       exit 1
   fi
   
   echo "Repository: $OWNER/$REPO_NAME"
   echo "Issue: #$ISSUE_NUMBER"
   ```

3. **Fetch issue details** (batch in ONE message)

   **Method A: GitHub MCP (Preferred)**

   ```python
   # Use GitHub MCP to get rich issue data
   issue = github_get_issue(
       owner=OWNER,
       repo=REPO_NAME,
       number=ISSUE_NUMBER
   )
   
   # Returns structured data:
   # - issue.title
   # - issue.body
   # - issue.labels[]
   # - issue.comments[] (full comment thread)
   # - issue.timeline[] (events, cross-references)
   # - issue.linked_pull_requests[] (related PRs)
   # - issue.state
   # - issue.author
   # - issue.created_at
   # - issue.updated_at
   ```

   **Method B: gh CLI (Fallback)**

   ```bash
   # Get all issue data in one gh call
   gh issue view $ISSUE_NUMBER \
     --repo $OWNER/$REPO_NAME \
     --json number,title,body,state,labels,author,comments,createdAt,updatedAt
   
   # Note: gh CLI provides less data (no timeline, no linked PRs)
   ```

   **Why GitHub MCP is better:**
   - ✅ Includes comments (can find reproduction steps in discussion)
   - ✅ Includes timeline events (references, cross-links)
   - ✅ Includes linked PRs (see if already being worked on)
   - ✅ Structured data (no JSON parsing needed)
   - ✅ Better error handling

4. **Parse and extract key information**

   **Method A: GitHub MCP (Preferred)**

   ```python
   # MCP returns structured data - no JSON parsing needed
   title = issue.title
   description = issue.body
   labels = [label.name for label in issue.labels]
   state = issue.state  # 'OPEN' or 'CLOSED'
   author = issue.author.login
   comments = issue.comments  # Full comment thread
   created_at = issue.created_at
   updated_at = issue.updated_at
   
   # MCP-exclusive data:
   timeline = issue.timeline  # Events, references, cross-links
   linked_prs = issue.linked_pull_requests  # Related PRs
   ```

   **Method B: gh CLI (Fallback)**

   ```python
   # Parse JSON from gh output
   import json
   issue_json = json.loads(gh_output)
   
   title = issue_json['title']
   description = issue_json['body']
   labels = [l['name'] for l in issue_json['labels']]
   state = issue_json['state']
   author = issue_json['author']['login']
   comments = issue_json.get('comments', [])
   created_at = issue_json['createdAt']
   updated_at = issue_json['updatedAt']
   
   # Note: No timeline or linked PRs available
   ```

   **Key information to extract:**
   - **Title**: Issue summary
   - **Description**: Full bug report
   - **Labels**: bug, enhancement, question, etc.
   - **State**: open/closed
   - **Author**: Who reported it
   - **Comments**: Additional context, stack traces, workarounds
   - **Timeline** (MCP only): Event history, references
   - **Linked PRs** (MCP only): See if already being worked on
   - **Created**: When reported
   - **Updated**: Last activity

5. **Validate if issue is actionable**

   **Check 1: Is it labeled as a bug?**

   ```python
   labels = issue['labels']
   is_bug = any(label['name'].lower() in ['bug', 'defect', 'error'] for label in labels)
   
   if not is_bug:
       print("⚠️  Issue not labeled as 'bug'")
       print("Labels:", [l['name'] for l in labels])
       print("Proceed anyway? [y/N]")
   ```

   **Check 2: Is it open?**

   ```python
   if issue['state'] != 'OPEN':
       print(f"ℹ️  Issue is {issue['state']}")
       print("Still proceed? [y/N]")
   ```

   **Check 3: Has enough information?**

   ```python
   # Check if description has key sections
   required_info = {
       'steps_to_reproduce': ['steps', 'reproduce', 'how to'],
       'expected_behavior': ['expected', 'should'],
       'actual_behavior': ['actual', 'instead', 'error'],
       'environment': ['version', 'python', 'ansible']
   }
   
   missing = []
   for section, keywords in required_info.items():
       if not any(kw in issue['body'].lower() for kw in keywords):
           missing.append(section)
   
   # GitHub MCP advantage: Check comments for missing info
   if use_mcp and missing and issue.comments:
       for comment in issue.comments:
           for section, keywords in required_info.items():
               if section in missing:
                   if any(kw in comment.body.lower() for kw in keywords):
                       missing.remove(section)
                       print(f"✅ Found {section} in comment by {comment.author.login}")
   
   if missing:
       print(f"⚠️  Missing information: {', '.join(missing)}")
       print("Continue anyway? [y/N]")
   ```

   **Check 4: Has error messages/stack traces?**

   ```python
   # Check issue body
   has_traceback = 'Traceback' in issue['body'] or '```' in issue['body']
   has_error = 'error' in issue['body'].lower() or 'exception' in issue['body'].lower()
   
   # GitHub MCP advantage: Also check comments for stack traces
   if use_mcp and not (has_traceback or has_error) and issue.comments:
       for comment in issue.comments:
           if 'Traceback' in comment.body or '```' in comment.body:
               has_traceback = True
               print(f"✅ Found stack trace in comment by {comment.author.login}")
               break
           if 'error' in comment.body.lower() or 'exception' in comment.body.lower():
               has_error = True
               print(f"✅ Found error info in comment by {comment.author.login}")
               break
   
   if not (has_traceback or has_error):
       print("⚠️  No error messages or stack traces found")
       print("May be hard to reproduce. Continue? [y/N]")
   ```

6. **Extract affected components**

   Identify what files/modules are likely affected:

   ```python
   import re
   
   file_patterns = [
       r'`([a-zA-Z0-9_/]+\.py)`',  # Backticked paths
       r'plugins/([a-zA-Z0-9_/]+\.py)',  # Plugin paths
       r'modules/([a-zA-Z0-9_/]+\.py)',  # Module paths
   ]
   
   affected_files = []
   
   # Search issue body
   for pattern in file_patterns:
       matches = re.findall(pattern, issue.body)
       affected_files.extend(matches)
   
   # GitHub MCP advantage: Structured access to comments
   if use_mcp and issue.comments:
       for comment in issue.comments:
           for pattern in file_patterns:
               matches = re.findall(pattern, comment.body)
               if matches:
                   affected_files.extend(matches)
                   print(f"Found file references in comment by {comment.author.login}")
   
   # GitHub MCP exclusive: Check timeline for code references
   if use_mcp and issue.timeline:
       for event in issue.timeline:
           if event.type == 'cross-referenced':
               print(f"Cross-referenced in {event.source.type} {event.source.number}")
   
   # GitHub MCP exclusive: Check linked PRs for related work
   if use_mcp and issue.linked_pull_requests:
       for pr in issue.linked_pull_requests:
           print(f"Related PR: #{pr.number} - {pr.title} ({pr.state})")
   
   print(f"Potentially affected files: {affected_files}")
   ```

7. **Categorize bug type**

   ```python
   bug_categories = {
       'crash': ['crash', 'segfault', 'fatal', 'core dump'],
       'logic_error': ['wrong result', 'incorrect', 'unexpected output'],
       'performance': ['slow', 'timeout', 'performance', 'hangs'],
       'api_break': ['breaking', 'api change', 'incompatible'],
       'docs': ['documentation', 'readme', 'typo'],
   }
   
   detected_types = []
   
   # Build text corpus from issue
   if use_mcp:
       # MCP: Use structured properties
       text = (issue.title + ' ' + issue.body).lower()
       # Also search comments
       if issue.comments:
           text += ' ' + ' '.join(c.body.lower() for c in issue.comments)
   else:
       # gh CLI: Parse JSON
       text = (issue['title'] + ' ' + issue['body']).lower()
       if issue.get('comments'):
           text += ' ' + ' '.join(c['body'].lower() for c in issue['comments'])
   
   for bug_type, keywords in bug_categories.items():
       if any(kw in text for kw in keywords):
           detected_types.append(bug_type)
   
   print(f"Bug type: {detected_types or ['unknown']}")
   ```

8. **Generate issue summary**

   Create structured summary for planning stage:

   ```markdown
   # Issue #123: [Title]
   
   **Status**: OPEN
   **Labels**: bug, high-priority
   **Reporter**: @username
   **Created**: 2026-03-15
   **Last Updated**: 2026-03-20
   
   ## Summary
   [Extract 2-3 sentence summary from description]
   
   ## Bug Type
   - Logic error
   - Affects: plugins/modules/my_module.py
   
   ## Steps to Reproduce
   1. [Extracted from issue]
   2. [...]
   
   ## Expected Behavior
   [What should happen]
   
   ## Actual Behavior
   [What actually happens]
   
   ## Error Messages
   ```

   [Stack trace or error output]

   ```
   
   ## Environment
   - Python: 3.9
   - Ansible: 2.15
   - Collection: amazon.aws 5.0.0
   
   ## Related Work (GitHub MCP only)
   **Linked PRs**:
   - #456: Fix for similar issue (MERGED)
   - #789: Attempted fix (CLOSED)
   
   **Timeline Events**:
   - Referenced in PR #456 (2026-03-18)
   - Mentioned in issue #234 (2026-03-19)
   
   **Discussion Highlights** (from comments):
   - @contributor: Provided additional stack trace
   - @maintainer: Confirmed affected version range
   
   ## Validation
   ✅ Labeled as bug
   ✅ Issue is open
   ✅ Has reproduction steps
   ✅ Has error messages
   ⚠️  Missing: environment details (found in comments)
   
   ## Actionability: HIGH
   This issue is ready for implementation.
   
   ## Next Steps
   1. Run /bug-plan to create implementation plan
   2. Verify reproduction in local environment
   3. Implement fix in affected files
   ```

   **Note**: When using GitHub MCP, the summary will include richer context from comments, linked PRs, and timeline events. With gh CLI fallback, it will include only the basic issue information.

9. **Save summary to file**

   ```bash
   mkdir -p .bug-fixes
   cat > .bug-fixes/issue-$ISSUE_NUMBER.md <<EOF
   [Generated summary]
   EOF
   
   echo "✅ Issue summary saved: .bug-fixes/issue-$ISSUE_NUMBER.md"
   ```

10. **Report validation result**

    ```
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Issue Analysis: #123
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    Title: Module xyz fails with KeyError on missing parameter
    Status: OPEN
    Labels: bug, high-priority
    
    Validation:
      ✅ Labeled as bug
      ✅ Issue is open
      ✅ Has reproduction steps
      ✅ Has error messages
      ⚠️  Missing environment details
    
    Bug Type: logic_error
    Affected: plugins/modules/xyz.py
    
    Actionability: HIGH ✅
    
    Next steps:
      1. Review: cat .bug-fixes/issue-123.md
      2. Plan: /bug-plan
      3. Or full workflow: /bug-fix --issue 123
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ```

## Actionability Scoring

**HIGH** (ready to fix):

- ✅ Labeled as bug
- ✅ Open issue
- ✅ Has reproduction steps
- ✅ Has error messages or stack trace
- ✅ Affected files identified

**MEDIUM** (needs clarification):

- ✅ Labeled as bug
- ✅ Open issue
- ⚠️  Missing some details (repro steps OR error messages)

**LOW** (not ready):

- ❌ Not labeled as bug
- ❌ Closed issue
- ❌ Vague description
- ❌ No reproduction steps
- ❌ No error information

GitHub MCP Advantage: Issues that would be scored MEDIUM with gh CLI (missing info in
description) may be scored HIGH with GitHub MCP if the missing information is found in comments, timeline, or linked PRs.

## Integration Points

This skill is imported by:

- `/bug-fix` - Bug fix orchestrator
- Can be used standalone for issue analysis

## Troubleshooting

### GitHub MCP Not Available

If GitHub MCP tools are not available, the skill will automatically fall back to gh CLI.

To set up GitHub MCP for richer data:

```bash
# See GITHUB_MCP_SETUP.md for complete instructions
npm install -g @modelcontextprotocol/server-github

# Add to ~/.claude/config.json:
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here"
      }
    }
  }
}

# Restart Claude Code
```

### "gh CLI not found"

If using fallback mode without MCP:

```bash
brew install gh
gh auth login
```

### "Issue not found"

```bash
# With GitHub MCP:
# Tool will return clear error message

# With gh CLI:
gh issue view 123 --repo owner/repo
```

### "Missing information"

Ask reporter for more details:

```bash
# With GitHub MCP:
# Use github_add_issue_comment tool

# With gh CLI:
gh issue comment 123 --body "Could you provide reproduction steps?"
```

## Implementation Notes

### Preferred: GitHub MCP

- Use `github_get_issue()` for structured data (no JSON parsing)
- Access comments, timeline, and linked PRs automatically
- Better error handling and authentication
- Richer context for actionability analysis

### Fallback: gh CLI

- Use `gh issue view --json` to get all data in one call (batch operation)
- Parse JSON to extract structured information
- Limited to basic issue data (no timeline or linked PRs)

### General

- Auto-detect available GitHub access method
- Validate completeness before proceeding (check comments if needed)
- Save summary for use by issue-plan and issue-implement
- Provide clear actionability assessment
- Handle edge cases (closed issues, feature requests, etc.)
- Works with any GitHub repository
- Graceful fallback ensures skill works with or without MCP
