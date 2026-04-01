from dataclasses import dataclass, field


class Owner:
    def __init__(self, owner_id, name, available_time, preferences):
        self.owner_id = owner_id
        self.name = name
        self.available_time = available_time
        self.preferences = preferences

    def set_available_time(self):
        pass

    def update_preferences(self):
        pass


@dataclass
class Pet:
    pet_id: int
    name: str
    species: str
    age: int
    notes: str = ""

    def update_info(self):
        pass


@dataclass
class Task:
    task_id: int
    title: str
    duration: int
    priority: int
    category: str
    completed: bool = False

    def edit_task(self):
        pass

    def mark_complete(self):
        pass


class Scheduler:
    def __init__(self, owner, pet):
        self.owner = owner
        self.pet = pet
        self.tasks = []
        self.daily_plan = []

    def add_task(self):
        pass

    def edit_task(self):
        pass

    def generate_plan(self):
        pass

    def explain_plan(self):
        pass

    def get_total_scheduled_time(self):
        pass
