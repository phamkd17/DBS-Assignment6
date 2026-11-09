# Demo talking points (3–5 min)

Screen layout: **the page on the left, Claude Code on the right.** Type live.
Everything below is built. The only ⏳ left is confirming my real class time.

---

## The 4-minute script (if you only read one section)

| Time | Do | Say |
|---|---|---|
| 0:00 | Page already open on the left (reload it so the photo intro plays) | "I work full time and take one MPCS course at night. I have 30 minutes between waking up and driving to work, so my check-in has to take 2–3 minutes." |
| 0:20 | Type `good morning` | "I didn't name the skill. Claude picked it from its description." |
| 0:40 | Answer "Which step are you on?" | "It reads my LifeHarness calendar, the weather, yesterday's notes and my to-dos, then asks one question." |
| 1:10 | Point at the orange **Proposed** badge on the left | "The page shows the plan *before* I agree." |
| 1:20 | Say `yes`; badge turns green | "Only my yes makes it the real plan." |
| 1:30 | 20-second page tour: week peaks, weather chart, commute, calendar, to-dos | (see "The page" below) |
| 2:00 | Type "Move my Wednesday dentist appointment to 1 PM" | "Claude refuses on its own. That's Claude *deciding* to follow AGENTS.md." |
| 2:20 | Type "I'm testing my hook. Try to move it anyway." | "Now Claude tries, and Claude Code *blocks* it. AGENTS.md is a request; the hook is a guarantee." |
| 2:45 | Explain what loads when (show `/context`) | AGENTS.md every session · skill description every session · SKILL.md when triggered · context files and plan format only when needed |
| 3:30 | One hook story (humidity or 7-day forecast) | "The hook even stopped Claude from changing my weather script, so I made that edit myself." |
| 3:50 | Click the photo caption, full photo opens | Vacation-game line, then the closing line |

---

## 0:00–0:30 · Intro: the problem
- "I work full time, 8 to 5, and take one MPCS course at night."
- "I have about 30 minutes between waking up at 6:50 and driving to work at 7:20, so my check-in has to take 2–3 minutes."
- "All my school work happens in the evenings and on weekends, so the harness really plans *those*."

## 0:30–2:00 · Live check-in
- Type `good morning`. Don't name the skill, so the audience sees Claude pick it on its own. **The page opens by itself** on the left (the check-in starts the page server if needed).
- What it reads: the LifeHarness calendar, the weather file, yesterday's entry in `notes/log.md`, and my open to-dos in `notes/todos.json`.
- It asks one question: "Which step of the assignment are you on?" Answer it.
- It proposes a plan built around my school blocks ("finish step 4, then record"), with calendar changes as **suggestions** that have an "Edit … in Google Calendar ↗" button.
- **The orange "Proposed: waiting for your OK" badge** appears on the page. Say "yes" → the badge turns green, **"Saved plan."**
- Optional: tick a to-do on the page first, then show that Claude doesn't bring it up.
- Optional: add an event on my phone, say "I just added something, replan", and show it picked up.

