"""
Project-wide pytest feature.

conftest.py is a feature of pytest — anything defined here is available
to every test under this directory tree without `import`. We can add more common features - as we go in this project.
"""

import os
import pytest
from dotenv import load_dotenv
#widening the existing Page import and adding Generator
from collections.abc import Generator
from playwright.sync_api import APIRequestContext, Page, Playwright
from api.clients.pet_client import PetClient
from api.data.pets import build_pet, unique_pet_id


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

@pytest.fixture(scope="session")
def api_request_context(
    playwright: Playwright, api_base_url: str
) -> Generator[APIRequestContext, None, None]:
    """Session-scoped HTTP client for the Petstore API.

    APIRequestContext is Playwright's HTTP client — like a browser context but
    with no page/rendering, just request->response. We point it at API_BASE_URL
    (from .env) so tests use short relative paths like "/pet", and set JSON
    headers once here instead of on every call. Built once per session for
    speed; disposed at the end to release the connection.
    """
    request_context = playwright.request.new_context(
        base_url=api_base_url.rstrip("/") + "/",
        extra_http_headers={
            "Accept": "application/json",
            #"Content-Type": "application/json",
            # No Content-Type here on purpose:
            # Playwright auto-sets application/json for dict bodies, and
            # for the multipart image upload it sets multipart/form-data + boundary itself.
        },
    )
    # Everything before `yield` is setup; everything after is teardown.
    yield request_context
    request_context.dispose()

@pytest.fixture
def pet_client(api_request_context: APIRequestContext) -> PetClient:
    """A PetClient wired to the session-scoped API request context."""
    return PetClient(api_request_context)

@pytest.fixture
def created_pet(pet_client: PetClient) -> Generator[dict, None, None]:
    """Create a fresh pet on the server, yield it, delete it on teardown.

    Lets read/update/upload tests start from an existing pet without each one
    repeating create + cleanup. Teardown keeps the shared sandbox tidy.
    """
    pet = build_pet(unique_pet_id())
    response = pet_client.create(pet)
    assert response.status == 200, f"Setup create failed: HTTP {response.status}"

    yield pet  # hand the created pet (incl. its id) to the test

    # Teardown: best-effort delete; ignore the result if it's already gone.
    pet_client.delete(pet["id"])

