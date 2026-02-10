#!/usr/bin/env python3
"""
PreToolUse hook to block ALL access to .env files.

Prevents bypass methods like:
- Direct read: Read(.env)
- Bash read: cat .env, head .env, grep .env
- Copy bypass: cp .env /tmp/x && cat /tmp/x
- Archive bypass: tar/zip .env
- Search content: Grep in .env files

Exit codes:
- 0: Allow operation
- 2: Block operation (security policy violation)
"""

import sys
import json
import re

# Patterns that indicate .env files (for file paths)
ENV_FILE_PATTERNS = [
    r'\.env$',           # ends with .env
    r'\.env\.',          # .env.local, .env.production, etc.
    r'/\.env$',          # path/.env
    r'/\.env\.',         # path/.env.local
    r'^\.env$',          # just .env
    r'^\.env\.',         # .env.something at start
]

# Patterns for detecting .env in bash commands (as tokens/arguments)
ENV_COMMAND_PATTERNS = [
    r'\s\.env(\s|$)',    # .env as argument (space before, space/end after)
    r'\s\.env\.',        # .env.local etc as argument
    r'^\.env(\s|$)',     # .env at start of command
    r'^\.env\.',         # .env.local at start
    r'/\.env(\s|$)',     # path/.env as argument
    r'/\.env\.',         # path/.env.local as argument
    r'"[^"]*\.env[^"]*"', # .env inside double quotes
    r"'[^']*\.env[^']*'", # .env inside single quotes
]

# Bash commands that read file contents
READ_COMMANDS = [
    'cat', 'head', 'tail', 'less', 'more', 'bat', 'view',
    'grep', 'egrep', 'fgrep', 'rg', 'ag', 'ack',
    'awk', 'sed', 'perl', 'ruby', 'python',
    'sort', 'uniq', 'wc', 'nl', 'od', 'xxd', 'hexdump',
    'strings', 'file', 'diff', 'comm', 'cut', 'paste',
    'xargs', 'source', '.', 'eval',
]

# Bash commands that copy/move files (enables later reading)
COPY_COMMANDS = [
    'cp', 'mv', 'rsync', 'scp', 'install',
    'ln',  # symlinks
    'dd',
]

# Bash commands that archive files
ARCHIVE_COMMANDS = [
    'tar', 'zip', 'gzip', 'bzip2', 'xz', 'zstd',
    '7z', '7za', 'rar', 'unrar',
]

# Combined dangerous commands
DANGEROUS_COMMANDS = READ_COMMANDS + COPY_COMMANDS + ARCHIVE_COMMANDS


def matches_env_pattern(path_str: str) -> bool:
    """Check if path matches any .env file pattern."""
    if not path_str:
        return False
    for pattern in ENV_FILE_PATTERNS:
        if re.search(pattern, path_str, re.IGNORECASE):
            return True
    return False


def command_references_env(command: str) -> bool:
    """Check if a bash command references .env files."""
    if not command:
        return False
    # Check command-specific patterns
    for pattern in ENV_COMMAND_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    # Also check file path patterns
    return matches_env_pattern(command)


def check_bash_command(command: str) -> tuple[bool, str]:
    """
    Check if bash command attempts to access .env files.
    Returns (is_blocked, reason).
    """
    if not command:
        return False, ""

    # Check if .env appears anywhere in the command
    if not command_references_env(command):
        return False, ""

    # Command references .env - now check if it's a dangerous operation
    command_lower = command.lower().strip()

    # Check for dangerous commands
    for cmd in DANGEROUS_COMMANDS:
        # Match command at start or after pipe/semicolon/&&/||
        patterns = [
            rf'^{cmd}\s',           # command at start
            rf'^{cmd}$',            # just the command
            rf'\|\s*{cmd}\s',       # after pipe
            rf'\|\s*{cmd}$',        # after pipe at end
            rf';\s*{cmd}\s',        # after semicolon
            rf'&&\s*{cmd}\s',       # after &&
            rf'\|\|\s*{cmd}\s',     # after ||
            rf'\$\({cmd}\s',        # in subshell
            rf'`{cmd}\s',           # in backticks
        ]
        for pattern in patterns:
            if re.search(pattern, command_lower):
                return True, f"Command '{cmd}' with .env file is blocked"

    # Also block direct execution of .env (source, .)
    if re.search(r'(^|\s)(source|\.)\s+.*\.env', command_lower):
        return True, "Sourcing .env files is blocked"

    # Block echo/printf that might read .env via subshell
    if re.search(r'(echo|printf).*\$\(.*\.env', command_lower):
        return True, "Reading .env via subshell is blocked"

    return False, ""


def check_file_path(file_path: str, tool_name: str) -> tuple[bool, str]:
    """Check if file path is a .env file."""
    if matches_env_pattern(file_path):
        return True, f"{tool_name} access to .env files is blocked"
    return False, ""


def check_grep_tool(tool_input: dict) -> tuple[bool, str]:
    """Check if Grep tool targets .env files."""
    # Check path parameter
    path = tool_input.get('path', '')
    if matches_env_pattern(path):
        return True, "Grep in .env files is blocked"

    # Check glob parameter
    glob_pattern = tool_input.get('glob', '')
    if matches_env_pattern(glob_pattern):
        return True, "Grep with .env glob pattern is blocked"

    return False, ""


def main():
    try:
        data = json.load(sys.stdin)
        tool_name = data.get('tool_name', '')
        tool_input = data.get('tool_input') or {}

        is_blocked = False
        reason = ""

        # Check based on tool type
        if tool_name == 'Bash':
            command = tool_input.get('command', '')
            is_blocked, reason = check_bash_command(command)

        elif tool_name == 'Read':
            file_path = tool_input.get('file_path', '')
            is_blocked, reason = check_file_path(file_path, 'Read')

        elif tool_name == 'Edit':
            file_path = tool_input.get('file_path', '')
            is_blocked, reason = check_file_path(file_path, 'Edit')

        elif tool_name == 'Write':
            file_path = tool_input.get('file_path', '')
            is_blocked, reason = check_file_path(file_path, 'Write')

        elif tool_name == 'Grep':
            is_blocked, reason = check_grep_tool(tool_input)

        if is_blocked:
            error_msg = f"""
╔══════════════════════════════════════════════════════════════╗
║  SECURITY POLICY VIOLATION: .env Access Blocked              ║
╠══════════════════════════════════════════════════════════════╣
║  Tool: {tool_name:<54} ║
║  Reason: {reason:<52} ║
╠══════════════════════════════════════════════════════════════╣
║  .env files contain secrets and are protected.               ║
║  This includes all bypass attempts (cp, cat, grep, etc.)     ║
╚══════════════════════════════════════════════════════════════╝
"""
            print(error_msg, file=sys.stderr)
            sys.exit(2)  # Block operation

    except json.JSONDecodeError:
        # If we can't parse input, allow (fail open for usability)
        pass
    except Exception:
        pass

    sys.exit(0)  # Allow operation


if __name__ == "__main__":
    main()
