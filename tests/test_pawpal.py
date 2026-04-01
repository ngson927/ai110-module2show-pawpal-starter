import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner
from scheduler import Scheduler


# --- Helpers ---

def make_owner(available_time=90):
    owner = Owner(owner_id=1, name="Alex", available_time=available_time)
    dog = Pet(pet_id=1, name="Buddy", species="Dog", age=3)
    owner.add_pet(dog)
    return owner, dog


# --- Existing tests ---

def test_mark_complete_changes_status():
    task = Task(task_id=1, title="Morning Walk", duration=30, priority=5, category="walking")
    assert task.completed == False
    task.mark_complete()
    assert task.completed == True


def test_add_task_increases_pet_task_count():
    pet = Pet(pet_id=1, name="Buddy", species="Dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task(task_id=1, title="Breakfast", duration=10, priority=4, category="feeding"))
    assert len(pet.tasks) == 1


# --- Sorting ---

def test_sort_by_time_returns_chronological_order():
    owner, dog = make_owner()
    dog.add_task(Task(1, "Evening Walk", 30, 3, "walking",  start_time="17:00"))
    dog.add_task(Task(2, "Medication",   5,  5, "medication", start_time="09:00"))
    dog.add_task(Task(3, "Breakfast",    10, 4, "feeding",   start_time="07:30"))

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time()
    times = [t.start_time for t in sorted_tasks]
    assert times == ["07:30", "09:00", "17:00"]


def test_sort_by_time_handles_same_hour_different_minutes():
    owner, dog = make_owner()
    dog.add_task(Task(1, "Task A", 10, 3, "feeding",  start_time="08:45"))
    dog.add_task(Task(2, "Task B", 10, 3, "feeding",  start_time="08:05"))
    dog.add_task(Task(3, "Task C", 10, 3, "feeding",  start_time="08:30"))

    scheduler = Scheduler(owner)
    times = [t.start_time for t in scheduler.sort_by_time()]
    assert times == ["08:05", "08:30", "08:45"]


# --- Recurrence ---

def test_daily_task_creates_next_occurrence_one_day_later():
    owner, dog = make_owner()
    today = date.today()
    dog.add_task(Task(1, "Morning Walk", 30, 5, "walking", frequency="daily", due_date=today))

    scheduler = Scheduler(owner)
    next_task = scheduler.complete_and_reschedule(1)

    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed == False


def test_weekly_task_creates_next_occurrence_seven_days_later():
    owner, dog = make_owner()
    today = date.today()
    dog.add_task(Task(1, "Flea Bath", 20, 3, "grooming", frequency="weekly", due_date=today))

    scheduler = Scheduler(owner)
    next_task = scheduler.complete_and_reschedule(1)

    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)
    assert next_task.completed == False


def test_as_needed_task_does_not_create_recurrence():
    owner, dog = make_owner()
    dog.add_task(Task(1, "Vet Visit", 60, 5, "medical", frequency="as needed"))

    scheduler = Scheduler(owner)
    next_task = scheduler.complete_and_reschedule(1)

    assert next_task is None
    assert len(dog.get_tasks()) == 1  # original only, no clone


def test_reschedule_nonexistent_task_returns_none():
    owner, dog = make_owner()
    scheduler = Scheduler(owner)
    result = scheduler.complete_and_reschedule(999)
    assert result is None


# --- Conflict Detection ---

def test_detect_conflicts_flags_overlapping_times():
    owner, dog = make_owner()
    dog.add_task(Task(1, "Morning Walk", 30, 5, "walking",    start_time="08:00"))
    dog.add_task(Task(2, "Medication",   10, 5, "medication", start_time="08:15"))  # overlaps Walk

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "Morning Walk" in conflicts[0]
    assert "Medication" in conflicts[0]


def test_detect_conflicts_flags_exact_same_start_time():
    owner, dog = make_owner()
    dog.add_task(Task(1, "Breakfast", 10, 4, "feeding",  start_time="08:00"))
    dog.add_task(Task(2, "Grooming",  15, 2, "grooming", start_time="08:00"))

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) >= 1


def test_detect_no_conflicts_when_tasks_do_not_overlap():
    owner, dog = make_owner()
    dog.add_task(Task(1, "Breakfast",    10, 4, "feeding",  start_time="07:00"))
    dog.add_task(Task(2, "Morning Walk", 30, 5, "walking",  start_time="08:00"))
    dog.add_task(Task(3, "Medication",   5,  5, "medication", start_time="09:00"))

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()
    assert conflicts == []


# --- Edge Cases ---

def test_generate_plan_empty_when_no_tasks():
    owner, dog = make_owner()
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    assert plan == []


def test_generate_plan_does_not_exceed_available_time():
    owner, dog = make_owner(available_time=20)
    dog.add_task(Task(1, "Long Walk",  30, 5, "walking"))
    dog.add_task(Task(2, "Breakfast",  10, 4, "feeding"))

    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    assert scheduler.get_total_scheduled_time() <= 20


def test_filter_tasks_unknown_pet_returns_empty():
    owner, dog = make_owner()
    dog.add_task(Task(1, "Breakfast", 10, 4, "feeding"))
    scheduler = Scheduler(owner)
    result = scheduler.filter_tasks(pet_name="Unknown")
    assert result == []
