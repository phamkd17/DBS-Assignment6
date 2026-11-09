#!/usr/bin/env python3
"""LifeHarness PreToolUse hook: Claude can read the data, never change it.

Claude Code runs this before every matching tool call and passes the call as JSON on stdin.
  exit 0 -> allow
  exit 2 -> block; the stderr message is shown to Claude

Enforces:
  1. Google Calendar: no create/update/delete/respond. Reads only from the LifeHarness calendar.
  2. data/: no Write/Edit, no shell commands that touch it.
     (Weather is refreshed only by ./scripts/fetch-weather.sh, which is also protected.)
"""
import json
import os
import re
import sys
from pathlib import Path

LIFEHARNESS = "c_998de92f1d7cebef39d571a1a5dc76aabfd9d059a86b1283004bd1e9f4ea40a4@group.calendar.google.com"
CAL = "mcp__claude_ai_Google_Calendar__"
CAL_READS = {"list_events", "get_event"}  # must name the LifeHarness calendar
CAL_ALLOWED = {"list_calendars"}          # names only, no events

PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2]).resolve()
PROTECTED = [PROJECT / "data", PROJECT / "scripts" / "fetch-weather.sh"]

# A path segment named data/ (not "metadata/"), or "cd data"
DATA_IN_SHELL = re.compile(r"(?<![\w.-])data/|\bcd\s+['\"]?(\./)?data\b")
FETCH_SCRIPT_EDIT = re.compile(r"fetch-weather\.sh")
SHELL_WRITES = re.compile(r">|\b(rm|mv|cp|tee|sed\s+-i|perl\s+-i|truncate|chmod|ln|dd)\b")


def block(msg):
    print(f"Blocked by LifeHarness hook: {msg}", file=sys.stderr)
    sys.exit(2)


def is_protected(path_str, cwd):
    if not path_str:
        return False
    p = Path(path_str)
    if not p.is_absolute():
        p = Path(cwd or PROJECT) / p
    p = p.resolve()
    return any(p == prot or prot in p.parents for prot in PROTECTED)


def main():
    try:
        call = json.load(sys.stdin)
    except json.JSONDecodeError:
        block("could not read the tool call, so it was blocked to be safe.")
    tool = call.get("tool_name", "")
    args = call.get("tool_input") or {}
    cwd = call.get("cwd")

    # 1. Google Calendar
    if tool.startswith(CAL):
        action = tool[len(CAL):]
        if action in CAL_ALLOWED:
            sys.exit(0)
        if action in CAL_READS:
            if args.get("calendarId") == LIFEHARNESS:
                sys.exit(0)
            block("only the LifeHarness calendar may be read. Pass its calendarId from AGENTS.md "
                  "(leaving it out reads Khang's main calendar).")
        block(f"the calendar is read-only ({action} is not allowed). Don't retry. "
              "Suggest the change to Khang and include the event's htmlLink so Khang can make it.")

    # 2. File edits
    if tool in {"Write", "Edit", "MultiEdit", "NotebookEdit"}:
        path = args.get("file_path") or args.get("notebook_path")
        if is_protected(path, cwd):
            block(f"{path} is protected data and can't be changed. "
                  "Weather is refreshed only by running ./scripts/fetch-weather.sh.")
        sys.exit(0)

    # 3. Shell commands
    if tool == "Bash":
        cmd = args.get("command", "")
        if DATA_IN_SHELL.search(cmd) or str(PROJECT / "data") in cmd:
            block("shell commands can't touch data/. Use the Read tool to read data files; "
                  "refresh weather only with ./scripts/fetch-weather.sh.")
        if FETCH_SCRIPT_EDIT.search(cmd) and SHELL_WRITES.search(cmd):
            block("scripts/fetch-weather.sh is protected and can't be changed.")
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
