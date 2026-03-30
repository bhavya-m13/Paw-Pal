import uuid
import streamlit as st
from datetime import datetime, date, time
from pawpal_system import Owner, Pet, Task, Scheduler, Priority

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ── Session state: initialize once, reuse on every rerun ─────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        id=str(uuid.uuid4()),
        name="Jordan",
        email="jordan@example.com",
        phone="555-0100",
    )

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(owners=[st.session_state.owner])

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

# ── Sidebar: Add a pet ───────────────────────────────────────────────────────
with st.sidebar:
    st.header("Manage Pets")
    new_pet_name = st.text_input("Pet Name", placeholder="e.g. Mochi")
    new_species   = st.selectbox("Species", ["Dog", "Cat", "Bird", "Other"])
    new_breed     = st.text_input("Breed", placeholder="e.g. Shiba Inu")
    new_dob       = st.date_input("Date of Birth", value=date(2021, 1, 1))

    if st.button("Add Pet"):
        if new_pet_name.strip():
            pet = Pet(
                id=str(uuid.uuid4()),
                owner_id=owner.id,
                name=new_pet_name.strip(),
                species=new_species,
                breed=new_breed.strip() or "Unknown",
                birth_date=datetime.combine(new_dob, time()),
            )
            owner.add_pet(pet)
            scheduler._rebuild_cache()
            st.success(f"{new_pet_name} added!")
        else:
            st.error("Please enter a pet name.")

    st.divider()

    # Remove a pet
    if owner.pets:
        st.subheader("Remove a Pet")
        pet_to_remove = st.selectbox(
            "Select pet to remove",
            options=[p.name for p in owner.pets],
            key="remove_pet_select",
        )
        if st.button("Remove Pet", type="secondary"):
            target = next((p for p in owner.pets if p.name == pet_to_remove), None)
            if target:
                owner.remove_pet(target.id)
                scheduler._rebuild_cache()
                st.warning(f"{pet_to_remove} removed.")

# ── Main: Schedule a Task ────────────────────────────────────────────────────
st.subheader("Schedule a Task")

if not owner.pets:
    st.info("👈 Add a pet in the sidebar first!")
else:
    selected_pet_name = st.selectbox(
        "Select Pet",
        options=[p.name for p in owner.pets],
    )
    selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)

    col1, col2 = st.columns([2, 1])
    with col1:
        task_title = st.text_input("Task Title", placeholder="e.g. Morning Walk")
        task_desc  = st.text_area("Description", placeholder="Details...", height=80)
        task_cat   = st.selectbox("Category", ["Exercise", "Medication", "Health", "Feeding", "Grooming", "Other"])
    with col2:
        task_date     = st.date_input("Due Date", value=date.today())
        task_time     = st.time_input("Due Time", value=time(9, 0))
        priority_label = st.select_slider("Priority", options=["LOW", "MEDIUM", "HIGH"], value="MEDIUM")

    if st.button("Add Task", type="primary"):
        if task_title.strip():
            task = Task(
                id=str(uuid.uuid4()),
                pet_id=selected_pet.id,
                title=task_title.strip(),
                description=task_desc.strip(),
                due_date=datetime.combine(task_date, task_time),
                category=task_cat,
                is_completed=False,
                priority=Priority[priority_label],
            )
            selected_pet.add_task(task)
            scheduler._rebuild_cache()
            st.toast(f"Task added for {selected_pet_name}!")
        else:
            st.error("Please enter a task title.")

# ── Main: Today's Schedule ───────────────────────────────────────────────────
st.divider()
st.subheader("Today's Schedule")

upcoming = scheduler.sort_by_due_date(scheduler.get_upcoming_tasks(days=1))
pet_lookup = {p.id: p for p in owner.pets}

if not upcoming:
    st.info("No upcoming tasks. Add some tasks above!")
else:
    for task in upcoming:
        pet_name = pet_lookup[task.pet_id].name if task.pet_id in pet_lookup else "Unknown"
        priority_colors = {Priority.HIGH: "🔴", Priority.MEDIUM: "🟡", Priority.LOW: "🟢"}

        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 3, 1])
            c1.metric("Time", task.due_date.strftime("%I:%M %p"))
            c2.markdown(f"**{task.title}** — {pet_name}  \n*{task.category}* · {task.description}")
            c3.markdown(f"{priority_colors[task.priority]} {task.priority.name}")

            if st.button("Mark Complete", key=f"complete_{task.id}"):
                task.mark_complete()
                scheduler._rebuild_cache()
                st.rerun()

# ── Expander: System state ───────────────────────────────────────────────────
with st.expander("System Data Status"):
    st.write(f"**Owner:** {owner.name} ({owner.email})")
    st.write(f"**Pets:** {[p.name for p in owner.pets]}")
    for pet in owner.pets:
        st.write(f"  • {pet.name}: {len(pet.tasks)} task(s)")
    st.write(f"**Scheduler cache:** {len(scheduler.get_all_tasks())} total task(s)")
