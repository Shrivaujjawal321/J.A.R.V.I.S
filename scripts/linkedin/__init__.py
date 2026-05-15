"""
Jarvis LinkedIn Pipeline.

Daily autonomous LinkedIn growth machine for Boss (Ujjawal).
Architecture:

    daily_runner (8am IST)
        |
        +--> icp_search.py     (find target profiles via LinkedIn search)
        +--> connection_drafter (personalize notes per profile)
        +--> message_drafter    (varied templates for 1st-degree)
        +--> post_generator     (1 post/day, rotating calendar)
        |
        +--> telegram_approval  (sends batch to Boss, waits)
        |
        +--> [Boss approves via Telegram]
        |
        +--> executor (10am IST)  (browser-autopilot drives Chrome to send)
        |
        +--> contacted.jsonl    (no-repeat enforcement)
        +--> state.json         (rolling counters)

    reporter (9pm IST)
        +--> Telegram nightly summary

All Tier-3 actions (send connection / send message / publish post) require Boss's
explicit approval via the Telegram morning batch flow. NEVER auto-submit.
"""

__version__ = "0.1.0"
