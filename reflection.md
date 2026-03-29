# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

In this project, a user should be able to enter information about themselves and their pet for the program to keep as user input. Users should also be able to add and/or modify tasks. Example of a task could be scheduling a morning walk for their pet at a specific time. Finally, users should also be able to view a chronological list of all pending tasks across all pets for the current day. 

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

For my main design, I think I want to include 4 classes: Owners, Pets, Tasks, and Scheduling. 
Owner will include: the name of the owner and a list of pets attached to that owner. Owners will be able to add_pet() and get_tasks(). 
Pets will include: name of pet, breed/species, list of tasks needed to be completed for pet. Pets will need tasks, so I will use add_task() and remove_task(). 
Tasks will include: description of task, time task must be completed at, frequence of the task, and whether or not it is completed. I can use, for example, task_complete() to determine whether it's finished or not. 
Finally, the scheduler will be responsible for sorting tasks, checking if there are any timing conflicts, and printing a chronological view of all tasks per pet. I can use sort_tasks(), check_times(), and daily_view() as methods for those. 

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes. I asked Claude to review my skeleton and asked if  it notices any missing relationships or potential logic bottlenecks. Here is what AI suggested: 
1. priority enum should be added to sort by priority of tasks 
2. Task.pet_id will re-associate a task with it's pet after flattening
3. remove_task and remove_pet should be bool so that callers can tell if the ID was actually found. 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
