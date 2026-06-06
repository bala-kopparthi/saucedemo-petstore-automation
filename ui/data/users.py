"""
Test user constants for SauceDemo.

SauceDemo's credentials are publicly displayed on their login page,
so these are not real secrets. We still source the password from .env
to demonstrate the pattern of externalising credentials from test code.
"""

import os

# ── Password ───────────────
# All SauceDemo users share the same password.

SAUCE_PASSWORD: str = os.getenv("SAUCEDEMO_VALID_PASSWORD", "secret_sauce")

# ── User types ─────────────
STANDARD_USER = "standard_user"
LOCKED_OUT_USER = "locked_out_user"
PROBLEM_USER = "problem_user"
PERFORMANCE_GLITCH_USER = "performance_glitch_user"
ERROR_USER = "error_user"
VISUAL_USER = "visual_user"

# ── Users that should reach inventory on login (for P1 parametrize) ───
VALID_USERS = [
    STANDARD_USER,
    PROBLEM_USER,
    PERFORMANCE_GLITCH_USER,
    VISUAL_USER,
]
