"""Fleek GTM / retention decision engine.

Pipeline: load -> clean -> dependency -> segments -> guardrails -> feature context
-> NBA -> execution plan -> run comparison / state.
All rules are transparent and vectorised (no per-account hard-coding).
"""
