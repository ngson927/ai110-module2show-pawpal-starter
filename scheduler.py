from dataclasses import replace
from datetime import date, timedelta
from itertools import combinations
from pawpal_system import Owner

TODAY_FREQUENCIES = {"daily", "as needed"}
RECURRING_FREQUENCIES = {"daily", "weekly"}


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.daily_plan = []
        self.skipped = []
        self.conflicts = []
        self._next_id = max((t.task_id for t in owner.get_all_tasks()), default=0) + 1

    # ------------------------------------------------------------------
    # Task management
    # ------------------------------------------------------------------

    def add_task(self, pet, task):
        """Assign a task to a specific pet."""
        pet.add_task(task)

    def _find_task_and_pet(self, task_id):
        """Return (task, pet) for the given task_id, or (None, None) if not found."""
        for pet in self.owner.pets:
            for task in pet.get_tasks():
                if task.task_id == task_id:
                    return task, pet
        return None, None

    def complete_and_reschedule(self, task_id):
        """Mark a task complete and automatically queue its next occurrence.

        For 'daily' tasks the next due date is today + 1 day.
        For 'weekly' tasks the next due date is today + 7 days.
        'as needed' tasks are completed without creating a follow-up.
        Returns the new Task if one was created, otherwise None.
        """
        task, pet = self._find_task_and_pet(task_id)
        if task is None:
            return None

        task.mark_complete()

        if task.frequency not in RECURRING_FREQUENCIES:
            return None

        delta = timedelta(days=1) if task.frequency == "daily" else timedelta(weeks=1)
        next_due = task.due_date + delta

        next_task = replace(task, task_id=self._next_id, completed=False, due_date=next_due)
        self._next_id += 1
        pet.add_task(next_task)
        return next_task

    def edit_task(self, task_id, **kwargs):
        """Find a task by ID across all pets and update its fields."""
        for task in self.owner.get_all_tasks():
            if task.task_id == task_id:
                task.edit_task(**kwargs)
                return

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def sort_by_time(self, tasks=None):
        """Return tasks sorted chronologically by their start_time (HH:MM).

        If no task list is provided, sorts all tasks across every pet.
        Converts 'HH:MM' to a (hour, minute) tuple for accurate comparison.
        """
        source = tasks if tasks is not None else self.owner.get_all_tasks()
        return sorted(source, key=lambda t: tuple(int(x) for x in t.start_time.split(":")))

    def get_tasks_by_pet(self, pet_name):
        """Return all tasks belonging to the named pet."""
        for pet in self.owner.pets:
            if pet.name.lower() == pet_name.lower():
                return pet.get_tasks()
        return []

    def get_tasks_by_status(self, completed: bool):
        """Return all tasks across pets filtered by completion status."""
        return [t for t in self.owner.get_all_tasks() if t.completed == completed]

    def filter_tasks(self, pet_name=None, completed=None):
        """Return tasks matching all supplied filters.

        pet_name: if given, restricts results to that pet (case-insensitive).
        completed: if True returns only done tasks; if False returns only pending.
        Both filters can be combined; omitting a filter applies no restriction.
        """
        tasks = self.owner.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in self.get_tasks_by_pet(pet_name)]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    # ------------------------------------------------------------------
    # Recurring task handling
    # ------------------------------------------------------------------

    def get_todays_tasks(self):
        """Return only tasks whose frequency makes them relevant today."""
        return [
            t for t in self.owner.get_all_tasks()
            if t.frequency in TODAY_FREQUENCIES and not t.completed
        ]

    def reset_daily_tasks(self):
        """Reset completion status for all daily tasks (call at start of new day)."""
        for task in self.owner.get_all_tasks():
            if task.frequency == "daily":
                task.completed = False

    # ------------------------------------------------------------------
    # Conflict detection
    # ------------------------------------------------------------------

    @staticmethod
    def _to_minutes(time_str):
        """Convert 'HH:MM' string to total minutes since midnight."""
        h, m = map(int, time_str.split(":"))
        return h * 60 + m

    def detect_conflicts(self):
        """Scan all tasks and return a list of human-readable warning strings.

        Two conflict types are detected:
          1. Duplicate title — same task name assigned more than once to the same pet.
          2. Time overlap — two tasks (same or different pets) whose time windows intersect,
             indicating the owner cannot perform both simultaneously.
        Never raises an exception; returns an empty list when no conflicts exist.
        """
        self.conflicts = []

        # Build a flat list of (task, pet_name) across all pets
        all_entries = [
            (task, pet.name)
            for pet in self.owner.pets
            for task in pet.get_tasks()
        ]

        # 1. Duplicate title on the same pet
        for pet in self.owner.pets:
            seen = {}
            for task in pet.get_tasks():
                key = task.title.lower()
                if key in seen:
                    self.conflicts.append(
                        f"WARNING: '{task.title}' assigned twice to {pet.name} "
                        f"(task IDs {seen[key]} and {task.task_id})"
                    )
                else:
                    seen[key] = task.task_id

        # 2. Time overlap — check every unique pair of tasks across all pets
        for (task_a, pet_a), (task_b, pet_b) in combinations(all_entries, 2):
            start_a = self._to_minutes(task_a.start_time)
            end_a   = start_a + task_a.duration
            start_b = self._to_minutes(task_b.start_time)
            end_b   = start_b + task_b.duration

            if start_a < end_b and start_b < end_a:
                scope = pet_a if pet_a == pet_b else f"{pet_a} and {pet_b}"
                self.conflicts.append(
                    f"WARNING: Time overlap for {scope} — "
                    f"'{task_a.title}' ({task_a.start_time}, {task_a.duration} min) "
                    f"overlaps '{task_b.title}' ({task_b.start_time}, {task_b.duration} min)"
                )

        return self.conflicts

    # ------------------------------------------------------------------
    # Plan generation
    # ------------------------------------------------------------------

    def generate_plan(self):
        """Build today's plan: priority-sorted, time-bounded, recurring-aware."""
        if self.owner.available_time <= 0:
            self.daily_plan = []
            self.skipped = self.get_todays_tasks()
            return self.daily_plan

        candidates = self.get_todays_tasks()

        # Sort by priority (high first), break ties by shortest duration first
        candidates = sorted(candidates, key=lambda t: (-t.priority, t.duration))

        scheduled, skipped, total = [], [], 0
        for task in candidates:
            if total + task.duration <= self.owner.available_time:
                scheduled.append(task)
                total += task.duration
            else:
                skipped.append(task)

        self.daily_plan = scheduled
        self.skipped = skipped
        return self.daily_plan

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def explain_plan(self):
        """Print a grouped, annotated summary of the daily plan."""
        if not self.daily_plan:
            self.generate_plan()

        print(f"\nDaily Plan for {self.owner.name} ({self.owner.available_time} min available)")

        # Group scheduled tasks by pet
        for pet in self.owner.pets:
            pet_tasks = [t for t in self.daily_plan if t in pet.get_tasks()]
            if not pet_tasks:
                continue
            print(f"\n  {pet.name} ({pet.species})")
            print("  " + "-" * 40)
            for task in pet_tasks:
                freq = f"[{task.frequency}]"
                print(f"    [{task.priority}★] {task.title:<20} {task.duration:>3} min  {freq}")

        print(f"\n  Total scheduled : {self.get_total_scheduled_time()} min")
        print(f"  Time remaining  : {self.owner.available_time - self.get_total_scheduled_time()} min")

        if self.skipped:
            print(f"\n  Skipped ({len(self.skipped)} tasks — not enough time):")
            for task in self.skipped:
                print(f"    - {task.title} ({task.duration} min)")

        if self.conflicts:
            print(f"\n  Conflicts detected:")
            for c in self.conflicts:
                print(f"    ⚠ {c}")

    def get_total_scheduled_time(self):
        """Return the total duration in minutes of all tasks in the daily plan."""
        return sum(task.duration for task in self.daily_plan)

    # ------------------------------------------------------------------
    # Next available slot
    # ------------------------------------------------------------------

    def find_next_slot(self, duration):
        """Return the first HH:MM start time where duration minutes fit without overlap.

        Walks from 06:00 to 22:00 in 5-minute increments.  A candidate slot is
        accepted when [slot, slot+duration) does not overlap any task already in
        self.daily_plan.  Returns None if no such slot exists before 22:00.
        """
        DAY_START = self._to_minutes("06:00")
        DAY_END   = self._to_minutes("22:00")

        # Build list of (start, end) intervals for planned tasks
        booked = []
        for task in sorted(self.daily_plan, key=lambda t: self._to_minutes(t.start_time)):
            start = self._to_minutes(task.start_time)
            booked.append((start, start + task.duration))

        current = DAY_START
        while current + duration <= DAY_END:
            end = current + duration
            overlaps = any(start < end and current < task_end for start, task_end in booked)
            if not overlaps:
                hours, mins = divmod(current, 60)
                return f"{hours:02d}:{mins:02d}"
            current += 5

        return None
