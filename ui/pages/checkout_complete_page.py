"""
CheckoutCompletePage — Page Object for SauceDemo's order confirmation screen.

URL: {base_url}/checkout-complete.html

Tests that use this: S3 (happy path) — the final "did we actually complete an order?" assertion
"""

from playwright.sync_api import Page, Locator

from ui.pages.base_page import BasePage


class CheckoutCompletePage(BasePage):
    """Final confirmation screen — 'Thank you for your order!'"""

    URL_PATH = "/checkout-complete.html"

    # The exact heading text SauceDemo displays on success. Stored as a
    # class constant so tests can import and compare against it without
    # duplicating the literal string.
    SUCCESS_HEADING_TEXT = "Thank you for your order!"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)

        # --- Confirmation elements ---
        self.confirmation_heading: Locator = page.locator(".complete-header")
        self.confirmation_text: Locator = page.locator(".complete-text")

        # --- Back to inventory button ---
        self.back_home_button: Locator = page.locator('[data-test="back-to-products"]')

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------

    def heading_text(self) -> str:
        """The big 'Thank you for your order!' heading text."""
        return self.confirmation_heading.inner_text()

    def is_order_complete(self) -> bool:
        """True if the success heading is on screen with expected text."""
        return (
            self.confirmation_heading.is_visible()
            and self.heading_text() == self.SUCCESS_HEADING_TEXT
        )

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def back_to_products(self) -> None:
        """Return user to the inventory page."""
        self.back_home_button.click()