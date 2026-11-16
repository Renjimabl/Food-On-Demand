# DineFlash Login Tests (Python + Playwright) - Beginner Guide

## What is in this project

```
dineflash-tests/
  requirements.txt      list of tools to install
  .env.example          template for your username/password
  pytest.ini            test settings
  conftest.py           shared setup (reads .env, opens the login page)
  pages/login_page.py   knows where the username, password and button are
  tests/test_login.py   the actual test cases
```

## One-time setup (Windows)

1. Install Python from https://www.python.org/downloads/ . On the first installer screen tick "Add python.exe to PATH".
2. Open VS Code, then File > Open Folder > choose the `dineflash-tests` folder.
3. Open the terminal: Terminal > New Terminal.
4. Check Python works:
   ```
   python --version
   ```
5. Create a virtual environment (a private box for this project's tools):
   ```
   python -m venv venv
   ```
6. Activate it:
   ```
   venv\Scripts\activate
   ```
   If PowerShell blocks it, run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` and try again. You should now see `(venv)` at the start of the line.
7. Install the tools:
   ```
   pip install -r requirements.txt
   ```
8. Install the test browsers:
   ```
   playwright install
   ```
9. Add your login details:
   - Copy `.env.example` and rename the copy to `.env`
   - Open `.env` and replace `your_username_here` and `your_password_here` with your real username and password
   - Keep `.env` private. Do not email it or post it anywhere.

## Run the tests

All tests, with a visible browser so you can watch:
```
pytest --headed
```
Slow it down so you can follow what happens:
```
pytest --headed --slowmo 500
```
Only one test:
```
pytest tests/test_login.py::test_valid_login --headed
```
Without opening the browser window (faster):
```
pytest
```
Run in Chrome specifically:
```
pytest --browser chromium --headed
```

## Reading the result

- `PASSED` means the app behaved as expected.
- `FAILED` means a bug, or the test needs adjusting. Read the message below it. A screenshot of failures is saved in the `test-results` folder.
- `SKIPPED` on valid-login tests means `.env` is missing or empty.

## If a test cannot find the username box or button

The locators in `pages/login_page.py` are guesses based on the screen. To find the exact ones, let Playwright record them:
```
playwright codegen https://py.softlandindia.net/dine_flash_buffet/login/
```
A browser and a code window open. Click the username box and Sign In; the code window shows the exact locator. Copy it into `login_page.py`.

## How a test works (example)

```python
def test_valid_login(login_page, valid_username, valid_password):
    login_page.login(valid_username, valid_password)   # type + click Sign In
    assert not login_page.is_on_login_page()           # check we left /login
```
Steps: open the page, do something, then check (assert) the result.

## Next steps

Once login works, add new files in `tests/` for other modules (for example `test_outlet.py`), using the same pattern.
Copy the test case IDs from your Excel sheet into the test names so they match.
