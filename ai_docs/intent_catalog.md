# RUBE Intent Catalog

All 27 intents recognized by the system prompt (`core/prompt.txt`).
The LLM returns one of these as the `"intent"` key in its JSON response.

## Routing Reference

| # | Intent | Handler | Module | Parameters |
|---|--------|---------|--------|------------|
| 1 | `chat` | (inline in main.py) | — | none |
| 2 | `web_navigate` | `web_navigate()` | `open_app.py` | `url` |
| 3 | `system_launch` | `system_launch()` | `open_app.py` | `program_name` |
| 4 | `system_close` | `system_close()` | `open_app.py` | `program_name` |
| 5 | `system_control` | `system_control()` | `open_app.py` | `command` (minimize_all, volume_up, power_off_pc, etc.) |
| 6 | `broadcast_control` | `broadcast_control()` | `broadcast_control.py` | `action`, `target`, `state` |
| 7 | `whatsapp_message` | `send_whatsapp_message()` | `whatsapp.py` | `receiver_nickname`, `message_text`, `action`, `attachment_path` |
| 8 | `execute_shortcut` | `execute_shortcut()` | `keyboard_matrix.py` | `modifiers[]`, `key` |
| 9 | `search` | `web_search()` | `web_search.py` | `query` |
| 10 | `system_diagnostics` | `system_diagnostics()` | `system_status.py` | `check` (storage, memory, cpu, temperature) |
| 11 | `hardware_control` | `hardware_control()` | `system_status.py` | `action`, `device` |
| 12 | `vision_analysis` | `analyze_multimodal_view()` | `vision.py` | `target`, `prompt`, `file_path` |
| 13 | `facial_recognition` | `identity_scan_room()` | `face_recognizer.py` | none |
| 14 | `play_soundcloud` | `play_soundcloud()` | `open_app.py` | `category`, `query` |
| 15 | `register_api_key` | (inline in main.py) | — | `service_name` |
| 16 | `generate_social_post` | `generate_social_post()` | `social_manager.py` | `post_content`, `image_prompt`, `platform` |
| 17 | `email_message` | `send_email_message()` | `email_manager.py` | `receiver_email`, `subject`, `message_text`, `attachment_path` |
| 18 | `generate_analytics_report` | `generate_analytics_report()` | `analytics_manager.py` | `client_name` |
| 19 | `save_contact` | `save_contact()` | `contact_manager.py` | `contact_name`, `phone_number`, `email` |
| 20 | `import_contacts` | `import_contacts()` | `contact_manager.py` | `file_path` |
| 21 | `review_pending_edits` | `handle_review_pending()` | `self_improver.py` | none |
| 22 | `approve_edit` | `handle_approve()` | `self_improver.py` | `edit_id` |
| 23 | `reject_edit` | `handle_reject()` | `self_improver.py` | `edit_id` |
| 24 | `request_file_edit` | `handle_request_file_edit()` | `self_improver.py` | `file_path`, `reason` |
| 25 | `self_improve` | `handle_self_improve()` | `self_improver.py` | none |
| 26 | `code_task` | `handle_code_task()` | `code_agent.py` | `task`, `context` |
| 27 | `play_media` | `play_media()` | `open_app.py` | `media_name`, `platform` |

## Adding a New Intent

1. Add the intent definition to `core/prompt.txt` under AVAILABLE INTENTS
2. Create the handler function in the appropriate `actions/` module (or create a new module)
3. Import the handler in `main.py`
4. Add an `elif intent == "your_intent":` branch in the routing chain in `main.py`
5. If the intent needs preflight validation, add a check in `core/preflight.py`
