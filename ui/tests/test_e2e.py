"""
End-to-end test — the revenue-critical happy path (S3).

Scenario covered:
    S3 | login → add to cart → checkout → finish → order confirmed  [smoke, e2e]
"""

import pytest
from playwright.sync_api import Page, expect

from ui.data.products import BACKPACK
from ui.pages.cart_page import CartPage
from ui.pages.checkout_complete_page import CheckoutCompletePage
from ui.pages.checkout_step_one_page import CheckoutStepOnePage
from ui.pages.checkout_step_two_page import CheckoutStepTwoPage
from ui.pages.inventory_page import InventoryPage


@pytest.mark.smoke
@pytest.mark.e2e
@pytest.mark.ui
def test_full_checkout_happy_path(
    logged_in_inventory: InventoryPage, page: Page, base_url: str
) -> None:
    """S3: complete a purchase from inventory through order confirmation."""
    # 1) Add a product from inventory
    inventory = logged_in_inventory
    inventory.add_to_cart(BACKPACK)
    assert inventory.cart_badge_count() == 1

    # 2) Open the cart and confirm the item is there
    inventory.open_cart()
    cart = CartPage(page, base_url)
    assert cart.contains(BACKPACK)
    cart.checkout()

    # 3) Fill checkout information
    step_one = CheckoutStepOnePage(page, base_url)
    step_one.fill_information("Bala", "Kopparthi", "560001")
    step_one.continue_checkout()

    # 4) Review the overview and finish
    step_two = CheckoutStepTwoPage(page, base_url)
    expect(page).to_have_url(f"{base_url}/checkout-step-two.html")
    assert step_two.items_count() == 1
    step_two.finish()

    # 5) Assert the order-complete confirmation
    complete = CheckoutCompletePage(page, base_url)
    expect(page).to_have_url(f"{base_url}/checkout-complete.html")
    assert complete.is_order_complete(), "Order confirmation heading not shown"
    