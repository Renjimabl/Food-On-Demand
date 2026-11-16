# Bug Report - Food On Demand (DineFlash Buffet) - Admin Portal
Test date: 10-Nov-2026 | Build: py.softlandindia.net/dine_flash_buffet | Tool: Python + Playwright (Chromium)
Tester account: zam (Company Admin)

## Run summary (kitchen / user-management flow, 18 tests)
Passed: 11 | Failed: 6 | Skipped: 1 (first run)
Of the 6 failures, 3 were wrong test locators (fixed, see "Test issues") and 3 point to one suspected product bug (BUG-01) that needs the developer's confirmation.

| ID | Title | Severity | Priority | Status |
|----|-------|----------|----------|--------|
| BUG-01 | Kitchen Staff and Outlet Manager users created in the portal cannot log in on the web login page | High (if web login is intended) / Info (if app-only) | P1 | Open - needs confirmation |
| BUG-02 | Web login silently ignores Sign In clicked soon after the page loads | Medium | P2 | Open |
| BUG-03 | Sidebar and menu names differ from the user manual | Low | P3 | Open |
| BUG-04 | Users List has no username column and no Mapped/Unmapped filter | Low | P3 | Open - confirm against manual |
| BUG-05 | Browser pop-up alert used for login errors | Low | P3 | Open |

---

## BUG-01 - Created Kitchen Staff / Outlet Manager cannot log in on the web login
- Module: Login and Authentication / Users
- Severity: High | Priority: P1
- Steps:
  1. Log in as zam. Open Users(Dev) > New User.
  2. Create user "kia" / password 123, role Kitchen Staff, outlet "zam zam kazhakkoottam". Message "User created successfully" is shown and the user appears in Users List.
  3. Repeat for username "omar" / 123, role Outlet Manager.
  4. Open the login page and sign in as kia / 123, then as omar / 123.
- Expected: Either the user signs in, or the page says clearly that this role can use the mobile app only.
- Actual: Pop-up "Invalid username or password." for both, although the password is correct. The message wrongly suggests a wrong password.
- Evidence: tests test_12, test_14, test_16, test_17 (marked xfail BUG-01). popup_log.txt.
- Note: The manual says kitchen staff and managers use the Android apps (Android Tabs, Manager Devices). If web login is meant for admins only, change the message to "This account can sign in on the mobile app only" and re-class this as an improvement.

## BUG-02 - Sign In ignored when clicked too soon after page load
- Module: Login | Severity: Medium | Priority: P2
- Steps: Open the login page, type valid credentials, click Sign In within about 1 second of load.
- Expected: Login completes, or the button is disabled until the page is ready.
- Actual: The form is posted but nothing happens. No message, user stays on the login page. Behaviour appeared in automation (a fast user could hit it). Waiting about 2.5 seconds after load makes login work.
- Evidence: failed test_valid_login before the wait was added. The page also fires several background calls to /api/dine_flash_client_diag/ on load.

## BUG-03 - Names in the app differ from the manual
| Manual says | App shows |
|---|---|
| Role "Utility User (Kitchen)" | Kitchen Staff |
| Menu "Food / Utility Mapping" | Menu Mapping |
| Screen "Select Utility User" | Select Kitchen Staff |
| Message "Utility mapping saved successfully." | to be confirmed on save |
Severity Low. Update the manual or the app so they match.

## BUG-04 - Users List missing items described in the manual
- Users List columns: Name, Roles, Outlet Name, Created Time, Actions. No username column, so two users with the same full name cannot be told apart.
- The Mapped / Unmapped / All filter in the manual is not on the page.
- Severity Low. Confirm with the product owner.

## BUG-05 - Login errors shown as browser pop-up
- The message "Invalid username or password." appears as an alert() dialog. It blocks the page and is hard to read for screen readers. Suggest an inline error message under the form.

---

## Test issues (not product bugs, already fixed in the test code)
| Test | Cause | Fix |
|---|---|---|
| test_03 | Looked for role "Utility User"; the app says Kitchen Staff | Updated |
| test_09 | Looked for a Filter dropdown that does not exist | Replaced with a Users List content check |
| test_10, test_11 | Looked for menu "Food / Utility Mapping" | Now opens Menu Mapping, uses #user-select and #save-mapping-btn |
| Login tests | Clicked Sign In before the page was ready | Wait added in LoginPage |

## Passed (working as expected)
Admin login and dashboard, sidebar items, New User form fields, required-field validation, password-mismatch rejection, kitchen user creation, outlet manager creation, duplicate username rejection, new users shown in Users List with correct role, wrong password rejected, kitchen user cannot open the admin dashboard.

## Test data created on the live site
Users kia (Kitchen Staff) and omar (Outlet Manager) now exist for outlet "zam zam kazhakkoottam". The list also holds other users that were not created by these tests (for example Test zam, food, kit, buffet, jay, hiya). Ask the admin to delete test users when finished.


---
# Add Menu module (new menu / food counter) - added 11-Nov-2026
Test file: tests/test_add_menu.py (24 tests). Final result: 23 passed, 1 expected failure (BUG-09).

