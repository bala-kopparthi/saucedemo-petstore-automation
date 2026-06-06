"""
CheckoutStepTwoPage — Page Object for SauceDemo's order summary screen.

URL: {base_url}/checkout-step-two.html

Tests that use this: S3 (happy path), R4 (item total + tax == grand total math)
"""

from playwright.sync_api import Page, Locator

from ui.pages.base_page import BasePage


class CheckoutStepTwoPage(BasePage):
    """Second step of checkout — review order, see totals, finish or cancel."""

    URL_PATH = "/checkout-step-two.html"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)

        # --- Cart item list (same selectors as CartPage) ---
        self.cart_items: Locator = page.locator(".cart_item")
        self.cart_item_names: Locator = page.locator(".cart_item .inventory_item_name")

        # --- Currency labels ---
        self.item_total_label: Locator = page.locator(".summary_subtotal_label")
        self.tax_label: Locator = page.locator(".summary_tax_label")
        self.grand_total_label: Locator = page.locator(".summary_total_label")

        # --- Buttons ---
        self.finish_button: Locator = page.locator('[data-test="finish"]')
        self.cancel_button: Locator = page.locator('[data-test="cancel"]')

    # Helpers (private)

    @staticmethod
    def _extract_amount(text: str) -> float:
        """Pull the dollar value out of strings like 'Tax: $2.40' -> 2.40."""

    # Read helpers

    def items_count(self) -> int:
        """Number of cart items being reviewed."""
        return self.cart_items.count()

    def item_names(self) -> list[str]:
        """Display names of items being purchased, in display order."""
        return self.cart_item_names.all_inner_texts()

    def item_subtotal(self) -> float:
        """Pre-tax line-item total (e.g., 29.99)."""
        return self._extract_amount(self.item_total_label.inner_text())

    def tax(self) -> float:
        """Tax amount (e.g., 2.40)."""
        return self._extract_amount(self.tax_label.inner_text())

    def grand_total(self) -> float:
        """Final total shown to the customer (e.g., 32.39)."""
        return self._extract_amount(self.grand_total_label.inner_text())

    # Actions

    def finish(self) -> None:
        """Place the order — advances to the confirmation page."""
        self.finish_button.click()

    def cancel(self) -> None:
        """Abandon checkout — returns to the inventory page."""
        self.cancel_button.click()
