"""
SauceDemo product catalog — canonical product names for cart/checkout tests.

Centralizing these avoids magic-string duplication across test files and
gives a single place to update if SauceDemo changes its catalog.

"""

BACKPACK = "Sauce Labs Backpack"
BIKE_LIGHT = "Sauce Labs Bike Light"
BOLT_TSHIRT = "Sauce Labs Bolt T-Shirt"
FLEECE_JACKET = "Sauce Labs Fleece Jacket"
ONESIE = "Sauce Labs Onesie"

# A small, stable subset used by multi-item cart tests
SAMPLE_PRODUCTS = [BACKPACK, BIKE_LIGHT, BOLT_TSHIRT]