## Test data used
| # | Menu name | Display name | Food type | Pre-announce | Service time | Active | Expected |
|---|-----------|--------------|-----------|--------------|--------------|--------|----------|
| 1 | North Indian Counter | Counter 2 | Veg | 2 | 5 | Yes | Created, shows Veg / Active |
| 2 | Chinese Counter | Counter 3 | Non Veg | 2 | 5 | Yes | Created, shows Non Veg / Active |
| 3 | Dessert Counter | Counter 4 | Veg | 2 | 5 | Yes | Created |
| 4 | Seasonal Counter | Counter 5 | Veg | 0 | 0 | No | Created, shows Inactive |
| 5 | (all empty) | | | | | | Rejected |
| 6 | each of outlet / name / display / food type left empty | | | | | | Rejected |
| 7 | South Indian Counter | Counter 1 | Non Veg | | | | Rejected (duplicate name) |
| 8 | SOUTH INDIAN COUNTER (upper case) | | | | | | Rejected (duplicate, any case) |
| 9 | pre-announcement -1, -50, 1.5, letters | | | | | | Rejected / letters not typed |
| 10 | <script>alert(1)</script> and ' OR 1=1 -- as name | | | | | | No script runs |
| 11 | 300 letter name | | | | | | Should be rejected (BUG-09) |
| 12 | Option "No onion", status Active | | | | | | Option shows in Manage Options |
| 13 | Fill form then Cancel | | | | | | Leaves the form, nothing saved |

## BUG-06 - Menu list loads several seconds late
Manage Food Menu shows an empty table for about 3 seconds before rows appear. Low / P3. Add a loading indicator.

## BUG-07 - Duplicate menu error is vague
Creating a duplicate shows a popup "Something went wrong" with the real reason underneath ("Menu name already exists for this outlet"). Low / P3. Show only the specific reason.

## BUG-08 - Create Menu button not disabled while saving
No visible busy state, so a double click may send two requests. Low / P3. (Not proven by a test; confirm manually.)

## BUG-09 - No length limit on menu name
- Steps: Add Menu, enter a 300 character name, valid display name and food type, click Create Menu.
- Expected: Rejected with a length message (a reasonable limit such as 50 or 100 characters).
- Actual: Saved (HTTP 201). The very long name can break table layouts and mobile screens.
- Severity: Medium | Priority: P2

## BUG-10 - Cancel is a link, not a button
Minor accessibility note: Cancel is not exposed as a button to screen readers. Low / P4.

## Test data now on the live site (please delete when testing ends)
North Indian Counter, Chinese Counter, Dessert Counter, Seasonal Counter (inactive), a 300 letter "AAAA..." menu, and possibly menus named <script>alert(1)</script> and ' OR 1=1 -- . Check Manage Food Menu and remove them.


---
# Banners and Banner Profiles - added 11-Nov-2026
Evidence: pages read on the live site with a script. The Banner Profiles automated tests (tests/test_banner_profiles.py) have NOT been run yet, so bugs from those runs are not listed here. Add them after your first run.

| ID | Title | Severity | Priority | Status |
|----|-------|----------|----------|--------|
| BUG-11 | Developer labels "(Dev)" visible in the admin menu | Low | P3 | Open |
| BUG-12 | Profile List table is empty for about 2 seconds after the page opens | Low | P3 | Open (same cause as BUG-06) |
| BUG-13 | Mapped List has no way to see or remove the profiles mapped to an outlet | Low / Medium | P3 | Suspected - confirm against the manual |
| BUG-02 | Sign In ignored when clicked soon after page load (new evidence) | Medium | P2 | Still open |

## BUG-11 - "(Dev)" labels in the menu
- Menu items read "Users(Dev)" and "Profile List(Dev)" (seen in the sidebar on every page).
- Expected: final names such as "Users" and "Profile List", or the items hidden from customers if they are not finished.
- Actual: development suffix is shown. Looks unfinished and may mean the screens are not ready.
- Severity Low. Evidence: sidebar screenshot and page text.

## BUG-12 - Profile List loads late with an empty table
- Steps: open Banner Profiles > Profile List(Dev).
- Actual: 0 rows at 0.5 seconds, rows appear after about 2 seconds, with no loading message. Same behaviour as Manage Food Menu (BUG-06).
- Suggest a loading indicator or "Loading..." text so staff do not think the list is empty.

## BUG-13 - Mapped List shows only a count
- The page "Profiles Mapped to Each Outlet" shows "zam zam kazhakkoottam - 1 Profile". The page has no visible button to open the outlet, see which profile, or remove (unassign) it.
- Expected: view the mapped profiles and unassign one.
- Confirm with the product owner whether this is meant to be view-only. Severity Low (Medium if unassign is required).

## BUG-02 - new evidence
- Seen again today in two of about six automated login attempts: the form is submitted and the page stays on the login screen with no message. Waiting about 3 seconds after the page opens and retrying makes it work.

## Checked and fine (no bug)
- Profile List row icons have names: "View Images", "Edit Profile", "Delete Profile".
- New Profile form has all 5 priorities and 7 day boxes plus Select All, Add Slot and an image library with Select All / Confirm Selection.
- Profile "Banner1" uses the same date for start and end, so a same-day profile is valid.

## Not yet tested (needs your run or a decision)
Edit save, real delete, unassign, multiple slots, overlapping slots, other roles opening these pages, banner shown on the customer screen.


---
# Security finding - added 11-Nov-2026

## BUG-14 - Debug 404 page exposes the site's internal URL list
- Severity: High (information disclosure) | Priority: P1 | Status: Open
- Steps: while logged in as zam, open https://py.softlandindia.net/dine_flash_buffet/company/users_list/ (a wrong address; the correct one is user_list).
- Expected: A plain "Page not found" page.
- Actual: A technical page titled "Page not found (404)" that says "Using the URLconf defined in caller_on.urls, Django tried these URL patterns" and lists the internal addresses of the whole site (api/login, api/token/refresh, admin, vendors, manager and more). This means the server is running in debug mode.
- Impact: Gives attackers a map of the application and may leak settings on server errors.
- Fix: Turn debug mode off on the live server (DEBUG = False) and show a normal error page.
- Automated test: tests/test_nonfunctional_web.py::test_unknown_page_does_not_show_debug_info (and the company page version).
