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

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
