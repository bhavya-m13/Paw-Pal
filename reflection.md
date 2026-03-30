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
There are three primary constraints that my scheduler considers: Chronological time, task priority(high, low, medium), and duration based availability. In determining which constraints mattered most, I decided that in a pet care context, the human owner should get ultimate decision making power. I chose to make Time the most significant constraint because biological needs, like feeding and bathroom breaks, are time-sensitive. Next, I chose priority so that if a schedule becomes overbooked, the most important care tasks are completed first.


**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
The algorithmic method that Claude suggested fixing is mark_task_complete() in paw_pal_system.py lines 128-171. The problem was that the nested break command didn't actually break all three featured loops. After finding the match, Python exits the task loop but continues iterating every remaining pet and owner. For a small pet list this is harmless, but it's a logic bug that scales poorly and reads incorrectly. The code looks like it stops early and it looks incomplete. The fix for this is, as suggested by AI, was to use python's next() command with a generator expression to short circuit the exact point in time where the first match is found across all three loops. This tradeoff is reasonable because it makes sure there are no wasted iterations and the intent is expressed directly. 

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
I used Claude to help me with brainstorming logic, specifically for pawpal_system.py. I used AI to brainstorm ideas for how  to structure the Task and Pet objects so they’d interact with each other. AI also helped me debug and troubleshoot. The most helpful prompts for me included: 
- How do I use st.session_state to make sure my Owner object doesn't reset every time the UI reruns? 
- Can you refactor my pytest cases? 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
There was a specific moment where I did not accept an AI suggestion as-is, but I thought it needed some tweaking. When I was implementing the recurring task logic, the AI suggested using a complex  external task-scheduler library. I believe that this would be too complicated, and I also didn't know how to use this at all. Instead, I worked with the AI to build a custom mark_task_complete method inside my Scheduler. I wrote it so that the moment a task is marked as done, the code manually calculates the next date (using timedelta) and injects a new task object into the system. I verified my manual recurrence logic by having the AI write a simulation script with out of order tasks. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
I focused my testing on chronological sorting, multi-pet conflict detection, and automated recurrence. I specifically tested if the scheduler could take tasks added out of order, if it could handle overlapping conflicts, and if the system automatically generated the next correct occurrence in the future. These tests were critical because a pet care app is only useful if it's reliable. If the sorting failed, an owner might miss a morning feeding. If the recurrence logic didn't work, the owner would have to manually re-enter the same tasks every single day, which defeats the purpose of having an app to help you out. 
**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?
I’m very confident that my scheduler works correctly because my test script successfully handled the 'out of order' inputs and the date math for recurring tasks. AI created 23 specific test cases, and my scheduler passed all of them. If I had more time, I’d want to test Leap Years and Daylight Savings transitions to make sure the timedelta math doesn't shift the pet's schedule by an hour or a day incorrectly.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I am very satisfied with the way the final app works. No errors, every button, every slider, everything is running smoothly. Honestly, it's a really big win for me and it really helped me realize how amazing AI can be as a helper when used correctly. 

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
If I had another iteration, I’d redesign the Task Conflict Resolver. Right now, the scheduler just gives a warning in the UI, but it doesn't actually suggest a better time. I’d love to implement a Smart Re-scheduler that looks for the next available gap in the day and offers a button to Auto-Fix the overlap.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
The biggest takeaway for me was learning how to balance AI suggestions with my own architectural goals. It’s easy to let the AI write a complex solution for a simple problem, but I learned that it's important to trust your own instincts as well. 