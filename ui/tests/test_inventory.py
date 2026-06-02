"""
Inventory test suite — product sorting (R1, R2).

Scenarios covered:
    R1 | Sort by price: low→high and high→low, verify actual order  [regression]
    R2 | Sort by name:  A→Z and Z→A, verify actual order            [regression]

All tests start from an already-authenticated inventory page via the
`logged_in_inventory` fixture (defined in the root conftest.py).
"""

import pytest

from ui.pages.inventory_page import InventoryPage


# ── R1 ────────────────────────────────────────────────────────────────

@pytest.mark.regression
@pytest.mark.ui
@pytest.mark.parametrize(
    "sort_value, descending",
    [
        (InventoryPage.SORT_PRICE_LOW_HIGH, False),  # cheapest first
        (InventoryPage.SORT_PRICE_HIGH_LOW, True),   # priciest first
    ],
    ids=["low_to_high", "high_to_low"],
)
def test_inventory_sorted_by_price(
    logged_in_inventory: InventoryPage, sort_value: str, descending: bool
) -> None:
    """R1: selecting a price sort reorders products correctly.

    We read the displayed order and assert it equals that same list sorted
    by Python — proving the UI's ordering matches the expected contract,
    without hard-coding fragile price values.
    """
    inventory = logged_in_inventory

    # Act: choose the price-sort option from the dropdown
    inventory.select_sort(sort_value)

    # Assert: on-screen order matches a correctly-sorted copy of itself
    prices = inventory.product_prices_in_order()       # e.g. [7.99, 9.99, ...]
    assert prices == sorted(prices, reverse=descending), (
        f"Prices not sorted (descending={descending}): {prices}"
    )


# ── R2 ────────────────────────────────────────────────────────────────

@pytest.mark.regression
@pytest.mark.ui
@pytest.mark.parametrize(
    "sort_value, descending",
    [
        (InventoryPage.SORT_NAME_AZ, False),  # A → Z
        (InventoryPage.SORT_NAME_ZA, True),   # Z → A
    ],
    ids=["a_to_z", "z_to_a"],
)
def test_inventory_sorted_by_name(
    logged_in_inventory: InventoryPage, sort_value: str, descending: bool
) -> None:
    """R2: selecting a name sort reorders products alphabetically."""
    inventory = logged_in_inventory

    inventory.select_sort(sort_value)

    names = inventory.product_names_in_order()
    assert names == sorted(names, reverse=descending), (
        f"Names not sorted (descending={descending}): {names}"
    )
    