"""
Login test suite — authentication and session flows.

Scenarios covered:
    S1 | standard_user login lands on inventory with 6 products  [smoke]
    S4 | Logout via hamburger returns user to login page          [smoke]
    N1 | Empty credentials → 'Username is required' error         [negative]
    N2 | locked_out_user → account locked error                   [negative]
    P1 | 4 valid user types all reach inventory                   [regression]
    P2 | performance_glitch_user: inventory loads under 10s       [regression]
"""

import time

import pytest
from playwright.sync_api import Page, expect

from ui.data.users import (
    LOCKED_OUT_USER,
    PERFORMANCE_GLITCH_USER,
    PROBLEM_USER,
    SAUCE_PASSWORD,
    STANDARD_USER,
    VALID_USERS,
    VISUAL_USER,
)
from ui.pages.inventory_page import InventoryPage
from ui.pages.login_page import LoginPage


# ── S1 ────────────────────────────────────────────────────────────────

@pytest.mark.smoke
@pytest.mark.ui
def test_standard_user_login_lands_on_inventory(
    page: Page, base_url: str, saucedemo_credentials: dict
) -> None:
    """S1: valid login navigates to /inventory.html with 6 products."""
    # Arrange
    login_page = LoginPage(page, base_url)
    login_page.navigate()

    # Act
    login_page.login(
        saucedemo_credentials["username"],
        saucedemo_credentials["password"],
    )

    # Assert: URL changed to inventory
    expect(page).to_have_url(f"{base_url}/inventory.html")

    # Assert: all 6 products are rendered
    # Using plain `assert` here because products_count() returns a Python int —
    # expect() is for Playwright Locators, assert is for computed Python values.
    inventory = InventoryPage(page, base_url)
    assert inventory.products_count() == 6, (
        f"Expected 6 products, found {inventory.products_count()}"
    )


# ── S4 ────────────────────────────────────────────────────────────────

@pytest.mark.smoke
@pytest.mark.ui
def test_logout_returns_to_login_page(
    page: Page, base_url: str, saucedemo_credentials: dict
) -> None:
    """S4: hamburger menu → Logout → user lands back on login page."""
    # Arrange: reach the inventory page first
    login_page = LoginPage(page, base_url)
    login_page.navigate()
    login_page.login(
        saucedemo_credentials["username"],
        saucedemo_credentials["password"],
    )

    # Act: open menu, click logout
    inventory = InventoryPage(page, base_url)
    inventory.logout()

    # Assert: back on root URL and the login button is visible
    expect(page).to_have_url(f"{base_url}/")
    expect(login_page.login_button).to_be_visible()


# ── N1 ────────────────────────────────────────────────────────────────

@pytest.mark.negative
@pytest.mark.ui
def test_empty_credentials_shows_username_required_error(
    page: Page, base_url: str
) -> None:
    """N1: submitting empty form → 'Username is required' error banner."""
    login_page = LoginPage(page, base_url)
    login_page.navigate()

    # Act: submit with both fields empty
    login_page.login("", "")

    # Assert: error is visible and contains the expected message
    assert login_page.is_error_visible(), "Error banner should be visible"
    assert "Username is required" in login_page.error_text(), (
        f"Unexpected error text: '{login_page.error_text()}'"
    )


# ── N2 ────────────────────────────────────────────────────────────────

@pytest.mark.negative
@pytest.mark.ui
def test_locked_out_user_sees_lockout_error(page: Page, base_url: str) -> None:
    """N2: locked_out_user credentials → account locked error message."""
    login_page = LoginPage(page, base_url)
    login_page.navigate()
    login_page.login(LOCKED_OUT_USER, SAUCE_PASSWORD)

    assert login_page.is_error_visible(), "Error banner should be visible"
    # Case-insensitive check — 'locked out' appears in the message
    assert "locked out" in login_page.error_text().lower(), (
        f"Unexpected error text: '{login_page.error_text()}'"
    )


# ── P1 ────────────────────────────────────────────────────────────────

@pytest.mark.regression
@pytest.mark.parametrize_users
@pytest.mark.ui
@pytest.mark.parametrize("username", VALID_USERS)
def test_valid_user_types_reach_inventory(
    page: Page, base_url: str, username: str
) -> None:
    """P1: standard_user, problem_user, performance_glitch_user, visual_user
    all successfully log in and reach inventory.

    @pytest.mark.parametrize runs this function once per entry in VALID_USERS.
    You will see 4 test entries in the output: test_valid_user...[standard_user],
    [...problem_user], etc.
    """
    login_page = LoginPage(page, base_url)
    login_page.navigate()
    login_page.login(username, SAUCE_PASSWORD)

    # All valid user types should land on inventory — no locked-out error
    expect(page).to_have_url(f"{base_url}/inventory.html")


# ── P2 ────────────────────────────────────────────────────────────────

@pytest.mark.regression
@pytest.mark.ui
def test_performance_glitch_user_loads_inventory_within_limit(
    page: Page, base_url: str
) -> None:
    """P2: performance_glitch_user — inventory page should load within 10s.

    SauceDemo intentionally adds ~5s latency for this user to simulate a
    sluggish backend. We verify it still completes within a generous limit.

    Note: uses wall-clock timing with time.time() — this is a soft
    upper-bound check, not a substitute for real perf tooling (Lighthouse/k6).
    """
    login_page = LoginPage(page, base_url)
    login_page.navigate()

    start = time.time()
    login_page.login(PERFORMANCE_GLITCH_USER, SAUCE_PASSWORD)

    # Wait until inventory URL is confirmed (page fully navigated)
    expect(page).to_have_url(f"{base_url}/inventory.html")
    elapsed = time.time() - start

    assert elapsed < 10, (
        f"Inventory took {elapsed:.2f}s to load for performance_glitch_user "
        f"(limit: 10s)"
    )
    