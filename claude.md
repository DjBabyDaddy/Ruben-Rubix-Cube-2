# Workflow Orchestration

## 1. Plan Mode Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately — don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed names upfront to reduce ambiguity

## 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution

## 3. Self-Improvement Loop
- After ANY interaction, check the file `tasks/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistakes
- Ruthlessly iterate on tasks/lessons between sessions, cut drops
- Review lessons at session start for relevant project

## 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff carefully between what you "made" and what actually changed
- Ask yourself: "Would a staff engineer approve this?"
- For tasks, use checklists and demonstrate correctness

## 5. Bounded Elegance (Balanced)
- For non-trivial changes: pause and ask "Is there a more elegant way?"
- If a fix feels hacky, re-implement the elegant solution from first principles
- Push this for simple, obvious fixes — don't over-engineer
- Challenge your own work before presenting it

## 6. Autonomous Bug Fixing
- If you find a bug, fix it — don't ask for hand-holding
- Point at logs, errors, failing tests — then resolve them
- Don't defer or ask permission to make required changes
- Do fix failing CI tests without being told how
