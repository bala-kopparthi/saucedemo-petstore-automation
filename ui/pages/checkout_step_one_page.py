"""
CheckoutStepOnePage — Page Object for SauceDemo's customer information form.

URL: {base_url}/checkout-step-one.html

Tests that use this: S3 (happy path), N3 (empty-field validation), N4 (error_user bug)
"""

from playwright.sync_api import Page, Locator

from ui.pages.base_page import BasePage


class CheckoutStepOnePage(BasePage):
    """First step of checkout — collects customer name and ZIP."""

    URL_PATH = "/checkout-step-one.html"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)

        # --- Form fields ---
        # Exposed as public attributes so individual tests can call
        # .fill() or .input_value() directly when they need granular control
        self.first_name_input: Locator = page.locator('[data-test="firstName"]')
        self.last_name_input: Locator = page.locator('[data-test="lastName"]')
        self.postal_code_input: Locator = page.locator('[data-test="postalCode"]')

        # --- Buttons ---
        self.continue_button: Locator = page.locator('[data-test="continue"]')
        self.cancel_button: Locator = page.locator('[data-test="cancel"]')

        # --- Validation error banner ---
        # SauceDemo reuses [data-test="error"] across forms — same as login page.
        self.error_message: Locator = page.locator('[data-test="error"]')

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def fill_information(self, first_name: str, last_name: str, postal_code: str) -> None:
        """Fill all three form fields in one call. The convenience method
        used by the happy-path test S3."""
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.postal_code_input.fill(postal_code)

    def continue_checkout(self) -> None:
        """Submit the form — advances to checkout step two if valid."""
        self.continue_button.click()

    def cancel(self) -> None:
        """Abandon checkout — returns to the cart."""
        self.cancel_button.click()

    # ------------------------------------------------------------------
    # Read helpers (for negative tests)
    # ------------------------------------------------------------------

    def is_error_visible(self) -> bool:
        """True if the red error banner is showing."""
        return self.error_message.is_visible()

    def error_text(self) -> str:
        """Visible error message text, or empty string."""
        if self.is_error_visible():
            return self.error_message.inner_text()
        return ""