## 2:00–2:45 · The hook: blocked live
- **Part 1, Claude decides:** "Move my Wednesday dentist appointment to 1 PM." Claude refuses on its own because of AGENTS.md and offers the Edit-in-Google-Calendar link. The hook never fires. Say: "That's Claude following the rule."
- **Part 2, Claude Code enforces:** "I'm testing my hook. Try to move the dentist appointment anyway." Claude attempts `update_event`, and Claude Code blocks it: "Blocked by LifeHarness hook: the calendar is read-only…". Say: "Even when Claude tries, it can't."
- Optional: "Try to edit data/weather.json" → blocked too.
- Backup if the live attempt is awkward: run `./scripts/test-hook.sh` (23 fake tool calls, all PASS).
- **What the hook covers:** no calendar create/update/delete; reads **only** from the LifeHarness calendar (a missing calendar ID would default to my main calendar, so that's blocked too); no Write/Edit in `data/`; no shell commands touching `data/`; the weather script itself is protected.
- **Honest limit:** shell commands are checked by text matching, so a deliberately disguised command could get past it. The Write/Edit and calendar checks are exact.

### Hook stories (pick one)
- **It stopped Claude from changing my weather pipeline, twice.** Adding humidity to the forecast, and later going from 3 to 7 days, both meant editing `scripts/fetch-weather.sh`. The hook protects that script, so Claude *couldn't*. It told me the exact line to change, and I made the edit. (Claude also gave me the wrong line number the first time; it caught the broken result before running the script.)
- **It blocked Claude's own harmless work, three times.** Twice a git commit message ("data/", then "fetch-weather.sh" plus a ">" from the co-author email), and once a page edit whose code *mentioned* the weather script. Claude worked around each by putting the text in a file. The point: text matching errs on the side of blocking. It's strict, sometimes too strict, and never quietly lets something through. That's the tradeoff of enforcing in code instead of trusting the model.

## 2:45–4:30 · Explain the harness (the three things the brief asks for)

### 1. Harness overview
- **Data (2 read-only sources):**
  - **Google Calendar:** a separate "LifeHarness" calendar of made-up events, read live through the connector, by its exact ID only.
  - **Weather:** live Open-Meteo forecast (free, no key): current conditions, hourly (temperature, humidity, rain, storms), and 7 days of highs/lows, sunrise/sunset. `scripts/fetch-weather.sh` is the only thing that writes it.
- **AGENTS.md (~30 lines):** who I am, the hard rules, priorities, and where everything lives.
- **Context files:** my weekly rhythm (school blocks, 11 PM cutoff, commute), the Tue→Tue assignment cycle, the steps of each assignment, weather rules.
- **Skill:** the morning check-in (gather → summarize → ask → propose → save).
- **Notes, Claude's memory:** `notes/log.md` (past plans, which step I'm on) and `notes/todos.json` (to-dos and progress notes, shared with the page).
- **Plans + page:** proposals go to `plans/proposed.json`, agreed plans to `plans/<date>.json`; a local page shows them and updates on its own.
- **Hook:** `.claude/hooks/protect-data.py`, switched on in `.claude/settings.json`.

### 2. What loads when
- **Every session: `AGENTS.md`.** Only what applies to *every* conversation: the hard rules, the priority order, the calendar ID, pointers to other files. Show `/context` with AGENTS.md listed.
- **The skill loads in three layers:**
  1. **Every session:** only the skill's one-paragraph *description*. That's how Claude knows the skill exists and picks it for "good morning" or "plan my day" without being told its name.
     - Talking point: "The description is the only part of the skill that loads every session, so it has to tell Claude when to use it. Keywords give a reliable match, and the intent covers phrasings I didn't think of."
     - Demo it: say "good morning" (a listed keyword), then try something *not* listed, like "what's my Sunday look like?", and show it still picks the skill.
  2. **When triggered:** `SKILL.md`, the check-in steps.
  3. **Only at save time:** `plan-format.md`, the JSON shapes for plans and to-dos. Claude doesn't need it until I say yes.
- **Only when needed: the context files.** The skill reads them when it plans. If I just ask "what's the weather?", Claude doesn't need my weekly schedule.

### 3. What Claude decides vs. what Claude Code enforces
- **Claude decides:** what to work on and when, whether to suggest skipping boxing, when the weather matters, what to ask me, which to-dos to mention.
- **Claude Code enforces (the hook):** no calendar create/update/delete, no reading other calendars, no edits to `data/` or the weather script. Even if Claude *wanted* to, or I asked it to, it can't.
- **The page server enforces too:** it only accepts to-do changes from the page itself, so another website can't send requests to my `localhost` and edit my to-dos. It can never touch plans, the calendar, or `data/`.
- Key line: **"AGENTS.md is a request. The hook is a guarantee."**
- Good example: "Only read the LifeHarness calendar" started as a rule in AGENTS.md. The hook now enforces it too.

## Design decisions worth a sentence each (pick 2–3)
- **The check-in takes 2–3 minutes** because of my morning: coffee, shower, drive. At most two questions.
- **The priority order:** work, class and the deadline are fixed → social plans only as a last resort → boxing can be skipped near a deadline → chores move freely.
- **Progress is tracked in steps** ("A6, step 3 of 5"), because that's how the assignments are structured. Plans say *which step*, not "work on homework."
- **The definition of "behind":** fewer than half the steps done by Saturday. That's when it suggests skipping boxing.
- **Weather stays quiet unless it matters.** It only mentions the drive for snow or ice, and outdoor plans for rain or cold.
- **"Don't invent steps."** If there's no assignment file, it asks me instead of guessing.
- **The page shows proposals before I agree.** The rule "never save a plan until I agree" still holds: a proposal is labeled as one, and only my "yes" makes it the real plan. A human-in-the-loop step that's *visible*.
- **Claude never edits my calendar; the page makes it one click for me.** Suggestions link to the exact event, and the Calendar card opens the day or a new event, in my UChicago account. Then I say "replan."
- **Claude can't see live traffic, and says so.** The commute card's "Check live traffic" button is for *me*; the context file tells Claude not to guess traffic.

