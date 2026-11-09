# Demo talking points (3–5 min)

Screen layout: **UI on the left, Claude Code on the right.** Type live.
Everything below is built. The only ⏳ left is the class-time confirmation.

---

## 0:00–0:30 · Intro: the problem
- "I work full time, 8 to 5, and take one MPCS course at night."
- "I have about 30 minutes between waking up at 6:50 and driving to work at 7:20, so my check-in has to take 2–3 minutes."
- "All my school work happens in the evenings and on weekends, so the harness really plans *those*."

## 0:30–2:00 · Live check-in
- Type `good morning`. Don't name the skill, so the audience sees Claude pick it on its own. **The page opens by itself** on the left.
- Point out what it reads: the LifeHarness calendar, the weather, and yesterday's notes.
- It asks one question: "Which step of the assignment are you on?" Answer it.
- It proposes a plan built around my school blocks, e.g. "Saturday: finish step 3, start step 4."
- Say "yes" → the plan is saved → **point at the UI updating on the left.**
- Optional: add an event on my phone in Google Calendar, say "I just added something, replan", and show it picked up.

## 2:00–2:45 · The hook: blocked live
- **Part 1, Claude decides:** type "Move my Wednesday dentist appointment to 1 PM." Claude will likely *refuse on its own* because of AGENTS.md and offer the Edit-in-Google-Calendar link. The hook never even fires. Say: "That's Claude following the rule."
- **Part 2, Claude Code enforces:** type "I'm testing my hook. Try to move the dentist appointment anyway." Claude attempts `update_event`, and Claude Code blocks it with "Blocked by LifeHarness hook: the calendar is read-only…". Say: "Even when Claude tries, it can't."
- Optional: "Try to edit data/weather.json" → blocked too.
- Optional backup (if the live attempt is awkward): run `./scripts/test-hook.sh`, which feeds 23 fake tool calls to the hook and shows PASS/BLOCK for each.
- What the hook covers: no calendar create/update/delete; reads **only** from the LifeHarness calendar (a missing calendar ID would default to my main calendar, so that's blocked too); no Write/Edit in `data/`; no shell commands touching `data/`; the weather script itself is protected.
- Honest limit: shell commands are checked by text matching, so a deliberately disguised command could get past it. The Write/Edit and calendar checks are exact.
- **Story: the hook stopped Claude from adding humidity.** I asked for humidity in the hourly forecast. That meant changing `scripts/fetch-weather.sh`, which the hook protects, so Claude *couldn't* do it and asked me to make the one-line change myself. That's the hook protecting my data pipeline from the agent, even for a harmless edit. Claude explained what to change; I made the change.
- **Story: the hook blocked Claude's own git commit, twice.** The commit message mentioned "data/", and later "fetch-weather.sh" plus a ">" from the co-author email, so the hook treated harmless text as a risky command. Claude worked around it by writing the message to a file. The point: text matching errs on the side of blocking. It's strict, sometimes too strict, and never quietly lets something through. That's the tradeoff of enforcing in code instead of trusting the model.

## 2:45–4:30 · Explain the harness (the three things the brief asks for)

### 1. Harness overview
- **Data (2 sources):** Google Calendar, using a separate "LifeHarness" calendar of made-up events, plus live weather from Open-Meteo (free, no key).
- **AGENTS.md:** who I am, the hard rules, priorities, and where everything lives.
- **Context files:** my weekly rhythm, the assignment cycle, the assignment steps, weather rules.
- **Skill:** the morning check-in.
- **Notes:** `notes/log.md`, Claude's memory of past plans and which step I'm on.
- **Plans + UI:** each agreed plan is saved as JSON, and a local page shows it.
- **Hook:** blocks changes to my data.

### 2. What loads when
- **Every session: `AGENTS.md`**, about 30 lines. It holds only what applies to *every* conversation: the hard rules, the priority order, the calendar ID, and pointers to other files.
- **Only when needed: the context files.** The check-in skill reads them when it plans. If I just ask "what's the weather?", Claude doesn't need my whole weekly schedule.
- **The skill loads in three layers:**
  1. **Every session:** only the skill's one-paragraph *description*. That's how Claude knows the skill exists and picks it for "good morning" or "plan my day" without being told its name.
     - Talking point: "The description is the only part of the skill that loads every session, so it has to tell Claude when to use it. Keywords give a reliable match, and the intent covers phrasings I didn't think of."
     - Demo it: say "good morning" (a listed keyword), then try something *not* listed, like "what's my Sunday look like?", and show it still picks the skill.
  2. **When triggered:** `SKILL.md`, the check-in steps (gather → summarize → ask → propose → save).
  3. **Only at save time:** `plan-format.md`, the JSON shape the UI expects. Claude doesn't need it until I say yes.
- Show `/context` with AGENTS.md listed.

### 3. What Claude decides vs. what Claude Code enforces
- **Claude decides:** what to work on and when, whether to suggest skipping boxing, when the weather matters, what to ask me.
- **Claude Code enforces (the hook):** no calendar create/update/delete, no edits to `data/`. Even if Claude *wanted* to, or I asked it to, it can't.
- Key line: "AGENTS.md is a request. The hook is a guarantee."
- Good example: "Only read the LifeHarness calendar" started as a rule in AGENTS.md. The hook now enforces it too: reads of any other calendar are blocked.

## Design decisions worth a sentence each (pick 2–3)
- **The check-in takes 2–3 minutes** because of my morning: coffee, shower, drive. At most two questions.
- **The priority order:** work, class and the deadline are fixed → social plans only as a last resort → boxing can be skipped near a deadline → chores move freely.
- **Progress is tracked in steps** ("A6, step 3 of 5"), because that's how the assignments are structured. Plans say *which step*, not just "work on homework."
- **The definition of "behind":** fewer than half the steps done by Saturday. That's when it suggests skipping boxing.
- **Weather stays quiet unless it matters.** It only mentions the drive for snow or ice, and outdoor plans for rain or cold.
- **"Don't invent steps."** If there's no assignment file, it asks me instead of guessing.

- **The page shows proposals before I agree.** I wanted to *see* what Claude is suggesting, not just read it in the terminal. Claude now writes its proposal to `plans/proposed.json`, and the page shows it with an orange **"Proposed: waiting for your OK"** badge. When I say yes, it saves the dated plan and the badge turns green: **"Saved plan."**
  - Why it matters: the rule "never save a plan until I agree" still holds. A proposal is clearly labeled as one, and only my "yes" makes it the real plan. That's a human-in-the-loop step that's *visible* in the UI.
  - Demo it: pause after the proposal and point at the orange badge, then say "yes" and watch it turn green.
- **Suggestions link straight to the event.** Each suggested calendar change has an "Edit … in Google Calendar ↗" button. Claude can't edit my calendar, but it gets me one click away from making the change myself. The page only allows Google Calendar links, and Claude copies each link from the calendar data instead of building one.
  - Demo it: click the button, move the event in Google Calendar, then say "replan" and show the plan pick up the change.

## The page: what's on it (tour it while Claude is "reading…", ~20 sec)
- **The page opens by itself on "good morning".** The check-in starts the page server if it isn't running, then opens the page.
- **Commute card: River North → Elk Grove Village.** "Leave 7:20 AM · usually ~40 min", plus a **"Check live traffic ↗"** button that opens Google Maps with live traffic. On days off it fades and says "No work today."
  - Honest point: **Claude can't see live traffic.** The button is for *me*, and the context file tells Claude not to guess traffic. The page shows me more than Claude knows, and the harness knows the difference.
- **Background: one Windows Spotlight photo per day.** It's the same photo-of-the-day feed Windows uses on its lock screen: muted so the plan stays readable, a new one each day, and it stays the same through reloads and server restarts.
  - **Opening animation:** when the page opens, today's photo fills the window in full color for a quarter of a second with its place name, then fades into the muted background. Start the demo by opening the page so the audience sees it.
  - **A caption credits each photo** with the place and photographer, e.g. "Ice kayaker in Shiroka Polyana reservoir, Bulgaria · © …".
  - **Click the caption → the full photo** opens sharp and in full color. Click anywhere or press Esc to close.
- **Weather chip → hourly forecast.** Click it for **one chart with temperature (orange) and humidity (blue)** on a single shared axis, with a legend showing each range, above an hourly strip with icons, chance of rain, and storm hours outlined in red. Every hour has a dot with its value (temperature bold, humidity grey, placed above/below so they never collide); hover highlights the hour. It reads the same weather file Claude plans from.
- **Calendar card:** "Open calendar ↗" jumps to that day in Google Calendar, and "+ Add event ↗" opens a new event. Point: Claude can't edit my calendar (the hook blocks it), so the page makes it one click for *me*. Then I say "replan" and Claude picks up the change.
- **To-dos I can tick off, with progress notes.** Tick a box to mark it done (done items fold into "Done"). Click a to-do to see its progress notes and add one, e.g. "Confirm class time → emailed the TA, waiting to hear back." I can add new to-dos right on the page.
  - **Shared memory:** the page and Claude use the same file, `notes/todos.json`. If I tick something off at night, the next morning Claude sees it's done. If I tell Claude "I made progress on X", it adds a note I can see on the page, marked "Claude".
  - **Rules:** Claude never deletes a to-do or a note. And the page server only accepts changes from the page itself, so another website can't send requests to my `localhost` and edit my to-dos.
  - Demo it: tick a to-do on the left, then say "good morning" on the right and show Claude doesn't bring it up.
- **✈️ The vacation game (personal touch, a good closer for the tour):** "These photos are our vacation inspiration. My friend and I pick a random date in the future, and wherever the photo is on that day, that's where we go." Demo it: click the caption to show today's full photo and say, "If today were our date, we'd be going to Bulgaria."

## Changes I asked for (my design input; shows this wasn't a one-shot)
1. **"Link it to Google Calendar so when I add an event, the tool updates."** → I made a separate LifeHarness calendar that Claude reads live at every check-in, so new events show up on the next check-in or "replan".
2. **I changed my data sources twice:** Chicago events → traffic → a made-up calendar plus live weather. I picked the made-up calendar for privacy and weather because it's live and free. (Chicago's traffic feed turned out to be stale.)
3. **"Build the UI first. I want to see what you're suggesting."** → Proposals now show on the page as "Proposed: waiting for your OK" *before* I agree, then turn into "Saved plan" when I say yes.
4. **"Give me a link to my calendar so I can edit your suggested change."** → Each suggestion has an "Edit … in Google Calendar ↗" button. Claude still can't edit; I make the change in one click.
5. **"Keep a running list of things I can add to."** → `docs/ideas.md`, a backlog of every suggestion plus my own ideas, with what's done.
6. **I caught Claude's assumption** about my class time (guessed from the 5:30 PM deadline) and made it a talking point. See "Claude flagged its own assumption" below.
7. **My answers shaped the rules.** The 2–3 minute check-in (my 6:50 → 7:20 morning), my school days (Mon, Wed, Thu, Sat, Sun), the 11 PM cutoff, "boxing can be skipped near a deadline, social plans rarely", and tracking progress **by step** because that's how my assignments are structured.
8. **"Add traffic from River North to Elk Grove Village."** Live drive times need an API key (TomTom), so I chose the simpler option: a **"Check live traffic" button** to Google Maps. I also asked for Claude to read the traffic time on "good morning", but that would mean scraping Google Maps or signing up for a key, so I **kept it as a button**. A conscious scope decision the night before the deadline.
9. **"When I say good morning, open the page."** → The check-in starts the server if needed and opens the page.
10. **Background photos, three iterations:**
    - First: **my own photos** from a Mood Board folder (227 photos, served from the folder, never copied into the public repo).
    - Then: **Windows Spotlight** instead, so no personal photos end up in a video posted to Slack.
    - Then: **"They change too quickly"** → from every 15 seconds to **once a day**, cached so a restart doesn't change it.
