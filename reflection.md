# PawPal+ Project Reflection

## 1. System Design
My initial design for PawPal+ focused on the main user needs described in the scenario. I identified three core actions:

1. Enter and manage owner and pet information.
2. Add, edit, and prioritize pet care tasks.
3. Generate and view a daily care plan based on available time, task duration, and task priority.

The main classes in my design were Owner, Pet, Task, and Scheduler.

- Owner stores the owner's information, available time, and preferences.
- Pet stores the pet's basic information.
- Task stores each care activity with attributes such as duration, priority, category, and completion status.
- Scheduler is responsible for organizing tasks and generating a daily plan.


**a. Initial design**

My initial design for PawPal+ included four main classes: Owner, Pet, Task, and Scheduler.

- The Owner class stores information about the user, including their name, available time, and preferences for scheduling tasks.
- The Pet class represents the pet being cared for and stores basic information such as name, species, age, and notes.
- The Task class represents individual pet care activities such as feeding, walking, or grooming. Each task includes attributes like duration, priority, category, and completion status.
- The Scheduler class is responsible for managing tasks and generating a daily plan based on constraints such as available time and task priority.

These classes work together to model the system and support the core functionality of generating a daily pet care plan.

**b. Design changes**

After reviewing my class skeleton, I made small improvements to clarify the design.

I realized that several methods needed clear input parameters to be practical during implementation. For example, methods such as set_available_time(), update_preferences(), add_task(), edit_task(), and update_info() needed parameters so they could actually update or manage data. I also confirmed that the Scheduler should rely on the Owner's available_time when generating a daily plan.

The most significant structural change was moving task ownership from Scheduler to Pet. In the original skeleton, the Scheduler held a flat tasks list. During implementation it became clear that tasks belong to individual pets — a walk belongs to Buddy, not to the schedule. This changed Pet from a passive data container into an active owner of its own task list, and made the Scheduler retrieve tasks through Owner.get_all_tasks() rather than managing them directly.

The Scheduler was also separated into its own file (scheduler.py) to keep algorithmic planning logic isolated from the core domain models in pawpal_system.py.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints when generating a plan:

1. **Available time** — the total minutes the owner has per day. Tasks are added greedily until this limit is reached; any remaining tasks go into a skipped list.
2. **Task priority** — a 1–5 integer where higher values mean more urgent. The plan is sorted by priority descending so medication and feeding tasks appear before lower-stakes grooming tasks.
3. **Task frequency** — only tasks marked "daily" or "as needed" are included in today's plan. Weekly tasks are excluded unless their due date falls today.

Priority was chosen as the primary constraint because it directly reflects the owner's judgment about what matters most for their pet's health. Time is a hard cap, not a preference, so it acts as a ceiling rather than a sorting key.

**b. Tradeoffs**

The scheduler detects time overlap conflicts but does not resolve them. When two tasks overlap, it prints a warning and still includes both tasks in the generated plan. A more advanced system might automatically reschedule the lower-priority task or block it from being added. However, for a personal pet care app with a small number of tasks, warning the owner and letting them decide is the more appropriate behavior. Automatically rescheduling could move a medication task to an inconvenient time without the owner's knowledge, which is worse than surfacing the conflict clearly.

A second tradeoff is that conflict detection runs in O(n²) time by comparing every unique pair of tasks using itertools.combinations. For a household with two or three pets and a handful of daily tasks, this is fast and simple. If the app were extended to manage many pets or a full weekly calendar, a more efficient approach such as sorting tasks by start time and doing a linear scan would be worth considering. For this scenario, readability and simplicity were prioritized over performance.

---

## 3. AI Collaboration

**a. How you used AI**

AI tools were used across every phase of the project, but with different purposes at each stage.

During design, Copilot Chat with #codebase was used to brainstorm attributes and methods for each class, suggest edge cases for the test plan, and identify gaps in the initial UML (such as missing method parameters and the lack of task ownership on Pet). These were open-ended questions where the AI gave a starting point that I then evaluated and adjusted.

During implementation, Inline Chat was used to generate method stubs and suggest algorithmic approaches — for example, how to use sorted() with a lambda key to sort HH:MM strings, and how Python's timedelta could calculate the next due date for recurring tasks. The most effective prompts were specific and grounded: "how should sort_by_time() handle ties within the same hour" produced a more useful answer than "how do I sort tasks."

During testing, Copilot was used to draft test function names and assert patterns, which I then reviewed and adjusted to match the actual behavior of my classes.

**b. Judgment and verification**

One clear moment of not accepting a suggestion as-is was during conflict detection. An early AI suggestion proposed crashing the program with a raised exception when a time overlap was found. I rejected this because a scheduling conflict is not a bug — it is a normal user scenario. A pet owner might intentionally add overlapping tasks and want to see both in the plan while being warned. I kept the detect_conflicts() method returning plain warning strings rather than raising, and verified this by writing a test (test_detect_conflicts_flags_overlapping_times) that confirmed warnings are returned and the plan still generates.