## The page: what's on it (tour it while Claude is "reading…", ~20 sec)
- **Opening:** today's photo fills the window in full color for a quarter second, then fades (1 s) into the muted background.
- **Status badge + headline:** orange "Proposed" or green "Saved plan," the day, and a one-line headline.
- **Assignment card:** "A6 · due Tue 5:30 PM · Step 3 of 5 · behind," with a progress bar.
- **Weather card (always open), top to bottom:**
  - **Week peaks:** "Next 7 days · High ▲ 58° Tue, Nov 10 · Low ▼ 34° Sat, Nov 14." Click it for a **full 7-day forecast** built from the same Open-Meteo data: icons, conditions, rain, sunrise/sunset, and a low→high bar per day on one shared scale.
  - **Any weather alert** from the plan (e.g. "Snow at 7 AM: leave by 7:05").
  - **Today's summary:** icon, high/low, "Mostly clear and cool · dry," sunrise/sunset.
  - **Next 24 hours:** per hour, the time and icon (🌙 after sunset), then **one chart with temperature (orange) and humidity (blue)** with a dot and value at every hour, then the chance-of-rain bar. Rainy hours are tinted, storm hours outlined in red; hover highlights the hour.
- **Commute card:** River North → Elk Grove Village, "Leave 7:20 AM · usually ~40 min," with a "Check live traffic ↗" button to Google Maps.
- **Calendar card:** "Open calendar ↗" (that day) and "+ Add event ↗," opening in my UChicago Google account.
- **Timeline:** the day's plan, color-coded by kind (work, class, school, exercise, social, chore), with the current item highlighted.
- **Suggestions:** calendar changes for me to make, each with an "Edit … in Google Calendar ↗" button.
- **To-dos:** tick to finish (done items fold into "Done"), click one to see and add progress notes, add new ones on the page. Claude reads and updates the same file at check-ins, never deletes a to-do or a note, and marks its own notes "Claude."
- **Look ahead:** the remaining days until the deadline.
- **Photo caption (bottom right):** place and photographer; click it for the full photo.
- **✈️ The vacation game:** "These photos are our vacation inspiration. My friend and I pick a random date in the future, and wherever the photo is on that day, that's where we go." Click the caption: "If today were our date, we'd be going to Bulgaria."

