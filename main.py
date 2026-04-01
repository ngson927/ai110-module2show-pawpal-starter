from pawpal_system import Task, Pet, Owner
from scheduler import Scheduler

owner = Owner(owner_id=1, name="Alex", available_time=90)

dog = Pet(pet_id=1, name="Buddy", species="Dog", age=3)
cat = Pet(pet_id=2, name="Whiskers", species="Cat", age=5)
owner.add_pet(dog)
owner.add_pet(cat)

# Buddy's tasks — Morning Walk and Medication overlap at 08:00
dog.add_task(Task(1, "Morning Walk", duration=30, priority=5, category="walking",    start_time="08:00"))
dog.add_task(Task(2, "Medication",   duration=10, priority=5, category="medication", start_time="08:15"))  # overlaps Walk
dog.add_task(Task(3, "Breakfast",    duration=10, priority=4, category="feeding",    start_time="09:00"))

# Whiskers's tasks — Breakfast overlaps with Buddy's Medication (cross-pet owner conflict)
cat.add_task(Task(4, "Breakfast",    duration=15, priority=4, category="feeding",    start_time="08:00"))  # overlaps Buddy's Walk + Medication
cat.add_task(Task(5, "Grooming",     duration=20, priority=2, category="grooming",   start_time="14:00"))

scheduler = Scheduler(owner)

print("=" * 55)
print("CONFLICT DETECTION REPORT")
print("=" * 55)
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  {warning}")
else:
    print("  No conflicts found.")

print()
print("=" * 55)
print("GENERATED DAILY SCHEDULE")
print("=" * 55)
scheduler.generate_plan()
scheduler.explain_plan()
