from datetime import datetime
from pawpal_system import Owner, Pet, Task, Scheduler, Priority

# --- Setup ---

owner = Owner(
    id="o1",
    name="Jamie Rivera",
    email="jamie@example.com",
    phone="555-0100",
)

buddy = Pet(
    id="p1",
    owner_id="o1",
    name="Buddy",
    species="Dog",
    breed="Golden Retriever",
    birth_date=datetime(2020, 4, 10),
)

luna = Pet(
    id="p2",
    owner_id="o1",
    name="Luna",
    species="Cat",
    breed="Siamese",
    birth_date=datetime(2021, 8, 22),
)

owner.add_pet(buddy)
owner.add_pet(luna)

now = datetime.now()

# --- Intentional conflict: two tasks at the exact same time (08:00) ---
luna.add_task(Task(
    id="t5",
    pet_id="p2",
    title="Morning Feeding",
    description="Wet food breakfast",
    due_date=now.replace(hour=8, minute=0, second=0, microsecond=0),
    category="Feeding",
    is_completed=False,
    priority=Priority.HIGH,
    frequency="daily",
))

# --- Tasks added OUT OF ORDER, with frequency set on recurring ones ---

buddy.add_task(Task(
    id="t4",
    pet_id="p1",
    title="Evening Playtime",
    description="Interactive toy session",
    due_date=now.replace(hour=18, minute=0, second=0, microsecond=0),
    category="Exercise",
    is_completed=False,
    priority=Priority.LOW,
    frequency="daily",          # recurring every day
))

luna.add_task(Task(
    id="t3",
    pet_id="p2",
    title="Vet Checkup",
    description="Annual wellness exam at City Vet Clinic",
    due_date=now.replace(hour=14, minute=30, second=0, microsecond=0),
    category="Health",
    is_completed=False,
    priority=Priority.MEDIUM,
    frequency=None,             # one-time task
))

buddy.add_task(Task(
    id="t2",
    pet_id="p1",
    title="Flea Medicine",
    description="Apply monthly flea treatment",
    due_date=now.replace(hour=12, minute=0, second=0, microsecond=0),
    category="Medication",
    is_completed=False,
    priority=Priority.HIGH,
    frequency="weekly",         # recurring every week
))

buddy.add_task(Task(
    id="t1",
    pet_id="p1",
    title="Morning Walk",
    description="30-minute walk around the park",
    due_date=now.replace(hour=8, minute=0, second=0, microsecond=0),
    category="Exercise",
    is_completed=False,
    priority=Priority.HIGH,
    frequency="daily",          # recurring every day
))

# --- Scheduler ---

scheduler = Scheduler(owners=[owner])
pet_lookup = {pet.id: pet for pet in owner.get_pets()}


def print_tasks(tasks: list[Task], label: str) -> None:
    print(f"\n{'=' * 44}")
    print(f"  {label}")
    print(f"{'=' * 44}")
    if not tasks:
        print("  (none)")
        return
    for task in tasks:
        pet = pet_lookup.get(task.pet_id)
        pet_name = pet.name if pet else "Unknown"
        status = "[x]" if task.is_completed else "[ ]"
        time_str = task.due_date.strftime("%I:%M %p")
        date_str = task.due_date.strftime("%a %b %d")
        freq = f"  [{task.frequency}]" if task.frequency else ""
        print(f"\n  {status} {date_str} {time_str} — {task.title} ({pet_name}){freq}")
        print(f"       Category : {task.category}")
        print(f"       Priority : {task.priority.name}")


# 1. Conflict detection — run before anything else
all_tasks = scheduler.get_all_tasks()
conflicts = scheduler.get_conflicts(all_tasks)
print(f"\n{'=' * 44}")
print("  Conflict Detection")
print(f"{'=' * 44}")
if conflicts:
    for warning in conflicts:
        print(f"  {warning}")
else:
    print("  No conflicts found.")

# 2. Today's schedule (added out of order, now sorted by time)
print_tasks(scheduler.sort_by_time(all_tasks), f"Today's Schedule — {now.strftime('%A, %B %d %Y')}")

# 2. Mark "Morning Walk" complete → should auto-create tomorrow's occurrence
print("\n>>> Completing 'Morning Walk' (daily recurring)...")
next_walk = scheduler.mark_task_complete("t1")
if next_walk:
    print(f"    Next occurrence created: '{next_walk.title}' due {next_walk.due_date.strftime('%A %b %d at %I:%M %p')}")

# 3. Mark "Flea Medicine" complete → should auto-create next week's occurrence
print("\n>>> Completing 'Flea Medicine' (weekly recurring)...")
next_flea = scheduler.mark_task_complete("t2")
if next_flea:
    print(f"    Next occurrence created: '{next_flea.title}' due {next_flea.due_date.strftime('%A %b %d at %I:%M %p')}")

# 4. Mark "Vet Checkup" complete → no recurrence (one-time)
print("\n>>> Completing 'Vet Checkup' (one-time)...")
result = scheduler.mark_task_complete("t3")
print(f"    Next occurrence created: {result}")  # should print None

# 5. Full task list after completions — shows completed originals + new occurrences
all_tasks_after = scheduler.get_all_tasks()
print_tasks(scheduler.sort_by_due_date(all_tasks_after), "All Tasks After Completions (sorted by date)")

# 6. Incomplete tasks only — original completed ones filtered out
incomplete = scheduler.filter_by_completion(all_tasks_after, is_completed=False)
print_tasks(scheduler.sort_by_due_date(incomplete), "Incomplete Tasks Only")

# 7. Buddy's tasks only
buddy_tasks = scheduler.filter_by_pet_name(all_tasks_after, pet_name="Buddy")
print_tasks(scheduler.sort_by_due_date(buddy_tasks), "Buddy's Tasks Only")

print("\n" + "=" * 44)
