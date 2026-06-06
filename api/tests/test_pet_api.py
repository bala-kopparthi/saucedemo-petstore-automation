"""
Petstore Pet API test suite (A1-A7).

Covers the Pet resource lifecycle, a status search, a negative path, and a
multipart image upload. See api/api-tests.md for the design rationale.

    A1 | Create a pet                   POST   /pet                  [smoke]
    A2 | Read the pet back              GET    /pet/{id}             [smoke]
    A3 | Update the pet                 PUT    /pet                  [regression]
    A4 | Delete the pet, then GET->404  DELETE /pet/{id}             [regression]
    A5 | Find pets by status=available  GET    /pet/findByStatus     [regression]
    A6 | Read a non-existent pet ->404  GET    /pet/{bogus}          [negative]
    A7 | Upload a pet image (multipart) POST   /pet/{id}/uploadImage [regression]
"""

from pathlib import Path

import pytest

from api.clients.pet_client import PetClient
from api.data.pets import build_pet, unique_pet_id

# The committed PNG for A7. __file__ is api/tests/..., so up to api/, into data/.
SAMPLE_IMAGE = Path(__file__).resolve().parent.parent / "data" / "sample_pet.png"

# An id chosen to be well outside anything we (or others) would realistically create.
BOGUS_PET_ID = 9_999_999_999


# ── A1 ──────────────────────────────────────────────────────────────────
@pytest.mark.api
@pytest.mark.smoke
def test_create_pet_returns_200_and_echoes_body(pet_client: PetClient) -> None:
    """A1: POST /pet returns 200 and the response echoes id, name, status."""
    pet = build_pet(unique_pet_id(), name="Rex", status="available")

    response = pet_client.create(pet)

    assert response.status == 200, f"Expected 200, got {response.status}"
    body = response.json()
    assert body["id"] == pet["id"]
    assert body["name"] == "Rex"
    assert body["status"] == "available"

    pet_client.delete(pet["id"])  # cleanup (this test creates its own pet)


# ── A2 ──────────────────────────────────────────────────────────────────
@pytest.mark.api
@pytest.mark.smoke
def test_get_returns_the_created_pet(
    pet_client: PetClient, created_pet: dict
) -> None:
    """A2: GET /pet/{id} returns the pet created by the fixture."""
    response = pet_client.get(created_pet["id"])

    assert response.status == 200, f"Expected 200, got {response.status}"
    body = response.json()
    assert body["id"] == created_pet["id"]
    assert body["name"] == created_pet["name"]
    assert body["status"] == created_pet["status"]


# ── A3 ──────────────────────────────────────────────────────────────────
@pytest.mark.api
@pytest.mark.regression
def test_update_pet_changes_name_and_status(
    pet_client: PetClient, created_pet: dict
) -> None:
    """A3: PUT /pet updates an existing pet's name and status."""
    updated = dict(created_pet)          # copy so we don't mutate the fixture
    updated["name"] = "Rex Updated"
    updated["status"] = "sold"

    response = pet_client.update(updated)

    assert response.status == 200, f"Expected 200, got {response.status}"
    body = response.json()
    assert body["name"] == "Rex Updated"
    assert body["status"] == "sold"


# ── A4 ──────────────────────────────────────────────────────────────────
@pytest.mark.api
@pytest.mark.regression
def test_delete_pet_then_get_returns_404(pet_client: PetClient) -> None:
    """A4: after DELETE /pet/{id}, a subsequent GET returns 404."""
    pet = build_pet(unique_pet_id())
    assert pet_client.create(pet).status == 200, "Setup create failed"

    delete_response = pet_client.delete(pet["id"])
    assert delete_response.status == 200, f"Delete failed: {delete_response.status}"

    get_response = pet_client.get(pet["id"])
    assert get_response.status == 404, (
        f"Deleted pet should be gone; got {get_response.status}"
    )


# ── A5 ──────────────────────────────────────────────────────────────────
@pytest.mark.api
@pytest.mark.regression
def test_find_by_status_available_returns_available_pets(
    pet_client: PetClient,
) -> None:
    """A5: GET /pet/findByStatus?status=available returns available pets."""
    response = pet_client.find_by_status("available")

    assert response.status == 200, f"Expected 200, got {response.status}"
    pets = response.json()
    assert isinstance(pets, list), "Expected a JSON list"
    assert len(pets) > 0, "Expected at least one available pet"
    # Public sandbox can hold messy data; assert on pets that report a status.
    assert all(p.get("status") == "available" for p in pets if "status" in p), (
        "findByStatus=available returned a non-available pet"
    )


# ── A6 ──────────────────────────────────────────────────────────────────
@pytest.mark.api
@pytest.mark.negative
def test_get_nonexistent_pet_returns_404(pet_client: PetClient) -> None:
    """A6: GET /pet/{bogus_id} for a non-existent pet returns 404."""
    response = pet_client.get(BOGUS_PET_ID)

    assert response.status == 404, (
        f"Expected 404 for a missing pet, got {response.status}"
    )


# ── A7 ──────────────────────────────────────────────────────────────────
@pytest.mark.api
@pytest.mark.regression
def test_upload_pet_image_returns_200(
    pet_client: PetClient, created_pet: dict
) -> None:
    """A7: POST /pet/{id}/uploadImage accepts a multipart file upload.
    """
    assert SAMPLE_IMAGE.exists(), f"Missing test asset: {SAMPLE_IMAGE}"

    response = pet_client.upload_image(created_pet["id"], SAMPLE_IMAGE)

    assert response.status == 200, f"Expected 200, got {response.status}"
    message = response.json().get("message", "").lower()
    assert "uploaded" in message, f"Unexpected upload response: {message}"
    