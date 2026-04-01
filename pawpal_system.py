from dataclasses import dataclass, field


@dataclass
class Task:
    task_id: int
    title: str
    duration: int           # in minutes
    priority: int           # 1 (low) to 5 (high)
    category: str           # e.g. "feeding", "walking", "medication", "grooming"
    frequency: str = "daily"  # e.g. "daily", "weekly", "as needed"
    completed: bool = False

    def edit_task(self, **kwargs):
        """Update one or more task fields by keyword argument."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True


@dataclass
class Pet:
    pet_id: int
    name: str
    species: str
    age: int
    notes: str = ""
    tasks: list = field(default_factory=list)

    def update_info(self, **kwargs):
        """Update one or more pet attributes by keyword argument."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def add_task(self, task):
        """Add a Task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self):
        """Return the list of tasks assigned to this pet."""
        return self.tasks


class Owner:
    def __init__(self, owner_id, name, available_time, preferences=None):
        self.owner_id = owner_id
        self.name = name
        self.available_time = available_time  # total minutes available per day
        self.preferences = preferences or {}
        self.pets = []

    def set_available_time(self, minutes):
        """Set the owner's total available time in minutes per day."""
        self.available_time = minutes

    def update_preferences(self, new_preferences):
        """Merge new key-value pairs into the owner's preferences."""
        self.preferences.update(new_preferences)

    def add_pet(self, pet):
        """Add a Pet to the owner's list of pets."""
        self.pets.append(pet)

    def get_all_tasks(self):
        """Return a flat list of all tasks across every pet the owner has."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


class Scheduler:
    def __init__(self, owner):
        self.owner = owner
        self.daily_plan = []

    def add_task(self, pet, task):
        """Assign a task to a specific pet."""
        pet.add_task(task)

    def edit_task(self, task_id, **kwargs):
        """Find a task by ID across all pets and update its fields."""
        for task in self.owner.get_all_tasks():
            if task.task_id == task_id:
                task.edit_task(**kwargs)
                return

    def generate_plan(self):
        """Build a priority-sorted daily plan that fits within the owner's available time."""
        all_tasks = self.owner.get_all_tasks()
        pending = [t for t in all_tasks if not t.completed]
        self.daily_plan = sorted(pending, key=lambda t: t.priority, reverse=True)

        scheduled, total = [], 0
        for task in self.daily_plan:
            if total + task.duration <= self.owner.available_time:
                scheduled.append(task)
                total += task.duration

        self.daily_plan = scheduled
        return self.daily_plan

    def explain_plan(self):
        """Print a formatted summary of the current daily plan to the terminal."""
        if not self.daily_plan:
            self.generate_plan()
        print(f"\nDaily Plan for {self.owner.name} ({self.owner.available_time} min available)")
        print("-" * 45)
        for task in self.daily_plan:
            status = "Done" if task.completed else "Pending"
            print(f"  [{task.priority}★] {task.title} | {task.duration} min | {task.category} | {status}")
        print("-" * 45)
        print(f"  Total scheduled: {self.get_total_scheduled_time()} min")

    def get_total_scheduled_time(self):
        """Return the total duration in minutes of all tasks in the daily plan."""
        return sum(task.duration for task in self.daily_plan)
