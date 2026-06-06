"""
BasePage — repository for all SauceDemo page objects.
"""

from playwright.sync_api import Page


class BasePage:
    """Parent class for every page object in this project."""

    # LoginPage sets URL_PATH = "/", InventoryPage sets "/inventory.html"
    URL_PATH: str = "/"

    def __init__(self, page: Page, base_url: str) -> None:
        """The Constructor - Store the Playwright page handle and the project's base URL.
        """
        self.page = page #Store the parameter as an instance attribute
        self.base_url = base_url

    @property
    def url(self) -> str:
        """Compose full URL: base_url + this page's URL_PATH."""
        return f"{self.base_url}{self.URL_PATH}"

    def navigate(self) -> None:
        """Open this page in the browser."""
        self.page.goto(self.url)

    def current_url(self) -> str:
        """Return what the browser is currently showing (address bar)."""
        return self.page.url
