# Bug Report - Food On Demand Manager APK
Build tested: FoodOnDemand_QA_v1.0.1.apk (package com.softland.foodondemand, version 1.0.1)
Device: vivo, Android 12, USB debugging | Tool: Appium 2.19 + UiAutomator2 + Python/pytest
Test user: buffet (Outlet Manager, outlet "zam zam kazhakkoottam") | Customer ID: 0711
Test date: 11-Nov-2026

---
## 1. Summary

| Item | Count |
|------|-------|
| Tests in the suite | 55 |
| Passed | 7 |
| Failed | 3 |
| Expected failure (known bug) | 1 |
| Not run - setup error | 44 |
| Run time | 33 min |

IMPORTANT: 47 of the 55 tests did not complete because Appium's helper app on the phone
crashed ("socket hang up"). That is a tool / phone problem (ENV-01 below), NOT a bug in the APK.
Only the product bugs in section 2 are real findings. Nothing in section 3 should be read as "the app failed".

## 2. Product bugs and findings (APK)

| ID | Title | Severity | Priority | Status |
|----|-------|----------|----------|--------|
| BUG-APK-01 | Logout does not end the session: reopening the app goes straight to the dashboard | High | P1 | Open - confirm with developer |
| BUG-APK-02 | Logout icon on the dashboard has no accessible name | Low | P4 | Suspected - confirm |

### BUG-APK-01 - Logout does not end the session
- Screen: Home dashboard, logout icon (top right) > "Are you sure you want to logout?" > Logout
- Steps:
  1. Log in as buffet / 123 (Customer ID 0711). Dashboard shows "Good morning buffet".
  2. Tap the logout icon, then tap **Logout** in the pop-up.
  3. The app closes to the phone home screen.
  4. Open Food On Demand again.
- Expected: Login screen is shown, because the user logged out.
- Actual: The dashboard opens straight away, still logged in as buffet, with no username or password asked. (Checked twice.)
- Impact: On a shared tablet or phone, the next person gets the previous manager's account. Possible security risk.
- Note: If "stay signed in" is intended, Logout should still clear it, or the pop-up should say so.
- Automated test: test_logout_then_reopen_asks_for_login (marked expected failure).

### BUG-APK-02 - Logout icon has no accessible name
- Screen: Home dashboard.
- The round logout icon top right has no text, no id and no description in the screen tree, so a screen reader cannot announce it and automation cannot find it without screen coordinates.
- Severity: Low. Suggest adding a content description such as "Logout".

### Things that worked (observed on the phone)
- Customer ID screen: 4 digit boxes and a Check License button, shows App Version 1.0.1 and the Device ID.
- Valid Customer ID (0711) moves on to "Fetching Service URL" and then the login screen.
- Login screen: "Welcome back", Username, Password (hidden), eye icon described as "Show password", Sign in button.
- Valid login (buffet / 123) opens the dashboard with greeting, outlet name, TOTAL / ACTIVE / SERVED, Create Order, View Orders, Chat, Report, Settings and five bottom tabs.
- Logout pop-up shows Cancel and Logout buttons; Cancel was not run through the suite.

## 3. Test environment problem (not an app bug)

### ENV-01 - Appium helper app crashes on this vivo phone
- Symptom: "Could not proxy command to the remote server. Original error: socket hang up" and
  "instrumentation process is not running (probably crashed)".
- Effect: 3 failed and 44 errored tests (every test after the first screen tap or text entry).
- Already tried: tapping and typing with adb instead of Appium, a new Appium session per test with retries, vivo "USB debugging (Security settings)" turned on.
- Next options:
  1. Run the suite on an Android emulator (Android Studio) or a different, non-vivo phone.
  2. Update the UiAutomator2 driver:  appium driver update uiautomator2
  3. Keep the phone unlocked, screen on, battery saver off, and the vivo "background high power use" allowed for Appium Settings and UiAutomator2.
  4. Until fixed, run these checks by hand on the phone (see section 4).

## 4. Coverage

| Area | Automated result | Status |
|------|------------------|--------|
| Customer ID screen (4 boxes, version, device id, wrong ID, empty ID) | Some passed | Partly verified |
| Login screen layout, masked password, show-password | Not run (ENV-01) | Verified by hand only |
| Valid login | Failed (ENV-01) | Verified by hand: works |
| Invalid logins (wrong password, unknown user, empty, spaces, SQL text, script text, 200 characters) | Not run (ENV-01) | NOT TESTED |
| Password case sensitivity | Not run (ENV-01) | NOT TESTED |
| Session kept after restart | Passed | OK |
| Logout cancel / logout pop-up | Not run (ENV-01) | Pop-up seen by hand |
| Logout then reopen | Expected failure | BUG-APK-01 |
| Dashboard content, quick actions, bottom tabs, refresh | Not run (ENV-01) | Seen by hand, not automated |
| Create Order, View Orders, Chat, Reports, Settings screens | Not run | NOT TESTED (screens not yet inspected) |

### Manual checklist for the untested login cases (buffet / 123)
Enter each pair on the Login screen and record the result:
| # | Username | Password | Expected |
|---|----------|----------|----------|
| 1 | buffet | wrong_pw_999 | Rejected with a message |
| 2 | no_such_user_x | 123 | Rejected |
| 3 | buffet | (empty) | Rejected, message asks for password |
| 4 | (empty) | 123 | Rejected, message asks for username |
| 5 | (empty) | (empty) | Rejected |
| 6 | (one space) | (one space) | Rejected |
| 7 | ' OR 1=1 -- | ' OR 1=1 -- | Rejected |
| 8 | BUFFET (capitals) | 123 | Record whether accepted (usernames may be case-insensitive) |
| 9 | " buffet " (spaces around) | 123 | Record whether accepted |
| 10 | 200 characters | 200 characters | Rejected, no crash |

## 5. Test data
- Android app data was cleared before each test, so the phone asks for the Customer ID 0711 again.
- The phone may still be signed in as buffet after the test run (see BUG-APK-01 - logging out does not end the session).
- No data was created on the server by the APK tests.
