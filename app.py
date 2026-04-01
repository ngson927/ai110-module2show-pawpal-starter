import streamlit as st
from pawpal_system import Owner, Pet, Task
from scheduler import Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Session State Init ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_id=1, name="Jordan", available_time=60)
if "pet_counter" not in st.session_state:
    st.session_state.pet_counter = 1
if "task_counter" not in st.session_state:
    st.session_state.task_counter = 1

owner = st.session_state.owner

# --- Owner Info ---
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.available_time = st.number_input("Available time (min/day)", min_value=10, max_value=480, value=owner.available_time)

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
    new_pet = Pet(
        pet_id=st.session_state.pet_counter,
        name=pet_name,
        species=species,
        age=age
    )
    owner.add_pet(new_pet)
    st.session_state.pet_counter += 1
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

    category = st.selectbox("Category", ["feeding", "walking", "medication", "grooming", "other"])

    if st.button("Add task"):
        selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)
        new_task = Task(
            task_id=st.session_state.task_counter,
            title=task_title,
            duration=duration,
            priority=priority,
            category=category
        )
        selected_pet.add_task(new_task)
        st.session_state.task_counter += 1
        st.success(f"Added '{task_title}' to {selected_pet_name}.")

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.write("**All tasks:**")
        st.table([
            {"Pet": p.name, "Task": t.title, "Duration": t.duration, "Priority": t.priority, "Category": t.category}
            for p in owner.pets for t in p.get_tasks()
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
        plan = scheduler.generate_plan()
        if plan:
            st.success(f"Schedule for {owner.name} ({owner.available_time} min available)")
            st.table([
                {"Priority": t.priority, "Task": t.title, "Duration (min)": t.duration, "Category": t.category}
                for t in plan
            ])
            st.metric("Total scheduled time", f"{scheduler.get_total_scheduled_time()} min")
        else:
            st.warning("No tasks fit within your available time.")