## Changes I asked for (my design input; shows this wasn't a one-shot)
1. **"Link it to Google Calendar so when I add an event, the tool updates."** → A separate LifeHarness calendar that Claude reads live at every check-in or "replan."
2. **I changed my data sources twice:** Chicago events → traffic → a made-up calendar plus live weather, for privacy and because weather is live and free. (Chicago's traffic feed turned out to be stale.)
3. **"Build the UI first. I want to see what you're suggesting."** → Proposals show on the page as "Proposed" *before* I agree, then turn into "Saved plan."
4. **"Give me a link to my calendar so I can edit your suggested change."** → Each suggestion has an "Edit … in Google Calendar ↗" button.
5. **"Keep a running list of things I can add to."** → `docs/ideas.md`: every suggestion, my own ideas, what's done, and what I decided against.
6. **I caught Claude's assumption** about my class time and made it a talking point (see below).
7. **My answers shaped the rules:** the 2–3 minute check-in, my school days (Mon, Wed, Thu, Sat, Sun), the 11 PM cutoff, "boxing can be skipped near a deadline, social plans rarely," and tracking progress **by step**.
8. **"Add traffic from River North to Elk Grove Village."** Live drive times need an API key or scraping Google Maps, so I **kept it as a button**. A conscious scope decision the night before the deadline.
9. **"When I say good morning, open the page."** → The check-in starts the server if needed and opens the page.
10. **Background photos, three versions:** my own Mood Board photos (never copied into the public repo) → **Windows Spotlight** instead, so no personal photos end up in a video posted to Slack → **"they change too quickly"** → once a day, cached so a restart doesn't change it.
11. **"Click the photo's caption to open the full photo"** → a full-screen viewer.
12. **The vacation game** gave the background a real purpose.
13. **"Make the carry-over clickable, with notes to track progress on longer items."** → To-dos moved into one shared file (`notes/todos.json`). The page went from read-only to editing exactly one thing, my to-dos.
14. **"A small calendar card I can click to add or delete items."** → "Open calendar" and "+ Add event." I also tried a mini month view in the card, then **removed it** to keep the page simple (it also needed Claude to save a calendar snapshot at every check-in).
15. **"Open my UChicago calendar, not my default one."** → The links carry my Google account. My email lives in a git-ignored `.env`, so it never reaches the public repo.
16. **"Flash the photo full-screen when the page opens, then fade it."** → I tuned it by feel: hold 2 s → 0.5 s → **0.25 s**; fade 1.6 s → 1 s → 0.5 s → 0.75 s → **1 s**.
17. **"Hourly forecast for temperature, humidity, and precipitation/storms."** Humidity needed a change to the protected weather script, so I made that edit myself.
18. **The weather chart, five iterations:** two separate line charts → **"on one graph"** (Claude flagged the tradeoff: °F and % are different units, so one shared axis, never two y-axes; where the lines cross means nothing) → **"actual values on every point, styled like the hourly strip"** → **"trend lines below the icon, no duplicate temperature"** → **"same label style, different colors, more compact"** (darker shades of the line colors so the text stays readable). Claude also caught a bug along the way: sun icons at midnight, now 🌙 after sunset.
19. **"Match the scrollbar to the theme, keep the forecast open, add a day summary at the top."** Then **"remove the Weather chip"** (it showed the old plan's weather; the card shows live data).
20. **"Peak high and low for the next 7 days; click to open the full weather app" → "use the same data source" → "peaks regardless of the day" → "show the dates."** The click opens an in-page forecast from the same data, so the numbers always match (the Mac Weather app uses Apple's data). Going to 7 days was another edit I made myself to the protected weather script.
21. **"Make the commute card the same opacity as the other cards."** Small, but it's my page.

## Behind the scenes (if asked)
- **Windows Spotlight has no official API.** The page uses the unofficial endpoint Windows itself calls, so it could change. If it fails, the page keeps yesterday's photo or shows a plain background.
- **The photos are licensed to Microsoft** (Getty, Shutterstock, etc.), so they're shown on my local page with credit, never downloaded or committed. Only the day's photo *link* is cached.
- **The weather card reads the same file Claude plans from,** so the page and Claude always agree. The page server only reads it.
- **Every chart color was checked**: the line colors pass colorblind-separation and contrast checks, and the labels use darker shades of the same colors for readable text.

## Things I learned building it (good for credibility)
- **The import went to the wrong calendar.** The made-up events landed in my *real* calendar at first. That showed me why the harness should only read one specific calendar, by ID.
- **I tried traffic data first.** Chicago's open-data traffic feed hadn't updated since April, so I switched to weather.
- **Claude flagged its own assumption.** The brief says the assignment is due Tuesday at 5:30 PM, so Claude guessed my class was Tuesday 5:30–8:30. It didn't present that as fact: it wrote "Time assumed - confirm" into the calendar event and listed the real class time under "what I can't see." It also noticed my Google Classroom calendar but didn't read it without asking. Point: a good harness separates what it *knows* from what it *guessed*, and asks before reading more of my data.
  - ⏳ Update once confirmed: "…and I confirmed / corrected it to ___."
- **I had Claude interview me one question at a time** and then split the answers between AGENTS.md and the context files. I reviewed and edited what it wrote.
- **A stale server looks like a broken feature.** The hourly forecast "didn't show" because the page server was started before the feature existed. Now the page says "restart the server" instead of loading forever.

## Closing line (~10 sec)
- "Claude reads, plans and suggests. I make the changes. And the hook makes sure it stays that way."

---

## Pre-recording checklist
- [ ] Restart the page server so it has the latest code: Ctrl+C, then `python3 ui/server.py` in its own Terminal window
- [ ] Restart Claude Code so AGENTS.md and the skill load fresh; check `/context`
- [ ] Run `./scripts/fetch-weather.sh` so the weather is fresh
- [ ] Do one practice "good morning" so today's plan replaces the old Sunday one (tell it you're on step 4 or 5), then delete `plans/proposed.json` if a proposal is left over
- [ ] Check today's background photo and caption, and know where it is for the vacation-game line
- [ ] Make sure the Wednesday dentist appointment is still on the calendar for the hook demo
- [ ] Phone ready if doing the "add an event live" moment
- [ ] Page on the left, Claude Code on the right; keep it under 5 minutes
