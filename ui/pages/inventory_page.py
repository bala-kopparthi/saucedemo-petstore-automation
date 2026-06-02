"""
InventoryPage — Page Object for the SauceDemo product listing.

URL: {base_url}/inventory.html

Tests that use this: S1, S2, S3, S4, R1, R2, R3, R5, P1, P2 (the workhorse of the suite)
"""

from playwright.sync_api import Page, Locator

from ui.pages.base_page import BasePage


class InventoryPage(BasePage):
    """Encapsulates locators and actions for the SauceDemo inventory page."""

    URL_PATH = "/inventory.html"

    # Sort dropdown values used by select_sort().
    # SauceDemo's <option value="..."> attribute strings are the official
    # API of the dropdown — we surface them as class constants so test
    # code reads as `inventory.select_sort(InventoryPage.SORT_PRICE_LOW_HIGH)`
    # instead of a magic string.
    SORT_NAME_AZ = "az"
    SORT_NAME_ZA = "za"
    SORT_PRICE_LOW_HIGH = "lohi"
    SORT_PRICE_HIGH_LOW = "hilo"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)

        # --- Product card locators ---
        # `.inventory_item` matches all 6 product cards. Playwright's Locator
        # is a chainable handle — calling .count() on it returns 6, .all() iterates.
        self.product_cards: Locator = page.locator(".inventory_item")
        self.product_names: Locator = page.locator(".inventory_item_name")
        self.product_prices: Locator = page.locator(".inventory_item_price")

        # --- Sort dropdown ---
        self.sort_dropdown: Locator = page.locator('[data-test="product-sort-container"]')

        # --- Cart icon + badge (top right) ---
        self.cart_icon: Locator = page.locator(".shopping_cart_link")
        self.cart_badge: Locator = page.locator(".shopping_cart_badge")

        # --- Hamburger menu (top left) ---
        self.menu_button: Locator = page.locator("#react-burger-menu-btn")
        self.logout_link: Locator = page.locator("#logout_sidebar_link")

    # ------------------------------------------------------------------
    # Helpers (private convention — leading underscore)
    # ------------------------------------------------------------------

    @staticmethod
    def _slug(product_name: str) -> str:
        """Convert a display name to SauceDemo's data-test slug.

        Example: 'Sauce Labs Backpack' -> 'sauce-labs-backpack'
        SauceDemo's data-test attributes are built as 'add-to-cart-<slug>'
        and 'remove-<slug>'. Computing the slug here lets test code pass
        the display name directly: inventory.add_to_cart('Sauce Labs Backpack')
        """
        return product_name.lower().replace(" ", "-")

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------

    def products_count(self) -> int:
        """How many product cards are rendered."""
        return self.product_cards.count()

    def product_names_in_order(self) -> list[str]:
        """Display names in the order they appear on the page.

        Used by sort-verification tests (R2): assert sorted == expected.
        """
        return self.product_names.all_inner_texts()

    def product_prices_in_order(self) -> list[float]:
        """Prices as floats (no '$' sign) in the order they appear.

        Used by sort-verification tests (R1).
        """
        # Inner texts look like ['$29.99', '$9.99', ...]
        # Strip the dollar sign and parse to float for numerical comparison.
        return [
            float(text.replace("$", "").strip())
            for text in self.product_prices.all_inner_texts()
        ]

    def cart_badge_count(self) -> int:
        """Return the number on the cart icon, or 0 if no badge is shown.

        SauceDemo hides the badge entirely when the cart is empty (rather
        than showing '0'), so we check existence before reading text.
        """
        if self.cart_badge.count() == 0:
            return 0
        return int(self.cart_badge.inner_text())

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def add_to_cart(self, product_name: str) -> None:
        """Click the 'Add to cart' button for the named product."""
        slug = self._slug(product_name)
        self.page.locator(f'[data-test="add-to-cart-{slug}"]').click()

    def remove_from_cart(self, product_name: str) -> None:
        """Click the 'Remove' button for the named product (replaces the
        Add to cart button after an item is added)."""
        slug = self._slug(product_name)
        self.page.locator(f'[data-test="remove-{slug}"]').click()

    def select_sort(self, value: str) -> None:
        """Choose a sort option. Use the SORT_* class constants for clarity.

        Example:
            inventory.select_sort(InventoryPage.SORT_PRICE_LOW_HIGH)
        """
        self.sort_dropdown.select_option(value)

    def open_cart(self) -> None:
        """Click the cart icon — navigates to /cart.html."""
        self.cart_icon.click()

    def open_menu(self) -> None:
        """Open the hamburger menu (slide-out from the left)."""
        self.menu_button.click()

    def logout(self) -> None:
        """Open the menu and click Logout — returns user to login page."""
        self.open_menu()
        # Playwright auto-waits for the link to be visible (menu animation)
        # before clicking, so no manual sleep needed.
        self.logout_link.click()
