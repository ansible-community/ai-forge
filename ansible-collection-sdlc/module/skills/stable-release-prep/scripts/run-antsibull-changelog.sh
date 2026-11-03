#!/usr/bin/env bash
#
# Helper script to run antsibull-changelog with blocking IO
#
# Usage: run-antsibull-changelog.sh <args>
# Example: run-antsibull-changelog.sh release --version 12.0.0
#
# Why this exists:
# antsibull-changelog (via ansible-core) requires blocking IO on file descriptors,
# but some environments (like Claude Code's Bash tool) set them to non-blocking.
# This wrapper fixes that before invoking antsibull-changelog.

python3 -I - "$@" << 'PYTHON_EOF'
import sys
import os
import fcntl
import subprocess

# Set stdin, stdout, stderr to blocking mode
for fd in [sys.stdin, sys.stdout, sys.stderr]:
    flags = fcntl.fcntl(fd.fileno(), fcntl.F_GETFL)
    fcntl.fcntl(fd.fileno(), fcntl.F_SETFL, flags & ~os.O_NONBLOCK)

# Run antsibull-changelog with all arguments passed to this script
result = subprocess.run(
    ['antsibull-changelog'] + sys.argv[1:],
    cwd=os.getcwd(),
    capture_output=False,  # Let output go directly to terminal
    text=True
)
sys.exit(result.returncode)
PYTHON_EOF
