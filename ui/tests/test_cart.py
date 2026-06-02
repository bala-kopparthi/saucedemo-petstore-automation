"""
Cart test suite — add/remove and navigation state (S2, R3, R5).

Scenarios covered:
    S2 | Add one product → cart badge increments to 1               [smoke]
    R3 | Add multiple, remove one from cart page, verify state      [regression]
    R5 | "Continue Shopping" returns to inventory, cart preserved   [regression]
"""

import pytest
from playwright.sync_api import Page, expect

from ui.data.products import BACKPACK, BIKE_LIGHT, BOLT_TSHIRT, SAMPLE_PRODUCTS
from ui.pages.cart_page import CartPage
from ui.pages.inventory_page import InventoryPage


# ── S2 ────────────────────────────────────────────────────────────────

@pytest.mark.smoke
@pytest.mark.ui
def test_add_single_product_increments_cart_badge(
    logged_in_inventory: InventoryPage,
) -> None:
    """S2: adding one product makes the cart badge show 1."""
    inventory = logged_in_inventory

    # Sanity: cart starts empty (badge absent → count 0)
    assert inventory.cart_badge_count() == 0, "Cart should start empty"

    # Act
    inventory.add_to_cart(BACKPACK)

    # Assert
    assert inventory.cart_badge_count() == 1, "Badge should read 1 after one add"


# ── R3 ────────────────────────────────────────────────────────────────

@pytest.mark.regression
@pytest.mark.ui
def test_remove_one_item_from_cart_updates_state(
    logged_in_inventory: InventoryPage, page: Page, base_url: str
) -> None:
    """R3: add three products, remove one on the cart page, verify survivors."""
    inventory = logged_in_inventory

    # Arrange: add all sample products from the inventory page
    for product in SAMPLE_PRODUCTS:
        inventory.add_to_cart(product)
    assert inventory.cart_badge_count() == len(SAMPLE_PRODUCTS)  # 3

    # Act: go to the cart and remove the middle item
    inventory.open_cart()
    cart = CartPage(page, base_url)
    # to_have_url auto-waits for navigation — doubles as a sync point + assert
    expect(page).to_have_url(f"{base_url}/cart.html")
    assert cart.items_count() == 3

    cart.remove_item(BIKE_LIGHT)

    # Assert final state: 2 remain, removed one gone, others preserved
    assert cart.items_count() == 2
    assert not cart.contains(BIKE_LIGHT), "Removed item should be gone"
    assert cart.contains(BACKPACK)
    assert cart.contains(BOLT_TSHIRT)


# ── R5 ────────────────────────────────────────────────────────────────

@pytest.mark.regression
@pytest.mark.ui
def test_continue_shopping_returns_to_inventory_preserving_cart(
    logged_in_inventory: InventoryPage, page: Page, base_url: str
) -> None:
    """R5: 'Continue Shopping' returns to inventory with cart intact."""
    inventory = logged_in_inventory

    # Arrange: add two products
    inventory.add_to_cart(BACKPACK)
    inventory.add_to_cart(BIKE_LIGHT)
    assert inventory.cart_badge_count() == 2

    # Go to cart, confirm both are there
    inventory.open_cart()
    cart = CartPage(page, base_url)
    assert cart.items_count() == 2

    # Act: Continue Shopping → back to inventory
    cart.continue_shopping()
    expect(page).to_have_url(f"{base_url}/inventory.html")

    # Assert: cart state survived the round-trip
    assert inventory.cart_badge_count() == 2, "Cart should still hold 2 items"
    