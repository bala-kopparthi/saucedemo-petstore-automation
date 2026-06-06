# SauceDemo + Petstore Automation

This is for demonstrating End-to-end test automation portfolio project:

- **Part 1 — UI:** [SauceDemo (Swag Labs)](https://www.saucedemo.com/) automated with Playwright + Python + pytest using the Page Object Model.
- **Part 2 — API:** [Petstore Swagger](https://petstore.swagger.io/) Pet endpoint tests using Playwright's APIRequestContext + pytest.

[![CI](https://github.com/bala-kopparthi/saucedemo-petstore-automation/actions/workflows/ci.yml/badge.svg)](https://github.com/bala-kopparthi/saucedemo-petstore-automation/actions/workflows/ci.yml)
[![Allure Report](https://img.shields.io/badge/Allure-Live%20Report-success)](https://bala-kopparthi.github.io/saucedemo-petstore-automation/)

> **Status:** Completed — sections below are filled with a detailed step by step analysis.

---

## Tech stack

| Layer | Tool                         |
|---|------------------------------|
| Language | Python 3.14                  |
| Browser automation | Playwright (Python)          |
| API testing | Playwright APIRequestContext |
| Test runner | pytest                       |
| Reporting | Allure + pytest-html         |
| CI | GitHub Actions + Jenkins     |

## Project structure

| Path | Purpose |
|---|---|
| `ui/pages/` | Page Objects — base + login, inventory, cart, and three checkout pages |
| `ui/tests/` | UI tests — login, cart, inventory, checkout, e2e |
| `ui/data/` | Shared UI test data — user-type and product-name constants |
| `api/clients/pet_client.py` | Service wrapper over the Petstore `/pet` endpoints |
| `api/tests/test_pet_api.py` | API tests A1–A7 (CRUD, search, negative, image upload) |
| `api/data/` | Pet payload factory + `sample_pet.png` upload asset |
| `conftest.py` | Shared pytest fixtures — base URLs, credentials, API context, login, failure screenshots |
| `pytest.ini` | Markers and default pytest options |
| `flows.txt` | UI test-design document (scenarios + rationale) |
| `api/api-tests.md` | API test plan |
| `.github/workflows/ci.yml` | CI pipeline — smoke / regression / validation + Allure publish |
| `requirements.txt` | Pinned dependencies |
| `.env.example` | Environment-variable template (copy to `.env`) |

# Quick Start
## 1. Clone
git clone https://github.com/bala-kopparthi/saucedemo-petstore-automation.git
cd saucedemo-petstore-automation

## 2. Virtual environment (Python 3.14)
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

## 3. Dependencies
pip install -r requirements.txt

## 4. Playwright browsers
playwright install               # or: playwright install chromium

## 5. Environment file
cp .env.example .env             # defaults work as-is; SauceDemo creds are public

# Running the tests

## By tier
pytest -m smoke                  # P0 — fast critical path
pytest -m regression             # P1 — broader functional
pytest -m negative               # P2 — validation / error paths

## By layer
pytest -m ui                     # SauceDemo UI only
pytest -m api                    # Petstore API only

## Cross-browser (matches the CI regression job)
pytest -m regression --browser chromium --browser firefox --browser webkit

## Handy flags
pytest --headed                  # watch the browser
pytest -n auto                   # parallel (pytest-xdist is installed)
pytest -k login -v               # filter by name, verbose


# Reporting

**📊 Live report (auto-published by CI):** <https://bala-kopparthi.github.io/saucedemo-petstore-automation/>

This URL always serves the latest CI run, published automatically to GitHub Pages
by the `publish-report` job in `.github/workflows/ci.yml`. The instructions below
are for generating the same report **locally**.

This suite uses [Allure](https://allurereport.org/) for rich, leadership-friendly
reports — charts, history trends, and per-test failure evidence (screenshots + URLs).

**Prerequisites:** `allure-pytest` (in `requirements.txt`, records results) and the
Allure CLI (renders the HTML report):

```bash
brew install allure      # for allure installation on mac
```

**Generate and view the report:**

```bash
# 1. Run the tests, writing raw results
pytest --alluredir=allure-results

# 2. Carry history forward from the previous report (enables Trends; no-op on first run)
cp -r allure-report/history allure-results/history 2>/dev/null || true

# 3. Build the HTML report and open it in the browser
allure generate allure-results --clean -o allure-report
allure open allure-report
```

**What to look at:**

- **Overview** — pass/fail/known-defect breakdown at a glance.
- **Behaviors** — tests grouped by feature → story.
- **Graphs → Severity** — defect severity distribution.
- **Trends** — suite health across runs (appears after the 2nd run).

> **Note on the grey test:** the `error_user` Last Name test (N4) is an `xfail` —
> a *documented, tracked SauceDemo defect*, not an accidental skip. Allure shows it
> grey (expected failure), not red (unexpected failure). The day SauceDemo fixes the
> bug it will flip to a pass — our signal to remove the `xfail` marker.

> `allure-results/` and `allure-report/` are git-ignored — they're build artifacts,
> regenerated on every run.

## Deliverables (per assignment)
1. `flows.txt` at repo root — UI test scenarios explained
2. `api/api-tests.md` — API endpoints covered + how to run

---