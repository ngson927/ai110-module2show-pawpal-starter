from pawpal_system import Task, Pet, Owner, Scheduler

# --- Owner ---
owner = Owner(owner_id=1, name="Alex", available_time=90)

# --- Pets ---
dog = Pet(pet_id=1, name="Buddy", species="Dog", age=3)
cat = Pet(pet_id=2, name="Whiskers", species="Cat", age=5)

owner.add_pet(dog)
owner.add_pet(cat)

# --- Buddy's Tasks ---
dog.add_task(Task(1, "Morning Walk",    duration=30, priority=5, category="walking"))
dog.add_task(Task(2, "Breakfast",       duration=10, priority=4, category="feeding"))
dog.add_task(Task(3, "Flea Medication", duration=5,  priority=3, category="medication"))

# --- Whiskers's Tasks ---
cat.add_task(Task(4, "Breakfast",       duration=10, priority=4, category="feeding"))
cat.add_task(Task(5, "Grooming",        duration=20, priority=2, category="grooming"))

# --- Generate and Print Today's Schedule ---
scheduler = Scheduler(owner)
scheduler.generate_plan()

print("=" * 45)
print("       PAWPAL+ — TODAY'S SCHEDULE")
print("=" * 45)
print(f"  Owner : {owner.name}")
print(f"  Pets  : {', '.join(p.name for p in owner.pets)}")
print(f"  Time  : {owner.available_time} min available")
print("-" * 45)

for task in scheduler.daily_plan:
    print(f"  [{task.priority}★] {task.title:<20} {task.duration:>3} min  |  {task.category}")

print("-" * 45)
print(f"  Total scheduled: {scheduler.get_total_scheduled_time()} min")
print("=" * 45)
