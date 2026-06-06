"""
CartPage — Page Object for the SauceDemo shopping cart.

URL: {base_url}/cart.html

Tests that uses this: S2, S3, R3, R5
"""

from playwright.sync_api import Page, Locator

from ui.pages.base_page import BasePage


class CartPage(BasePage):
    """Encapsulates locators and actions for the SauceDemo cart page."""

    URL_PATH = "/cart.html"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)

        # --- Cart items ---
        # Each row has class .cart_item; we read names from the same

        self.cart_items: Locator = page.locator(".cart_item")
        self.cart_item_names: Locator = page.locator(".cart_item .inventory_item_name")

        # --- Footer buttons ---
        self.continue_shopping_button: Locator = page.locator('[data-test="continue-shopping"]')
        self.checkout_button: Locator = page.locator('[data-test="checkout"]')

    # Read helpers

    def items_count(self) -> int:
        """How many cart_item rows are rendered (0 when cart is empty)."""
        return self.cart_items.count()

    def item_names(self) -> list[str]:
        """Display names of items currently in the cart, in display order."""
        return self.cart_item_names.all_inner_texts()

    def contains(self, product_name: str) -> bool:
        """True if a product with the given display name is in the cart."""
        return product_name in self.item_names()

    # Actions

    def remove_item(self, product_name: str) -> None:
        """Click the Remove button for the named product on the cart row."""
        # SauceDemo uses the same data-test slug as the inventory page,
        slug = product_name.lower().replace(" ", "-")
        self.page.locator(f'[data-test="remove-{slug}"]').click()

    def continue_shopping(self) -> None:
        """Return to the inventory page (cart state is preserved)."""
        self.continue_shopping_button.click()

    def checkout(self) -> None:
        """Proceed to checkout step one (the customer info form)."""
        self.checkout_button.click()