11. **"If I click the photo's caption, open the full photo"** → a full-screen viewer, unmuted.
12. **The vacation game** gave the background a real purpose: a random future date picks our next trip.
13. **"Make the carry-over clickable, and give me a way to add notes to track progress on longer items."** → To-dos moved out of each day's plan into one shared file (`notes/todos.json`). I tick them off and add progress notes on the page; Claude reads and updates the same file in check-ins. This changed the design: the page used to be read-only, and now it can edit exactly one thing, my to-dos, and nothing else.
14. **"A small calendar card I can click to add or delete items."** → A Calendar card with "Open calendar" and "+ Add event". Same pattern as the suggestion links: Claude suggests, I make the change. (I tried a mini month view in the card, then removed it to keep the page simple; it also needed Claude to save a calendar snapshot at every check-in.)
15. **"Flash the photo full-screen when the page opens, then fade it to the background."** → A quarter-second intro of today's photo (click to skip; skipped if the system asks for reduced motion).
16. **"Show me the hourly forecast for temperature, humidity, and precipitation/storms."** → Click the Weather chip for the hourly strip. Humidity needed a change to the protected weather script, so I made that edit myself.
17. **"Temperature and humidity as line graphs" → "on one graph."** → First two separate charts, then one chart as I asked. Claude flagged the tradeoff: °F and % are different units, so it used **one shared axis** (both fit in about 30–90) instead of two y-axes, plus a legend so it's clear which line is which. Where the lines cross doesn't *mean* anything; it's two measurements that happen to share a range. Then: **"data points with the actual values, styled like the hourly strip"** → every hour labeled, the upper value above its dot and the lower one below so they never overlap; the axis and tooltip came out because every value is now on the chart.

