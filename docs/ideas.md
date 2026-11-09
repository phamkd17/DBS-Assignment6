# Running list: things to add

Add anything here. Move items to "Done" when they're built.

## Suggested so far (not yet decided)
- [ ] **Read the "Design, Build, Ship Autumn 2026" calendar (read-only).** It's the Google Classroom calendar you're already subscribed to, and it likely has the real assignment deadlines and class time. That would replace my guessed class time (Tue 5:30–8:30).
- [ ] **Confirm the real class time.** Tue 5:30–8:30 is still Claude's guess from the 5:30 PM deadline. Fix it in the LifeHarness calendar and `context/weekly-rhythm.md`.
- [ ] **Hook also blocks reads of other calendars.** AGENTS.md *asks* Claude to read only LifeHarness; the hook would *enforce* it. Good "decides vs. enforces" demo point.
- [ ] **Permission deny rules as a second layer.** `permissions.deny` in `.claude/settings.json` (e.g. `Edit(data/**)`, the calendar write tools) on top of the hook. Two independent locks.
- [ ] **Hook protects itself.** Block edits to `.claude/hooks/` and `.claude/settings.json` so Claude can't turn the hook off. (Skipped for now so it can still be fixed during building; you'd edit it by hand after that.)
- [ ] **Fewer false blocks in the hook.** It blocked a git commit because the *message* mentioned "data/". It could ignore quoted text and here-docs, or allow `git commit -F <file>` explicitly.
- [ ] **Fetch weather overnight on a schedule** (macOS launchd, ~6:30 AM) so it's already fresh at check-in. The brief mentions "waiting when you wake up."
- [ ] **Live replan demo moment:** add an event on your phone mid-demo, say "I just added something, replan," and show the UI update.
- [ ] **Chicago events (Ticketmaster Discovery API, free key)** as a bonus third source, e.g. suggest something fun for Friday nights.
- [ ] **Live drive time in the Commute card on "good morning"** (requested). Needs a live source:
  - **TomTom free tier (recommended):** `scripts/fetch-traffic.sh` → `data/traffic.json` (hook-protected) → `commute` field in the plan → the card shows "47 min (usually 40) · leave by 7:10".
  - **Browser automation:** Claude opens Google Maps in Chrome and reads the ETA. No key, but slow (eats the 2–3 min check-in), fragile, and scraping Google Maps is against its terms.
- [ ] **First git commit** as a checkpoint before building the skill.

## Your ideas
-

## Done
- [x] Google Calendar connected (LifeHarness calendar, made-up events)
- [x] Live weather (Open-Meteo) → `data/weather.json`
- [x] AGENTS.md + context files
- [x] Morning check-in skill (`.claude/skills/morning-checkin/`)
- [x] UI: local page at http://localhost:4321 (`python3 ui/server.py`), shows proposed vs. saved plans
- [x] Suggestions link to the event in Google Calendar ("Edit … in Google Calendar ↗")
- [x] Hook: `.claude/hooks/protect-data.py`, on in `.claude/settings.json`; test with `./scripts/test-hook.sh`
- [x] Commute card: River North → Elk Grove Village, "Check live traffic ↗" opens Google Maps (no key)
- [x] "Good morning" opens the page (starts the server if it's not running)
- [x] Demo talking points (`docs/demo-talking-points.md`)
