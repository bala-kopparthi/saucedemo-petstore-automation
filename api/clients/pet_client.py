"""
PetClient — a thin service wrapper over the Swagger Petstore Pet endpoints.

Mirrors the Page Object Model from Part 1: tests express intent
(pet_client.create(pet)) while HTTP details (paths, verbs, params, multipart)
live here in one place. Every method returns the raw Playwright APIResponse so
the calling test asserts on both the status code and the JSON body.
"""

from pathlib import Path

from playwright.sync_api import APIRequestContext, APIResponse


class PetClient:
    """Wraps the /pet endpoints over a Playwright APIRequestContext."""

    PET_PATH = "pet"

    def __init__(self, request_context: APIRequestContext) -> None:
        self._request = request_context

    # ── CRUD ──────────────────────────────────────────────────────────
    def create(self, pet: dict) -> APIResponse:
        """POST /pet — add a new pet. A dict body is serialized to JSON."""
        return self._request.post(self.PET_PATH, data=pet)

    def get(self, pet_id: int) -> APIResponse:
        """GET /pet/{id} — fetch a pet by id."""
        return self._request.get(f"{self.PET_PATH}/{pet_id}")

    def update(self, pet: dict) -> APIResponse:
        """PUT /pet — update an existing pet (send the full object)."""
        return self._request.put(self.PET_PATH, data=pet)

    def delete(self, pet_id: int) -> APIResponse:
        """DELETE /pet/{id} — remove a pet by id."""
        return self._request.delete(f"{self.PET_PATH}/{pet_id}")

    # ── Query ─────────────────────────────────────────────────────────
    def find_by_status(self, status: str) -> APIResponse:
        """GET /pet/findByStatus?status=... — list pets in a given status."""
        return self._request.get(
            f"{self.PET_PATH}/findByStatus", params={"status": status}
        )

    # ── Upload (multipart) ────────────────────────────────────────────
    def upload_image(self, pet_id: int, image_path: str | Path) -> APIResponse:
        """POST /pet/{id}/uploadImage — multipart/form-data file upload.

        We read the file into a buffer and pass it via Playwright's `multipart`
        argument; Playwright sets the multipart Content-Type + boundary itself
        (which is why the request fixture no longer forces application/json).
        """
        image_path = Path(image_path)
        return self._request.post(
            f"{self.PET_PATH}/{pet_id}/uploadImage",
            multipart={
                "file": {
                    "name": image_path.name,
                    "mimeType": "image/png",
                    "buffer": image_path.read_bytes(),
                }
            },
        )
