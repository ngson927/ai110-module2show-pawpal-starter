import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet


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
