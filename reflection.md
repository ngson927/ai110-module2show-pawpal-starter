# PawPal+ Project Reflection

## 1. System Design
My initial design for PawPal+ focused on the main user needs described in the scenario. I identified three core actions:

1. Enter and manage owner and pet information.
2. Add, edit, and prioritize pet care tasks.
3. Generate and view a daily care plan based on available time, task duration, and task priority.

The main classes in my design were Owner, Pet, Task, and Scheduler.

- Owner stores the owner's information, available time, and preferences.
- Pet stores the pet's basic information.
- Task stores each care activity with attributes such as duration, priority, category, and completion status.
- Scheduler is responsible for organizing tasks and generating a daily plan.


**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
My initial design for PawPal+ included four main classes: Owner, Pet, Task, and Scheduler.

- The Owner class stores information about the user, including their name, available time, and preferences for scheduling tasks.
- The Pet class represents the pet being cared for and stores basic information such as name, species, age, and notes.
- The Task class represents individual pet care activities such as feeding, walking, or grooming. Each task includes attributes like duration, priority, category, and completion status.
- The Scheduler class is responsible for managing tasks and generating a daily plan based on constraints such as available time and task priority.

These classes work together to model the system and support the core functionality of generating a daily pet care plan.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
After reviewing my class skeleton, I made small improvements to clarify the design.

I realized that several methods needed clear input parameters to be practical during implementation. For example, methods such as set_available_time(), update_preferences(), add_task(), edit_task(), and update_info() needed parameters so they could actually update or manage data. I also confirmed that the Scheduler should rely on the Owner's available_time when generating a daily plan.

In addition, I recognized that task priority needs a clearly defined meaning, such as using a consistent numeric range where higher numbers represent higher priority. These refinements made the design more complete and easier to implement later.
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
