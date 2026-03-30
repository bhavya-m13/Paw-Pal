# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

### Pet & Owner Management
- **Add / remove pets** — Register multiple pets under one owner; each pet maintains its own independent task list.
- **Per-pet task lists** — Tasks are stored on the `Pet` object and referenced by `pet_id`, keeping ownership explicit even after the scheduler flattens everything into a single cache.

### Task Scheduling
- **One-time tasks** — Schedule any care activity (walk, feeding, medication, grooming, etc.) with a title, category, due date/time, and priority level.
- **Priority levels** — Every task carries a `LOW / MEDIUM / HIGH` priority (backed by a `Priority` enum) so high-urgency care is never buried in the list.

### Sorting Algorithms
- **Sort by time-of-day** — `sort_by_time()` extracts the `HH:MM` portion of each task's `due_date` and sorts ascending using zero-padded 24-hour strings, producing a clean chronological view of the day regardless of what date each task falls on.
- **Sort by due date** — `sort_by_due_date()` sorts by the full `datetime`, useful when displaying tasks across multiple days.
- **Sort by priority** — `sort_by_priority()` orders tasks from `HIGH` → `LOW` so the most urgent items always surface first.

### Filtering
- **Filter by pet name** — `filter_by_pet_name()` resolves the name to a set of pet IDs first (case-insensitive), then filters in O(1) per task — no repeated string comparisons across a growing list.
- **Filter by completion status** — `filter_by_completion()` isolates either pending or finished tasks, powering the Incomplete / Completed / All toggle in the UI.
- **Filter by category** — `filter_by_category()` narrows results to a single care type (e.g., Medication only).

### Recurring Tasks
- **Daily recurrence** — Marking a daily task complete automatically clones it with `due_date + timedelta(days=1)`, preserving the original time-of-day slot.
- **Weekly recurrence** — Same mechanism with `due_date + timedelta(weeks=1)`.
- **Infinite chaining** — Each generated task inherits `frequency`, so the chain continues indefinitely without manual re-entry.

### Conflict Detection
- **Duplicate-time warnings** — `get_conflicts()` groups tasks into `YYYY-MM-DD HH:MM` buckets. Any bucket with two or more tasks generates a human-readable warning: `[CONFLICT] 2026-04-01 08:00 — 'Morning Walk' (Buddy) vs 'Morning Feed' (Luna)`. Works across pets. Never raises an exception or blocks scheduling — it only reports.

### Internal Cache
- **Flat task cache** — `Scheduler` maintains a `_task_cache` list rebuilt after every add, remove, or completion. All read methods query the cache instead of traversing the owner → pet → task hierarchy on every call, keeping reads fast while writes stay correct.

---

## Smarter Scheduling

The `Scheduler` class has been extended with four new features beyond basic task listing:

**Time-of-day sorting** — `sort_by_time(tasks)` orders tasks by their `HH:MM` value extracted from `due_date`, letting you display a pet's day in chronological order regardless of the order tasks were added.

**Pet name filtering** — `filter_by_pet_name(tasks, pet_name)` returns only the tasks that belong to a named pet (case-insensitive). Internally it resolves the name to a set of pet IDs first, so the filter itself is O(1) per task.

**Recurring tasks** — Each `Task` now has an optional `frequency` field (`"daily"`, `"weekly"`, or `None`). Calling `scheduler.mark_task_complete(task_id)` marks the task done and, for recurring tasks, automatically creates the next occurrence using Python's `timedelta`:
- `"daily"` → `due_date + timedelta(days=1)`
- `"weekly"` → `due_date + timedelta(weeks=1)`

The new task is added to the same pet and the internal cache is rebuilt immediately.

**Conflict detection** — `get_conflicts(tasks)` scans a list of tasks for any that share an exact `YYYY-MM-DD HH:MM` timestamp. It works across pets and returns a plain list of warning strings — it never raises or blocks scheduling. Example output:

```
[CONFLICT] 2026-03-30 08:00 — 'Morning Walk' (Buddy) vs 'Morning Feeding' (Luna)
```

## Testing PawPal+

### Running the tests

```bash
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

The suite contains **23 tests** across 5 classes:

| Class | What is verified |
|---|---|
| `TestTaskCompletion` | `mark_complete()` sets `is_completed` and records `completed_at`; incomplete tasks have no timestamp |
| `TestTaskAddition` | Adding tasks increases the count and makes them retrievable via `get_tasks()` |
| `TestSortByTime` | Tasks are returned in chronological HH:MM order; empty lists and single-task lists are handled; sort is stable across equal times |
| `TestRecurrenceLogic` | Daily/weekly tasks auto-create the next occurrence on completion; the cloned task inherits `frequency`; chaining works across 3+ completions; one-time tasks return `None`; missing IDs return `None` |
| `TestConflictDetection` | Two or more tasks at the exact same timestamp are flagged; the warning contains all task titles and the timestamp; tasks at different times produce no conflicts; empty input returns an empty list |

### Confidence Level

**4 / 5 stars**

The core domain logic — task completion, recurring scheduling, time-of-day sorting, and conflict detection — is fully exercised and all 23 tests pass. One star is withheld because the UI layer (`app.py`) and Streamlit session-state interactions are not covered by automated tests, so regressions there would only surface manually.

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Demo
<a href="course_images/ai110/pawpal+.png" target="_blank">
    <img src='course_images/ai110/pawpal+.png' title='PawPal App' width='600' alt='PawPal App' class='center-block' />
</a>

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
