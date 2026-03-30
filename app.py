import uuid
import streamlit as st
from datetime import datetime, date, time
from pawpal_system import Owner, Pet, Task, Scheduler, Priority

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ── Session state: initialize once, reuse on every rerun ──────────────────────
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

# ── Sidebar: Manage Pets ──────────────────────────────────────────────────────
with st.sidebar:
    st.header("Manage Pets")
    new_pet_name = st.text_input("Pet Name", placeholder="e.g. Mochi")
    new_species  = st.selectbox("Species", ["Dog", "Cat", "Bird", "Other"])
    new_breed    = st.text_input("Breed", placeholder="e.g. Shiba Inu")
    new_dob      = st.date_input("Date of Birth", value=date(2021, 1, 1))

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

# ── Main: Schedule a Task ─────────────────────────────────────────────────────
st.subheader("Schedule a Task")

if not owner.pets:
    st.info("👈 Add a pet in the sidebar first!")
else:
    selected_pet_name = st.selectbox("Select Pet", options=[p.name for p in owner.pets])
    selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)

    col1, col2 = st.columns([2, 1])
    with col1:
        task_title = st.text_input("Task Title", placeholder="e.g. Morning Walk")
        task_desc  = st.text_area("Description", placeholder="Details...", height=80)
        task_cat   = st.selectbox(
            "Category", ["Exercise", "Medication", "Health", "Feeding", "Grooming", "Other"]
        )
        frequency  = st.selectbox(
            "Repeat",
            ["None (one-time)", "Daily", "Weekly"],
            help="Recurring tasks auto-schedule the next occurrence when marked complete.",
        )
    with col2:
        task_date      = st.date_input("Due Date", value=date.today())
        task_time      = st.time_input("Due Time", value=time(9, 0))
        priority_label = st.select_slider(
            "Priority", options=["LOW", "MEDIUM", "HIGH"], value="MEDIUM"
        )

    if st.button("Add Task", type="primary"):
        if task_title.strip():
            freq_value = {"None (one-time)": None, "Daily": "daily", "Weekly": "weekly"}[frequency]
            task = Task(
                id=str(uuid.uuid4()),
                pet_id=selected_pet.id,
                title=task_title.strip(),
                description=task_desc.strip(),
                due_date=datetime.combine(task_date, task_time),
                category=task_cat,
                is_completed=False,
                priority=Priority[priority_label],
                frequency=freq_value,
            )
            selected_pet.add_task(task)
            scheduler._rebuild_cache()
            st.toast(f"Task added for {selected_pet_name}!")
        else:
            st.error("Please enter a task title.")

# ── Main: Today's Schedule ────────────────────────────────────────────────────
st.divider()
st.subheader("Today's Schedule")

pet_lookup = {p.id: p for p in owner.pets}

# Conflict warnings — shown BEFORE the task list so they can't be missed
conflicts = scheduler.get_conflicts(scheduler.get_upcoming_tasks(days=1))
if conflicts:
    for conflict in conflicts:
        # Format: "[CONFLICT] YYYY-MM-DD HH:MM — 'A' (Pet1) vs 'B' (Pet2)"
        _, rest      = conflict.split("] ", 1)
        time_part, tasks_part = rest.split(" — ", 1)
        st.warning(
            f"**Scheduling conflict at {time_part}**  \n"
            f"{tasks_part}  \n"
            f"Consider rescheduling one of these tasks to avoid overlap.",
            icon="⚠️",
        )

# Filter controls
filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    pet_filter = st.selectbox(
        "Filter by pet",
        ["All pets"] + [p.name for p in owner.pets],
        key="pet_filter",
    )
with filter_col2:
    status_filter = st.selectbox(
        "Filter by status", ["Incomplete", "Completed", "All"], key="status_filter"
    )

# Apply filters and sort by time-of-day using Scheduler methods
display_tasks = scheduler.sort_by_time(scheduler.get_all_tasks())

if pet_filter != "All pets":
    display_tasks = scheduler.filter_by_pet_name(display_tasks, pet_filter)

if status_filter == "Incomplete":
    display_tasks = scheduler.filter_by_completion(display_tasks, is_completed=False)
elif status_filter == "Completed":
    display_tasks = scheduler.filter_by_completion(display_tasks, is_completed=True)

# Task cards
priority_color = {Priority.HIGH: "🔴", Priority.MEDIUM: "🟡", Priority.LOW: "🟢"}
freq_badge     = {"daily": "🔁 Daily", "weekly": "🔁 Weekly", None: ""}

if not display_tasks:
    st.info("No tasks match the current filters.")
else:
    for task in display_tasks:
        pet      = pet_lookup.get(task.pet_id)
        pet_name = pet.name if pet else "Unknown"
        time_str = task.due_date.strftime("%I:%M %p")
        date_str = task.due_date.strftime("%a %b %d")

        with st.container(border=True):
            header_col, badge_col = st.columns([5, 1])
            with header_col:
                title_text = f"~~**{task.title}**~~" if task.is_completed else f"**{task.title}**"
                st.markdown(f"{title_text} — {pet_name}")
            with badge_col:
                st.markdown(f"{priority_color[task.priority]} {task.priority.name}")

            meta1, meta2, meta3 = st.columns(3)
            meta1.caption(f"🕐 {date_str} · {time_str}")
            meta2.caption(f"📂 {task.category}")
            if task.frequency:
                meta3.caption(freq_badge[task.frequency])

            if task.description:
                st.caption(f"📝 {task.description}")

            if task.is_completed:
                completed_str = (
                    task.completed_at.strftime("%b %d at %I:%M %p")
                    if task.completed_at else "earlier"
                )
                st.success(f"Completed {completed_str}", icon="✅")
            else:
                if st.button("Mark Complete", key=f"complete_{task.id}"):
                    next_task = scheduler.mark_task_complete(task.id)
                    if next_task:
                        next_str = next_task.due_date.strftime("%a %b %d at %I:%M %p")
                        st.toast(f"Next '{next_task.title}' scheduled for {next_str}", icon="🔁")
                    st.rerun()

# ── Expander: System state ────────────────────────────────────────────────────
with st.expander("System Data Status"):
    st.write(f"**Owner:** {owner.name} ({owner.email})")
    st.write(f"**Pets:** {[p.name for p in owner.pets]}")
    for pet in owner.pets:
        st.write(f"  • {pet.name}: {len(pet.tasks)} task(s)")
    st.write(f"**Scheduler cache:** {len(scheduler.get_all_tasks())} total task(s)")
