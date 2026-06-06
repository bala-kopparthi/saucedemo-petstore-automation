"""
Checkout test suite — validation, known defect, and summary math.

Scenarios covered:
    N3 | Checkout step 1 empty fields → per-field required errors    [negative]
    N4 | error_user Last Name field rejects keyboard input (xfail)   [negative]
    R4 | Summary math: item subtotal + tax == grand total            [regression]
"""

import pytest
import allure
from playwright.sync_api import Page, expect

from ui.data.products import BACKPACK, SAMPLE_PRODUCTS
from ui.data.users import ERROR_USER, SAUCE_PASSWORD
from ui.pages.cart_page import CartPage
from ui.pages.checkout_step_one_page import CheckoutStepOnePage
from ui.pages.checkout_step_two_page import CheckoutStepTwoPage
from ui.pages.inventory_page import InventoryPage
from ui.pages.login_page import LoginPage


# ── N3 ────────────────────────────────────────────────────────────────

@pytest.mark.negative
@pytest.mark.ui
def test_checkout_step_one_empty_fields_show_validation_errors(
    logged_in_inventory: InventoryPage, page: Page, base_url: str
) -> None:
    """N3: SauceDemo validates required fields one at a time, in order."""
    # Arrange: reach checkout step one with one item in the cart
    inventory = logged_in_inventory
    inventory.add_to_cart(BACKPACK)
    inventory.open_cart()

    cart = CartPage(page, base_url)
    cart.checkout()

    step_one = CheckoutStepOnePage(page, base_url)
    expect(page).to_have_url(f"{base_url}/checkout-step-one.html")

    # 1) all empty → First Name required
    step_one.fill_information("", "", "")
    step_one.continue_checkout()
    assert step_one.is_error_visible(), "Error banner should appear"
    assert "First Name is required" in step_one.error_text()

    # 2) first name filled → Last Name required
    step_one.fill_information("Bala", "", "")
    step_one.continue_checkout()
    assert "Last Name is required" in step_one.error_text()

    # 3) first + last filled → Postal Code required
    step_one.fill_information("Bala", "Kopparthi", "")
    step_one.continue_checkout()
    assert "Postal Code is required" in step_one.error_text()


# ── N4 ────────────────────────────────────────────────────────────────
@allure.feature("Checkout")
@allure.story("Known defect — error_user Last Name field")
@allure.severity(allure.severity_level.MINOR)
@allure.label("defect_type", "known / tracked")
@allure.description(
    "For `error_user`, the Last Name field on Checkout Step One rejects keyboard input "
    "This is the expected test. The day SauceDemo fixes the bug, the test will XPASS, which is our signal to remove the xfail marker and promote it to a normal passing test."
)
@pytest.mark.negative
@pytest.mark.ui
@pytest.mark.xfail(reason="error_user: Last Name field rejects keyboard input")

def test_error_user_can_type_last_name_at_checkout(
    page: Page, base_url: str
) -> None:
    """N4: error_user SHOULD be able to type a last name (positive intent).
    If SauceDemo fixes it, this flips to XPASS — the signal to remove the xfail marker.
    """
    # Arrange: log in as error_user (not the standard fixture) → checkout step 1
    login = LoginPage(page, base_url)
    login.navigate()
    login.login(ERROR_USER, SAUCE_PASSWORD)

    inventory = InventoryPage(page, base_url)
    inventory.add_to_cart(BACKPACK)
    inventory.open_cart()

    cart = CartPage(page, base_url)
    cart.checkout()

    step_one = CheckoutStepOnePage(page, base_url)
    expect(page).to_have_url(f"{base_url}/checkout-step-one.html")

    # Act: simulate REAL keystrokes (char-by-char) — this triggers the defect,
    # whereas .fill() would set the value programmatically and may bypass it.
    step_one.last_name_input.press_sequentially("Kopparthi")

    # Assert the CORRECT behavior. On the live site the field stays empty for
    # error_user → assertion fails → XFAIL.
    assert step_one.last_name_input.input_value() == "Kopparthi", (
        "Last Name field should accept keyboard input"
    )


# ── R4 ────────────────────────────────────────────────────────────────

@pytest.mark.regression
@pytest.mark.ui
def test_checkout_summary_math_is_correct(
    logged_in_inventory: InventoryPage, page: Page, base_url: str
) -> None:
    """R4: on the overview page, item subtotal + tax must equal grand total."""
    # Arrange: add a few items and proceed to the summary page
    inventory = logged_in_inventory
    for product in SAMPLE_PRODUCTS:
        inventory.add_to_cart(product)
    inventory.open_cart()

    cart = CartPage(page, base_url)
    cart.checkout()

    step_one = CheckoutStepOnePage(page, base_url)
    step_one.fill_information("Bala", "Kopparthi", "560001")
    step_one.continue_checkout()

    step_two = CheckoutStepTwoPage(page, base_url)
    expect(page).to_have_url(f"{base_url}/checkout-step-two.html")

    # Act: read the three money values (page object parses "$X.XX" → float)
    subtotal = step_two.item_subtotal()
    tax = step_two.tax()
    grand_total = step_two.grand_total()

    # Assert: round to 2 dp to avoid floating-point noise (0.1 + 0.2 != 0.3)
    assert round(subtotal + tax, 2) == round(grand_total, 2), (
        f"Math mismatch: subtotal {subtotal} + tax {tax} != total {grand_total}"
    )

