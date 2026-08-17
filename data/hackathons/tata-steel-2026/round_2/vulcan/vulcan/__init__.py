"""VULCAN — agentic Maintenance Wizard for industrial steel equipment.

Product : VULCAN  (the diagnostic / RCA / RUL / planning engine)
Persona : EDITH   (the conversational voice the user talks to)
Brain   : Claude Max SUBSCRIPTION via claude_agent_sdk (OAuth token) — NO API key, ever.
          Falls through a keyless provider ladder to a deterministic template floor.

Built for the Tata Steel R2 hackathon (theme: Maintenance Wizard for Industrial
Equipment). CPU-only, free, offline-safe. Every LLM call has a deterministic
fallback so the demo never crashes.
"""

__product__ = "VULCAN"
__persona__ = "EDITH"
__version__ = "0.1.0"
__tagline__ = "Every Defect, Investigated, Triaged & Healed."  # EDITH

__all__ = ["__product__", "__persona__", "__version__", "__tagline__"]
