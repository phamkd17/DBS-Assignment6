---
name: morning-checkin
description: Khang's daily check-in and day planner. Use whenever Khang greets you in the morning ("good morning", "morning", "gm"), asks to plan or replan the day ("plan my day", "what should I do today", "replan", "I added an event"), or asks what's on today or how much time is left for the assignment. Reads the LifeHarness calendar, weather, and notes; asks at most two questions; proposes a plan; saves it only after Khang agrees.
allowed-tools: Read, Bash(date *), Bash(./scripts/fetch-weather.sh), mcp__claude_ai_Google_Calendar__list_events
---

# Morning check-in

Khang has ~2–3 minutes (coffee, shower, then driving at 7:20). Be brief. No long reports, no headers in your replies, no tables unless asked.

## 1. Gather (do this silently, in parallel where possible)
- Run `date` to get today's date and weekday. Don't trust your own sense of the date.
- Read `notes/log.md` (the latest 3 entries are enough).
- Read `context/weekly-rhythm.md` and `context/assignment-cycle.md`.
- Read the current assignment file in `context/assignments/` (the one due next Tuesday).
- Weather: read `data/weather.json`. If `current.time` is more than ~3 hours old, run `./scripts/fetch-weather.sh` first. Read `context/weather-rules.md`.
- Calendar: list events on the LifeHarness calendar (ID in AGENTS.md) from today 00:00 through next Tuesday 17:30. Only that calendar.
- If `plans/<today>.json` already exists, this is a **replan**: read it and change only what's needed.

## 2. Summarize (3–5 short lines)
- Today's events in time order, one line.
- Weather: one line **only** if `weather-rules.md` says it matters (bad drive, outdoor plan at risk). Otherwise skip it.
- Assignment: "A6 due Tue 5:30 PM, N school blocks left". Say "behind" if the cycle rules say so.
- Carried-over to-dos from the last log entry, if any.

## 3. Ask (at most two questions, one at a time)
- **Always (unless no school block since the last check-in):** "Which step of A6 are you on?"
- **Only if needed:** one question about a real conflict, e.g. "You're behind. Skip Monday boxing, or move the Sunday walk?"
- Don't ask anything the calendar, notes, or context files already answer.

## 4. Propose the plan
- Today's timeline, including the school block with **specific steps** ("finish step 3, start step 4"), never "work on homework".
- Respect the 11 PM cutoff and the priorities in AGENTS.md.
- A one-line look-ahead to the deadline ("Sun: step 4 · Mon: step 5 + submit").
- Calendar changes are **suggestions for Khang to make**: "Suggest: move the walk to 1 PM (you'd change it in Google Calendar)." Never try to edit the calendar. Include the event's `htmlLink` from the calendar results so the page can show an "Edit in Google Calendar" button.
- Read `plan-format.md` (next to this file) and write the proposal to `plans/proposed.json`, so Khang can see it on the page (it shows as "Proposed: waiting for your OK").
- End with: "Save this plan?"

## 5. Save (only after Khang agrees)
- If Khang asks for changes, update `plans/proposed.json` and confirm again.
- On yes: write the same plan to `plans/<YYYY-MM-DD>.json` (the date the plan is *for*; when planning tomorrow at night, use tomorrow's date), with a fresh `saved_at`. Then delete `plans/proposed.json`.
- Add a new entry at the **top** of `notes/log.md` (below the header): date, one-line plan, assignment step, carried-over to-dos (keep unfinished ones, drop ones Khang says are done).
- Reply in one line: "Plan saved. Your page is updated."

## Never
- Create, update, or delete calendar events, or read any calendar other than LifeHarness.
- Edit anything in `data/`.
- Save a plan Khang hasn't agreed to.
- Invent assignment steps. If there's no file for the current assignment, ask Khang to add one.