A second example was with sorting. Copilot initially suggested comparing start_time strings directly as strings ("08:00" < "17:00"). This works for most cases but fails at edge cases like "9:00" vs "10:00" due to single-digit hour formatting. I replaced it with tuple comparison on (int(hour), int(minute)) and added a specific test (test_sort_by_time_handles_same_hour_different_minutes) to verify it handles sub-hour differences correctly.

**c. Separate chat sessions**

Starting a new Copilot Chat session for each phase — design, implementation, testing, and UI — made a measurable difference to code quality. When a single session accumulates too much context, later suggestions start referencing earlier drafts or stale method signatures. A fresh session for the testing phase meant Copilot only saw the finished implementation, not the intermediate skeleton, which produced more accurate test assertions.

The tradeoff is that switching sessions requires manually re-establishing context (pointing to the right files with #file or #codebase). That overhead is worth it for a multi-phase project where the design evolves significantly between phases.

---

## 4. Testing and Verification

**a. What you tested**

The test suite covers 14 behaviors across five groups:

- **Core behavior** — mark_complete() flips completed to True; adding a task to a Pet increases its task count. These were the first two tests written and serve as a sanity check that the data model works at all.
- **Sorting** — tasks added out of order are returned in chronological HH:MM order; tasks within the same hour are sorted correctly by minute.
- **Recurrence** — daily tasks produce a clone with due_date + 1 day; weekly tasks produce due_date + 7 days; as-needed tasks produce no clone; an invalid task_id returns None without crashing.
- **Conflict detection** — overlapping time windows are flagged; exact same start times are flagged; a clean schedule returns an empty conflict list.
- **Edge cases** — a pet with no tasks produces an empty plan; the total scheduled time never exceeds available_time; an unknown pet name returns an empty list rather than an error.

Recurrence and conflict detection were the most important to test because they involve branching logic with multiple outcomes depending on frequency type and time intervals. A wrong result there could silently corrupt the schedule without any obvious error.

**b. Confidence**

★★★★☆ (4 / 5)

Confidence is high for all core scheduling behaviors. The happy paths and the most likely edge cases are covered and passing. The missing star reflects two untested areas: the Streamlit UI layer (app.py interactions are not automatically tested) and persistence — all tests run on in-memory data, so any file storage or database layer added later would need its own test suite.

If given more time, the next edge cases to test would be: an owner with zero available time, two pets with tasks that exactly share an end/start time boundary (adjacency vs. overlap), and reset_daily_tasks() leaving weekly tasks untouched.

---

## 5. Reflection

**a. What went well**

The separation of concerns between pawpal_system.py and scheduler.py worked well. Keeping the domain models (Owner, Pet, Task) isolated from the scheduling algorithm meant that adding new features to the Scheduler — recurrence, conflict detection, filtering — never required touching the data classes. When bugs appeared they were easy to locate because each file had a single, clear responsibility.

The incremental build approach also worked well. Starting from a skeleton with pass stubs, then fleshing out one method at a time with a terminal test in main.py, meant problems were caught early and in isolation rather than all at once.

**b. What you would improve**

The current generate_plan() uses a greedy algorithm — it adds tasks in priority order until time runs out. This can leave time on the table when a lower-priority short task would fit but a higher-priority long task blocked it. A more complete solution would use a knapsack-style approach that considers all combinations and finds the highest-priority set that fits within the time budget.

I would also add persistent storage. Right now all data lives in st.session_state, which resets on browser refresh. A lightweight SQLite backend or JSON file would make the app genuinely useful across multiple days.

**c. Key takeaway**

The most important thing I learned is that AI is a powerful collaborator but a poor architect. Copilot could generate correct code for a method in isolation, but it could not see that the Scheduler holding a flat task list was the wrong design — that insight required stepping back and thinking about ownership and responsibility across the whole system. The AI accelerated implementation; the design decisions still required human judgment. Being the lead architect means knowing when to accept a suggestion, when to modify it, and when the suggestion is technically correct but structurally wrong for the system you are building.

---

## 6. Prompt Comparison: Multi-Model Test

**Task tested:** Rescheduling logic for weekly recurring tasks using Python's timedelta.

**Prompt used:** "Write a Python method that marks a task complete and creates a new instance for the next occurrence. For daily tasks use due_date + 1 day, for weekly tasks use due_date + 7 days. Use dataclasses.replace to clone the task."

**Model A — GPT-4o:**
Returned a standalone function (not a method) that took a task and pet as separate parameters. Used copy.deepcopy() instead of dataclasses.replace(), which is heavier than necessary for a dataclass. The logic was correct but not idiomatic Python for dataclasses.

**Model B — Claude Sonnet:**
Returned a method on the Scheduler class that used dataclasses.replace() directly, matching the existing pattern in the codebase. Also correctly seeded the next task ID from _next_id rather than hardcoding. The result integrated cleanly without any structural changes.

**Verdict:**
Claude's suggestion was more modular and Pythonic for this codebase because it understood the existing class structure and used the dataclass-native replace() function rather than a generic deep copy. GPT-4o's version would have required refactoring to fit the Scheduler pattern. The key lesson: model outputs are more useful when the prompt includes the specific file context (#file:scheduler.py) rather than describing the problem in the abstract.
