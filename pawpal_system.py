import json
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

    def to_dict(self):
        """Serialize the Owner, its Pets, and their Tasks to a plain dictionary."""
        return {
            "owner_id": self.owner_id,
            "name": self.name,
            "available_time": self.available_time,
            "preferences": self.preferences,
            "pets": [
                {
                    "pet_id": pet.pet_id,
                    "name": pet.name,
                    "species": pet.species,
                    "age": pet.age,
                    "notes": pet.notes,
                    "tasks": [
                        {
                            "task_id": task.task_id,
                            "title": task.title,
                            "duration": task.duration,
                            "priority": task.priority,
                            "category": task.category,
                            "frequency": task.frequency,
                            "start_time": task.start_time,
                            "due_date": task.due_date.isoformat(),
                            "completed": task.completed,
                        }
                        for task in pet.get_tasks()
                    ],
                }
                for pet in self.pets
            ],
        }

    def save_to_json(self, filepath):
        """Write the owner's data to a JSON file at filepath."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, filepath):
        """Read a JSON file and reconstruct a full Owner with all Pets and Tasks."""
        with open(filepath, "r") as f:
            data = json.load(f)

        owner = cls(
            owner_id=data["owner_id"],
            name=data["name"],
            available_time=data["available_time"],
            preferences=data.get("preferences", {}),
        )

        for pet_data in data.get("pets", []):
            pet = Pet(
                pet_id=pet_data["pet_id"],
                name=pet_data["name"],
                species=pet_data["species"],
                age=pet_data["age"],
                notes=pet_data.get("notes", ""),
            )
            for task_data in pet_data.get("tasks", []):
                task = Task(
                    task_id=task_data["task_id"],
                    title=task_data["title"],
                    duration=task_data["duration"],
                    priority=task_data["priority"],
                    category=task_data["category"],
                    frequency=task_data.get("frequency", "daily"),
                    start_time=task_data.get("start_time", "08:00"),
                    due_date=date.fromisoformat(task_data["due_date"]),
                    completed=task_data.get("completed", False),
                )
                pet.add_task(task)
            owner.add_pet(pet)

        return owner
