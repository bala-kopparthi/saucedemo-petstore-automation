"""
LoginPage — Page Object for the SauceDemo login screen.

URL: {base_url}/
Tests that use this: smoke tests (S1, S3), negative tests (N1, N2), user-matrix tests (P1)
"""

from playwright.sync_api import Page, Locator

from ui.pages.base_page import BasePage


class LoginPage(BasePage):
    """Encapsulates locators and actions for the SauceDemo login page."""

    URL_PATH = "/"

    def __init__(self, page: Page, base_url: str) -> None:
        # Call the parent constructor — stores page + base_url
        super().__init__(page, base_url)

        # --- Locators ---
        # Defined once here, reused across methods below.
        # We prefer [data-test="..."] because SauceDemo's devs added these
        # as explicit testing hooks (stable across UI redesigns).
        self.username_input: Locator = page.locator('[data-test="username"]')
        self.password_input: Locator = page.locator('[data-test="password"]')
        self.login_button: Locator = page.locator('[data-test="login-button"]')
        self.error_message: Locator = page.locator('[data-test="error"]')

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def login(self, username: str, password: str) -> None:
        """Fill credentials and click Login.

        Important: this method does NOT assert success or failure.
        The test decides what success looks like by checking the URL
        or the error message AFTER calling this method.
        """
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    # ------------------------------------------------------------------
    # Used by negative tests N1, N2
    # ------------------------------------------------------------------

    def is_error_visible(self) -> bool:
        """True if the red error banner is showing on screen."""
        return self.error_message.is_visible()

    def error_text(self) -> str:
        """Return the visible error message text, or empty string."""
        if self.is_error_visible():
            return self.error_message.inner_text()
        return ""
    