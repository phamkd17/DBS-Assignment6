# Plan file format

Same shape for both files:
- `plans/proposed.json`: the proposal, before Khang agrees. The UI shows it with a "Proposed" badge.
- `plans/<YYYY-MM-DD>.json`: the agreed plan, for the date it covers. Overwrite on replan.

The UI shows `proposed.json` if it exists, otherwise the newest dated plan. The shape must match exactly.

```json
{
  "date": "2026-11-07",
  "weekday": "Saturday",
  "saved_at": "2026-11-07T07:05:00-06:00",
  "headline": "Big school day: finish step 3 and start step 4.",
  "weather": {
    "summary": "Sunny, 38→47°F",
    "alert": null
  },
  "assignment": {
    "name": "A6 LifeHarness",
    "due": "2026-11-10T17:30:00-06:00",
    "step": 3,
    "total_steps": 5,
    "status": "behind"
  },
  "timeline": [
    { "start": "09:00", "end": "10:15", "title": "Boxing", "kind": "exercise" },
    { "start": "12:00", "end": "16:30", "title": "A6: finish step 3, start step 4", "kind": "school" },
    { "start": "13:00", "end": "14:00", "title": "Grocery run", "kind": "chore", "note": "Suggest moving to Sunday" }
  ],
  "suggestions": [
    {
      "text": "Move the grocery run to Sunday morning.",
      "event_title": "Grocery run · Sat 1:00 PM",
      "event_link": "https://www.google.com/calendar/event?eid=..."
    }
  ],
  "carried_over": ["Email the TA about step 5"],
  "look_ahead": [
    { "day": "Sun", "plan": "Step 4" },
    { "day": "Mon", "plan": "Step 5 + submit" }
  ]
}
```

## Field rules
- `weather.alert`: a short string only when `weather-rules.md` says it matters (e.g. "Snow at 7 AM: leave by 7:05"), otherwise `null`.
- `assignment.status`: one of `"on track"`, `"behind"`, `"done"`.
- `timeline[].kind`: one of `"work"`, `"class"`, `"school"`, `"exercise"`, `"social"`, `"chore"`, `"free"`. Sort by `start`. Times are 24-hour `HH:MM`.
- `timeline[].note`: optional, short.
- `suggestions`: calendar changes for Khang to make. Empty array if none. Each one:
  - `text`: what to change and why, one sentence.
  - `event_title`: the event's name and current time, e.g. "Laundry · Mon 7:30 PM".
  - `event_link`: the event's `htmlLink`, copied exactly from the calendar results. Never build or guess a link. If the suggestion isn't about an existing event, leave it out.
- `carried_over`, `look_ahead`: empty arrays if none.
