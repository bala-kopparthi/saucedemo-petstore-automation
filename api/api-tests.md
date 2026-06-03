# Petstore API Test Plan — api-tests.md

| | |
|---|---|
| **Project**    | SauceDemo + Petstore Automation |
| **Part**       | 2 (Petstore API Automation) |
| **Target API** | https://petstore.swagger.io/v2  (Pet endpoints) |
| **Stack**      | Python 3.14 + Playwright APIRequestContext + pytest |
| **Author**     | Bala Kopparthi |

## 1. Purpose
This document describes the API test scenarios for the Swagger Petstore **Pet**
resource, the rationale behind the coverage, and what is intentionally out of
scope. Read this **before** the test code — it explains *why* these tests exist.

## 2. Tools & why
- **Playwright `APIRequestContext`** — same framework as Part 1 (UI), so a single
  dependency set, one test runner, one reporting pipeline. No browser is launched
  for API tests; we send raw HTTP and assert on JSON bodies + status codes.

- **pytest** — fixtures for setup/teardown and test isolation, markers for
  selective runs.

- **`PetClient` service class** — a thin wrapper over the Pet endpoints so tests
  read as intent (`pet_client.create(...)`) and the HTTP details live in one
  place. This mirrors the Page Object Model used in Part 1.

> This is code-first, CI-runnable API testing.

## 3. Test design philosophy
Coverage follows the resource lifecycle plus its boundaries:
1. **CRUD lifecycle** — Create → Read → Update → Delete (the core contract).
2. **Search** — find pets by status (a list-returning query endpoint).
3. **Negative** — request a non-existent pet (the 404 path).

## 4. Scenario inventory (6 scenarios)

| ID | Scenario | Method & Endpoint | Expected result | Tier marker |
|----|----------|-------------------|-----------------|-------------|
| A1 | Create a pet          | `POST /pet`                              | 200; body echoes id, name, status        | `smoke` |
| A2 | Read the pet back     | `GET /pet/{id}`                          | 200; fields match the created pet         | `smoke` |
| A3 | Update the pet        | `PUT /pet`                               | 200; name/status reflect the change       | `regression` |
| A4 | Delete the pet        | `DELETE /pet/{id}`                       | 200; subsequent `GET /pet/{id}` → 404     | `regression` |
| A5 | Find pets by status   | `GET /pet/findByStatus?status=available` | 200; a list; every item status==available | `regression` |
| A6 | Read non-existent pet | `GET /pet/{bogus_id}`                    | 404                                       | `negative` |
| A7 | Upload a pet image    | `POST /pet/{id}/uploadImage`             | 200; response reports the uploaded byte count | `regression` |

> Every API test additionally carries `@pytest.mark.api`, so `pytest -m api`
> runs the whole API suite in isolation.
 
> A7 caveat: petstore cannot be re-queried to confirm the stored image, so this
> test asserts only HTTP 200 + the byte count echoed in the response message.
> This is a documented limitation of the public sandbox, not a gap in coverage.

## 5. Test data & isolation strategy
- **Unique pet IDs** — petstore.swagger.io is a public, shared sandbox. Each test
  generates a unique ID so runs never collide with other users' data, and we
  assert only on the pet we own.
- **Self-cleaning tests** — a `created_pet` pytest fixture `POST`s a fresh pet,
  hands it to the test, and `DELETE`s it on teardown. Tests stay isolated and
  leave no litter on the shared server.
- **Tolerant assertions** — where the public server is known to be loose (e.g.
  eventual consistency on a freshly-created pet), assertions focus on what we
  control rather than brittle server-wide state.
- **Upload asset** — a tiny PNG committed at `api/data/sample_pet.png` feeds the
  A7 upload test (binary assets this small are fine to version-control).

## 6. Explicitly out of scope (with rationale)
1. `POST /pet/{id}` form-data update — redundant with `PUT /pet`.
2. **Store** and **User** endpoint groups — the assignment scopes Part 2 to the
   **Pet** endpoints.
3. API-key / auth flows — the public Petstore does not enforce them on Pet.

## 7. How to run
> Run from the repo root with the virtual environment active.

```bash
# Run the whole API suite
pytest -m api -v

# Or by path
pytest api/tests -v

# Only the API smoke tests
pytest api/tests -m smoke -v
```

## 8. pytest marker reference
| Marker        | Meaning |
|---------------|---------|
| `api`         | All Petstore API tests (Part 2) |
| `smoke`       | Core lifecycle (create / read) |
| `regression`  | Update, delete, search |
| `negative`    | Error / not-found paths |
