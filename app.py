import os
import streamlit as st
from pawpal_system import Owner, Pet, Task
from scheduler import Scheduler

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Helper functions ---

def priority_label(priority: int) -> str:
    """Return a coloured emoji label for a numeric priority."""
    if priority >= 4:
        return "🔴 High"
    if priority == 3:
        return "🟡 Medium"
    return "🟢 Low"


def category_emoji(category: str) -> str:
    """Return an emoji-prefixed label for a task category."""
    mapping = {
        "walking": "🦮 Walking",
        "feeding": "🍖 Feeding",
        "medication": "💊 Medication",
        "grooming": "✂️ Grooming",
    }
    return mapping.get(category.lower(), "🐾 Other")


# --- Session State Init ---
if "owner" not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.owner = Owner.load_from_json(DATA_FILE)
        all_tasks = st.session_state.owner.get_all_tasks()
        st.session_state.pet_counter = (
            max((p.pet_id for p in st.session_state.owner.pets), default=0) + 1
        )
        st.session_state.task_counter = (
            max((t.task_id for t in all_tasks), default=0) + 1
        )
    else:
        st.session_state.owner = Owner(owner_id=1, name="Jordan", available_time=60)
        st.session_state.pet_counter = 1
        st.session_state.task_counter = 1

owner = st.session_state.owner

# --- Owner Info ---
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.available_time = st.number_input(
        "Available time (min/day)", min_value=10, max_value=480, value=owner.available_time
    )

st.divider()

# --- Add a Pet ---
st.subheader("Add a Pet")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    age = st.number_input("Age", min_value=0, max_value=30, value=2)

if st.button("Add pet"):
    new_pet = Pet(pet_id=st.session_state.pet_counter, name=pet_name, species=species, age=age)
    owner.add_pet(new_pet)
    st.session_state.pet_counter += 1
    owner.save_to_json(DATA_FILE)
    st.success(f"Added {pet_name} the {species}!")

if owner.pets:
    st.write("**Your pets:**", ", ".join(p.name for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Add a Task ---
st.subheader("Add a Task")

if not owner.pets:
    st.warning("Add a pet first before adding tasks.")
else:
    pet_names = [p.name for p in owner.pets]
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        selected_pet_name = st.selectbox("Assign to pet", pet_names)
    with col2:
        task_title = st.text_input("Task title", value="Morning walk")
    with col3:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col4:
        priority = st.selectbox("Priority (1=low, 5=high)", [1, 2, 3, 4, 5], index=4)

    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("Category", ["feeding", "walking", "medication", "grooming", "other"])
    with col2:
        start_time = st.text_input("Start time (HH:MM)", value="08:00")
    frequency = st.selectbox("Frequency", ["daily", "weekly", "as needed"])

    if st.button("Add task"):
        selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)
        new_task = Task(
            task_id=st.session_state.task_counter,
            title=task_title,
            duration=duration,
            priority=priority,
            category=category,
            start_time=start_time,
            frequency=frequency,
        )
        selected_pet.add_task(new_task)
        st.session_state.task_counter += 1
        owner.save_to_json(DATA_FILE)
        st.success(f"Added '{task_title}' to {selected_pet_name}.")

    # --- All Tasks (sorted by time) ---
    all_tasks = owner.get_all_tasks()
    if all_tasks:
        scheduler = Scheduler(owner)
        sorted_tasks = scheduler.sort_by_time()

        st.write("**All tasks — sorted by start time:**")
        st.table([
            {
                "Start": t.start_time,
                "Pet": next(p.name for p in owner.pets if t in p.get_tasks()),
                "Task": t.title,
                "Duration (min)": t.duration,
                "Priority": priority_label(t.priority),
                "Category": category_emoji(t.category),
                "Frequency": t.frequency,
                "Status": "Done" if t.completed else "Pending",
            }
            for t in sorted_tasks
        ])
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# --- Generate Schedule ---
st.subheader("Generate Schedule")

if st.button("Generate schedule"):
    if not owner.pets or not owner.get_all_tasks():
        st.warning("Add at least one pet and one task first.")
    else:
        scheduler = Scheduler(owner)

        # Conflict detection — show before the plan
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.error("Scheduling conflicts detected — review before finalising your plan:")
            for c in conflicts:
                st.warning(c)

        plan = scheduler.generate_plan()

        if plan:
            col1, col2, col3 = st.columns(3)
            col1.metric("Scheduled tasks", len(plan))
            col2.metric("Total time", f"{scheduler.get_total_scheduled_time()} min")
            col3.metric("Time remaining", f"{owner.available_time - scheduler.get_total_scheduled_time()} min")

            # Plan grouped by pet
            for pet in owner.pets:
                pet_tasks = [t for t in plan if t in pet.get_tasks()]
                if not pet_tasks:
                    continue
                st.write(f"**{pet.name}** ({pet.species})")
                st.table([
                    {
                        "Start": t.start_time,
                        "Task": t.title,
                        "Duration (min)": t.duration,
                        "Priority": priority_label(t.priority),
                        "Category": category_emoji(t.category),
                        "Frequency": t.frequency,
                    }
                    for t in scheduler.sort_by_time(pet_tasks)
                ])

            # Skipped tasks
            if scheduler.skipped:
                with st.expander(f"Skipped tasks ({len(scheduler.skipped)} — not enough time)"):
                    for t in scheduler.skipped:
                        st.write(
                            f"- **{t.title}** ({t.duration} min, {priority_label(t.priority)})"
                        )

            owner.save_to_json(DATA_FILE)
            st.success("Schedule generated successfully!")
        else:
            st.error("No tasks fit within your available time. Try increasing available time or reducing task durations.")