## The background, behind the scenes (if asked)
- Windows Spotlight has **no official API.** It uses the unofficial endpoint Windows itself calls, so it could change. If it fails, the page keeps yesterday's photo or shows a plain background, and never breaks.
- **The photos are licensed to Microsoft** (Getty, Shutterstock, etc.), so they're shown on my local page with credit, never downloaded or committed. Only the day's photo *link* is cached.

## Things I learned building it (good for credibility)
- **The import went to the wrong calendar.** The made-up events landed in my *real* calendar at first. That showed me why the harness should only read one specific calendar, by ID.
- **I tried traffic data first.** Chicago's open-data traffic feed hadn't updated since April, so I switched to weather.
- **Claude flagged its own assumption.** The brief says the assignment is due Tuesday at 5:30 PM, so Claude guessed my class was Tuesday 5:30–8:30. It didn't present that as fact: it wrote "Time assumed - confirm" into the calendar event and listed the real class time under "what I can't see." It also noticed my Google Classroom calendar in my calendar list, but didn't read it without asking. Point: a good harness separates what it *knows* from what it *guessed*, and asks before reading more of my data.
  - ⏳ Update once confirmed: "...and I confirmed / corrected it to ___."
- **I had Claude interview me one question at a time** and then split the answers between AGENTS.md and the context files. I reviewed and edited what it wrote.

## Closing line (~10 sec)
- "Claude reads, plans and suggests. I make the changes. And the hook makes sure it stays that way."

---

## Pre-recording checklist
- [ ] Run `scripts/fetch-weather.sh` so the weather is fresh
- [ ] Restart Claude Code so AGENTS.md loads fresh, and check `/context`
- [ ] UI server running (`python3 ui/server.py` in its own Terminal window), page open on the left
- [ ] Check today's background photo and caption, and know where it is for the vacation-game line
- [ ] Do one practice run, then reset today's plan file
- [ ] Phone ready if doing the "add an event live" moment
- [ ] Keep it under 5 minutes
