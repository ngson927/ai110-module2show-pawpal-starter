# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps a pet owner plan daily care tasks for one or more pets. It generates a priority-sorted, time-bounded schedule, detects conflicts, and automatically reschedules recurring tasks.

## 📸 Demo

<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank"><img src='/course_images/ai110/pawpal_screenshot1.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>
<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank"><img src='/course_images/ai110/pawpal_screenshot2.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

## Features

### Multi-pet task management
- Add any number of pets (dogs, cats, or other species) to a single owner profile
- Assign tasks independently to each pet — feeding, walking, medication, grooming, or custom categories
- Each task stores a title, duration, priority (1–5), category, start time, frequency, and due date

### Priority-based schedule generation
- `generate_plan()` selects only pending, today-relevant tasks and sorts them by priority (highest first), breaking ties by shortest duration
- Tasks are added greedily until the owner's available time is filled
- Tasks that don't fit are collected in a `skipped` list and shown in the UI with their duration and priority

### Chronological sorting
- `sort_by_time()` orders any task list by `start_time` (HH:MM) using tuple comparison on `(hour, minute)`, so the schedule always reads as a timeline rather than a priority dump
- Applied automatically to both the task table and each pet's block in the generated schedule

### Flexible filtering
- `filter_tasks(pet_name, completed)` queries tasks by pet, by completion status, or both combined
- Underlying helpers `get_tasks_by_pet()` and `get_tasks_by_status()` available for single-criteria lookups

### Daily and weekly recurrence
- `complete_and_reschedule()` marks a task done and automatically clones it for the next occurrence
- `daily` tasks get `due_date + 1 day` using Python's `timedelta`
- `weekly` tasks get `due_date + 7 days`
- `as needed` tasks complete without spawning a follow-up

### Conflict detection
- `detect_conflicts()` scans every unique pair of tasks using `itertools.combinations` and flags two problem types:
  - **Duplicate title** — same task name assigned more than once to the same pet
  - **Time overlap** — two tasks whose start/end windows intersect, meaning the owner cannot perform both simultaneously
- Returns human-readable warning strings; never raises an exception
- Displayed in the UI before the plan so the owner can resolve conflicts before scheduling

### Streamlit UI
- Task table sorted by start time on every page load
- Schedule grouped by pet, each block sorted chronologically
- Conflict warnings shown with `st.error` / `st.warning` before the plan renders
- Skipped tasks in a collapsible expander
- Three summary metrics: scheduled task count, total time used, time remaining

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

## Agent Mode

The following features were implemented using Claude Code in agent mode:

- **Challenge 1 — `find_next_slot(duration)`**: Added to `Scheduler` in `scheduler.py`. Walks the day from 06:00 in 5-minute increments and returns the first `HH:MM` slot where `duration` minutes fit without overlapping any task already in `daily_plan`. Returns `None` if nothing fits before 22:00.
- **Challenge 2 — JSON persistence**: Added `to_dict()`, `save_to_json()`, and `load_from_json()` to the `Owner` class in `pawpal_system.py`. `app.py` now loads from `data.json` on startup (if it exists) and saves after every "Add pet", "Add task", and "Generate schedule" action.
- **Challenge 3 — Priority emoji labels**: A `priority_label(priority)` helper in `app.py` maps the 1–5 integer to "🔴 High", "🟡 Medium", or "🟢 Low". Used in both the task table and the schedule display.
- **Challenge 4 — Category emoji labels**: A `category_emoji(category)` helper in `app.py` maps category strings to labeled emoji strings (e.g. "🦮 Walking", "💊 Medication"). Used alongside `priority_label` in both table views.
- **Challenge 5 — Prompt comparison**: A new section in `reflection.md` documents a side-by-side test of GPT-4o vs. Claude Sonnet on the recurring-task rescheduling prompt, with analysis of output quality and integration fit.

## Testing PawPal+

### Run the tests

```bash
python3.11 -m pytest tests/test_pawpal.py -v
```

### What the tests cover

The test suite in `tests/test_pawpal.py` contains 14 tests across five groups:

| Group | Tests | What's verified |
|---|---|---|
| **Core behavior** | 2 | `mark_complete()` flips status; adding a task increases pet task count |
| **Sorting** | 2 | Tasks returned in chronological order; correct tie-breaking within the same hour |
| **Recurrence** | 4 | Daily tasks roll forward +1 day; weekly tasks roll forward +7 days; `as needed` tasks produce no clone; invalid task ID returns `None` safely |
| **Conflict detection** | 3 | Overlapping time windows flagged; exact same start time flagged; clean schedule returns no conflicts |
| **Edge cases** | 3 | Pet with no tasks returns empty plan; total scheduled time never exceeds `available_time`; unknown pet name returns empty list |

### Confidence level

★★★★☆ (4 / 5)

The core scheduling behaviors — priority sorting, time-bounding, recurrence, and conflict detection — are all covered and passing. Confidence is high for the happy paths and the most likely edge cases. One star is withheld because the tests use in-memory data only (no persistence layer), and the Streamlit UI interactions in `app.py` are not yet tested automatically.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
