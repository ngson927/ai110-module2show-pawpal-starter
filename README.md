# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The `Scheduler` class (in `scheduler.py`) goes beyond a simple task list with four algorithmic features:

- **Sort by time** — `sort_by_time()` orders any task list chronologically using each task's `start_time` (HH:MM), converting it to a `(hour, minute)` tuple for accurate comparison.
- **Flexible filtering** — `filter_tasks(pet_name, completed)` lets you query tasks by pet, by status, or both at once. Underlying helpers `get_tasks_by_pet()` and `get_tasks_by_status()` remain available for single-criteria lookups.
- **Recurring tasks** — `complete_and_reschedule()` marks a task done and automatically creates the next occurrence using Python's `timedelta`: daily tasks roll forward one day, weekly tasks roll forward seven days. One-off (`as needed`) tasks are completed without spawning a follow-up.
- **Conflict detection** — `detect_conflicts()` checks every unique pair of tasks (via `itertools.combinations`) for two problem types: duplicate task titles on the same pet, and time-window overlaps across any pets. Conflicts are returned as plain warning strings — the scheduler never crashes, and the owner decides how to resolve them.

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
