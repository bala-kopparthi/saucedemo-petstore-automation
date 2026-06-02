"""
Project-wide pytest feature.

conftest.py is a feature of pytest — anything defined here is available
to every test under this directory tree without `import`. We can add more common features - as we go in this project.
"""

import os
import pytest
from dotenv import load_dotenv

# Load .env once at import time so env vars are available in fixtures below.
# python-dotenv silently does nothing if .env doesn't exist — safe in CI.
load_dotenv()


@pytest.fixture(scope="session")
def base_url() -> str:
    """Providing SauceDemo base URL."""
    return os.getenv("BASE_URL", "https://www.saucedemo.com")


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Petstore API base URL."""
    return os.getenv("API_BASE_URL", "https://petstore.swagger.io/v2")


@pytest.fixture(scope="session")
def saucedemo_credentials() -> dict[str, str]:
    """Valid SauceDemo username/password from env vars.

    SauceDemo's creds are public (visible on their login page), so .env here
    is about *demonstrating the pattern*, not real secrecy.
    """
    return {
        "username": os.getenv("SAUCEDEMO_VALID_USERNAME", "standard_user"),
        "password": os.getenv("SAUCEDEMO_VALID_PASSWORD", "secret_sauce"),
    }
from playwright.sync_api import Page

from ui.pages.inventory_page import InventoryPage
from ui.pages.login_page import LoginPage

@pytest.fixture
def logged_in_inventory(
    page: Page, base_url: str, saucedemo_credentials: dict
) -> InventoryPage:
    """Log in as standard_user and return an InventoryPage instance.

    Use this as the starting fixture for any test that needs an
    authenticated session on the inventory screen. Avoids repeating
    login boilerplate in every test file.

    Usage in a test:
        def test_something(logged_in_inventory: InventoryPage) -> None:
            logged_in_inventory.add_to_cart("Sauce Labs Backpack")
    """
    login = LoginPage(page, base_url)
    login.navigate()
    login.login(
        saucedemo_credentials["username"],
        saucedemo_credentials["password"],
    )
    return InventoryPage(page, base_url)

