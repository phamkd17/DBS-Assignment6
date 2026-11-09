#!/bin/bash
# Feed fake tool calls to the hook and show allow/block.
cd "$(dirname "$0")/.."
H=.claude/hooks/protect-data.py
P="$PWD"
LH=c_998de92f1d7cebef39d571a1a5dc76aabfd9d059a86b1283004bd1e9f4ea40a4@group.calendar.google.com
t() { # expected name json
  out=$(echo "$3" | CLAUDE_PROJECT_DIR="$P" python3 "$H" 2>&1); code=$?
  got=$([ $code -eq 0 ] && echo ALLOW || echo BLOCK)
  [ "$got" = "$1" ] && mark=PASS || mark=FAIL
  printf "%-4s %-5s %-50s %s\n" "$mark" "$got" "$2" "${out:0:70}"
}
t BLOCK "calendar: update_event (move the walk)" '{"tool_name":"mcp__claude_ai_Google_Calendar__update_event","tool_input":{"calendarId":"'$LH'","eventId":"x"}}'
t BLOCK "calendar: create_event"                 '{"tool_name":"mcp__claude_ai_Google_Calendar__create_event","tool_input":{}}'
t BLOCK "calendar: delete_event"                 '{"tool_name":"mcp__claude_ai_Google_Calendar__delete_event","tool_input":{}}'
t BLOCK "calendar: search_events (main cal)"     '{"tool_name":"mcp__claude_ai_Google_Calendar__search_events","tool_input":{"query":"x"}}'
t ALLOW "calendar: list_events LifeHarness"      '{"tool_name":"mcp__claude_ai_Google_Calendar__list_events","tool_input":{"calendarId":"'$LH'"}}'
t BLOCK "calendar: list_events main calendar"    '{"tool_name":"mcp__claude_ai_Google_Calendar__list_events","tool_input":{"calendarId":"phamkd@uchicago.edu"}}'
t BLOCK "calendar: list_events no calendarId"    '{"tool_name":"mcp__claude_ai_Google_Calendar__list_events","tool_input":{}}'
t ALLOW "calendar: list_calendars"               '{"tool_name":"mcp__claude_ai_Google_Calendar__list_calendars","tool_input":{}}'
t BLOCK "Write data/weather.json"                '{"tool_name":"Write","tool_input":{"file_path":"'$P'/data/weather.json","content":"{}"}}'
t BLOCK "Edit data/weather.json (relative)"      '{"tool_name":"Edit","tool_input":{"file_path":"data/weather.json"},"cwd":"'$P'"}'
t BLOCK "Edit data/../data/x (sneaky path)"      '{"tool_name":"Edit","tool_input":{"file_path":"'$P'/plans/../data/x.json"}}'
t BLOCK "Edit scripts/fetch-weather.sh"          '{"tool_name":"Edit","tool_input":{"file_path":"'$P'/scripts/fetch-weather.sh"}}'
t ALLOW "Write plans/2026-11-09.json"            '{"tool_name":"Write","tool_input":{"file_path":"'$P'/plans/2026-11-09.json"}}'
t ALLOW "Edit notes/log.md"                      '{"tool_name":"Edit","tool_input":{"file_path":"'$P'/notes/log.md"}}'
t BLOCK "Bash: rm data/weather.json"             '{"tool_name":"Bash","tool_input":{"command":"rm data/weather.json"}}'
t BLOCK "Bash: echo {} > data/weather.json"      '{"tool_name":"Bash","tool_input":{"command":"echo {} > data/weather.json"}}'
t BLOCK "Bash: cd data && rm *"                  '{"tool_name":"Bash","tool_input":{"command":"cd data && rm *"}}'
t BLOCK "Bash: sed -i on fetch script"           '{"tool_name":"Bash","tool_input":{"command":"sed -i s/a/b/ scripts/fetch-weather.sh"}}'
t ALLOW "Bash: ./scripts/fetch-weather.sh"       '{"tool_name":"Bash","tool_input":{"command":"./scripts/fetch-weather.sh"}}'
t ALLOW "Bash: date"                             '{"tool_name":"Bash","tool_input":{"command":"date"}}'
t ALLOW "Bash: ls metadata/ (not data/)"         '{"tool_name":"Bash","tool_input":{"command":"ls metadata/"}}'
t ALLOW "Read data/weather.json (not hooked)"    '{"tool_name":"Read","tool_input":{"file_path":"'$P'/data/weather.json"}}'
t BLOCK "garbage input"                          'not json'
