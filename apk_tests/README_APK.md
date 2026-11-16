# Food On Demand APK - Login Tests (Appium + Python)

## What is already on this PC
Node.js, Java (JDK 24), Appium 2.19 with the UiAutomator2 driver, Python venv with Appium-Python-Client.

## One-time setup

### Step 1 - Install adb (the tool that talks to the phone)
adb is the only missing piece. Download "SDK Platform-Tools for Windows" from
https://developer.android.com/tools/releases/platform-tools (about 7 MB), and unzip it so this file exists:

    C:\Users\WSSPC-009\AppData\Local\Android\Sdk\platform-tools\adb.exe

(So the unzipped `platform-tools` folder sits inside `...\Android\Sdk`.)
Check it:
    C:\Users\WSSPC-009\AppData\Local\Android\Sdk\platform-tools\adb.exe version

### Step 2 - Prepare the phone
1. Settings > About phone > tap "Build number" 7 times (turns on Developer options).
2. Settings > Developer options > turn on **USB debugging**.
3. Connect the USB cable. On the phone tap **Allow** on the "Allow USB debugging?" prompt (tick "Always allow").
4. Check the phone is seen:
       C:\Users\WSSPC-009\AppData\Local\Android\Sdk\platform-tools\adb.exe devices
   The list must show a device with the word `device` (not `unauthorized`).

### Step 3 - Choose the APK
Open `apk.env`. APK_PATH is the QA build (FoodOnDemand_QA_v1.0.1.apk). Switch to the LIVE line if you must test live.

### Step 4 - Install the APK and detect the app name (once)
In the VS Code terminal, with (venv) active, from the dineflash-tests folder:

    python apk_tests/find_app.py

It installs the APK and fills APP_PACKAGE and APP_ACTIVITY in apk.env.

## Run the login tests
    cd apk_tests
    pytest

The Appium server starts by itself. Failure screenshots are saved in `apk_tests/failures`.

Test login used: username `buffet`, password `123` (apk.env).

## If a test cannot find the login boxes or button
    python apk_tests/dump_screen.py
It saves `screen.png` and `screen.xml`. Send both to Claude, or open screen.xml and find the real names, then adjust
the helper functions at the top of `test_apk_login.py`.

## Tests included (12)
App opens on login screen, username/password boxes, password masked, valid login, wrong password, unknown user,
empty fields, empty password, spaces only, case-sensitive password, SQL injection text, session kept after restart.


---
## Update: all scenarios (55 tests)
Files (all inside apk_tests, visible in the VS Code Explorer):
- `test_apk_login.py` - Customer ID screen, login screen, valid login, 9 invalid logins, session, logout pop-up
- `test_apk_dashboard.py` - dashboard content, quick actions, bottom tabs, refresh, logout pop-up
- `ui.py` - helpers. Tapping and typing use adb, because Appium's own click/type crashes its helper app on this vivo phone.
- `conftest.py` - starts Appium, resets the app, enters Customer ID 0711, logs in as buffet.

Run everything (phone connected, screen on and unlocked):
    cd apk_tests
    pytest

Run one file:   pytest test_apk_login.py
Run one test:   pytest test_apk_login.py::test_valid_login

Screens behind Create Order, Orders, Chat, Reports and Settings are only checked for "opens and returns".
Open each one on the phone, run `python dump_screen.py`, and add exact checks.
