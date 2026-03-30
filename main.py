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

# --- Tasks ---

now = datetime.now()

buddy.add_task(Task(
    id="t1",
    pet_id="p1",
    title="Morning Walk",
    description="30-minute walk around the park",
    due_date=now.replace(hour=8, minute=0, second=0, microsecond=0),
    category="Exercise",
    is_completed=False,
    priority=Priority.HIGH,
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
))

luna.add_task(Task(
    id="t4",
    pet_id="p2",
    title="Evening Playtime",
    description="Interactive toy session",
    due_date=now.replace(hour=18, minute=0, second=0, microsecond=0),
    category="Exercise",
    is_completed=False,
    priority=Priority.LOW,
))

# --- Scheduler ---

scheduler = Scheduler(owners=[owner])

# --- Print Today's Schedule ---

print("=" * 40)
print(f"  PawPal+ — Today's Schedule")
print(f"  {now.strftime('%A, %B %d %Y')}")
print(f"  Owner: {owner.name}")
print("=" * 40)

todays_tasks = scheduler.sort_by_due_date(scheduler.get_upcoming_tasks(days=1))

if not todays_tasks:
    print("No upcoming tasks for today.")
else:
    pet_lookup = {pet.id: pet for pet in owner.get_pets()}

    for task in todays_tasks:
        pet = pet_lookup.get(task.pet_id)
        pet_name = pet.name if pet else "Unknown"
        status = "[x]" if task.is_completed else "[ ]"
        time_str = task.due_date.strftime("%I:%M %p")
        print(f"\n{status} {time_str} — {task.title} ({pet_name})")
        print(f"     Category : {task.category}")
        print(f"     Priority : {task.priority.name}")
        print(f"     Note     : {task.description}")

print("\n" + "=" * 40)
