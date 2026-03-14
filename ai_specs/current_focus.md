# Current Focus — Updated 2026-03-13

## Active Work
- **Local coding agent integration** — Claude Code CLI + LM Studio (Qwen 3.5 9B) for offline code tasks
- **Developer dashboard** — double-click cube to see real-time system status, action log, session state
- **Folder-as-architecture** — implementing ai_docs/, ai_specs/, ai_toolkit/ structure

## Recently Completed
- Added `code_task` intent (intent #26) with full routing
- Fixed `self_improver.py` to use LM Studio instead of Anthropic API for subagent calls
- Added progress ticker to code_agent.py (shows elapsed time in terminal)
- Created developer dashboard in ui.py (system status, action log, session state, self-assessment)
- Increased subprocess timeouts from 120s to 300s

## Known Issues
- Code agent may still time out on complex tasks with Qwen 3.5 9B (300s limit)
- `manage_files` intent referenced in feedback log but no matching action module exists
- `chat` intent sometimes slow (>10s) on first call after boot

## Next Up
- Test the full code_task pipeline end-to-end with LM Studio
- Validate developer dashboard data accuracy
- Consider streaming output from local model instead of waiting for full response
