"""
Pet test-data factory for the Petstore API tests.

Centralizes Pet payload construction and unique-id generation so tests don't
collide on the shared public sandbox and don't repeat the Pet JSON shape.
"""

import random


def unique_pet_id() -> int:
    """Return a wide random id, unlikely to collide with other sandbox users.
    """
    return random.randint(10_000_000, 99_999_999)


def build_pet(
    pet_id: int,
    name: str = "doggie",
    status: str = "available",
) -> dict:
    """Build a valid Pet payload (Swagger v2 Pet schema).
    """
    return {
        "id": pet_id,
        "name": name,
        "status": status,                       # available | pending | sold
        "photoUrls": ["https://example.com/photo.jpg"],
        "category": {"id": 1, "name": "dogs"},
        "tags": [{"id": 1, "name": "friendly"}],
    }
