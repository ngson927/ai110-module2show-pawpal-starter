from dataclasses import dataclass, field
from datetime import date


@dataclass
class Task:
    task_id: int
    title: str
    duration: int           # in minutes
    priority: int           # 1 (low) to 5 (high)
    category: str           # e.g. "feeding", "walking", "medication", "grooming"
    frequency: str = "daily"        # e.g. "daily", "weekly", "as needed"
    start_time: str = "08:00"       # 24-hour "HH:MM" format
    due_date: date = field(default_factory=date.today)
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
