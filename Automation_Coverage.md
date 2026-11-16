# Food On Demand - Automation Coverage (as of 11-Nov-2026)
Basis: Food demand user manual + Food_on_Demand_Test_Cases.xlsx (504 manual cases) + the admin sidebar.
Counts below are test functions (some run several times with different data).

## A. Web admin portal (Playwright, in tests/)

| # | Module | Status | File | What is done | What is pending |
|---|--------|--------|------|--------------|-----------------|
| 1 | Login and Auth | Done (basic) | test_login.py (8) | Valid / invalid / injection / Enter key / forgot link | Reset-password flow, license-expired message, session timeout, logout then Back button |
| 2 | Company Dashboard | Not done | - | - | Welcome text, Outlets count, header "zam (ID: 0711)", license-expiry banner, menu items |
| 3 | Users (New User, Users List) | Mostly done | test_kitchen_flow.py (21) | Create kitchen + outlet manager, validation, duplicate, list | Users List actions (Unassign User from Outlet), edit user, role / outlet combinations |
| 4 | Menu Mapping | Done (basic) | test_kitchen_flow.py | Map kia, save without user | Several menus, unmap, remap, outlet with no menu |
| 5 | Add Menu (food counter) | Done | test_add_menu.py (15) | Create veg / non veg / inactive, required, duplicate, XSS, long name, option add | Edit menu, delete menu, images upload, pre-announcement and service-time effect |
| 6 | Manage Food Menu (list) | Partly | test_add_menu.py | Row visible, Active | Filters (All Outlets / All Status), edit and delete from list, sorting, empty state |
| 7 | Manage Options (menu options add / edit / delete) | Not done | - | - | Add, edit, delete with confirm, Active / Inactive badge |
| 8 | Banners | Done (basic) | test_banners.py (6) | Page, valid upload, no file, wrong file type, Select All | Several images, jpg / webp, big file, delete selected, size limit |
| 9 | Banner Profiles (4 pages) | Done, not run yet | test_banner_profiles.py (35) | New Profile, list, row actions (view / edit / cancel delete), map, mapped list | Real edit save, real delete, unassign, several slots, other roles |
| 10 | Outlet List and Update Outlet | Not done | - | - | Outlet cards, edit form, Update Outlet Data, validation |
| 11 | Table QR Generator | Not done | - | - | Outlet, table number (positive integer), Generate QR, Copy URL, Download, Print, bad numbers |
| 12 | Android Tabs (kitchen devices) | Not done | - | - | Device list, status, actions |
| 13 | Manager Devices | Not done | - | - | Device list, status, actions |
| 14 | Analytics: Total Orders, Order Details | Not done | - | - | Totals cards, Booking Details filters (token, status), empty state |
| 15 | Super Admin (Register Restaurant, Restaurant List, Create Outlet) | Not done | - | - | Needs a Super Admin login (not shared) |
| 16 | Non-functional (speed, layout on phone / tablet, browsers, accessibility, security headers) | Not done | - | - | Mobile viewport, Firefox / WebKit run, page-load times, keyboard use |

## B. Guest ordering (mobile web opened from the table QR) - NOT STARTED
Biggest gap. About 94 manual cases. Needs the QR link from Table QR Generator and a mobile browser.
Pending: open QR link, counter list, Veg / Non Veg filter, search, + / - quantity, bottom bar, place order, token and tracking screen, ready notification, Place Another Order, invalid / old QR, session table number.

## C. Kitchen operations - BLOCKED
Kitchen Staff cannot sign in on the web login (BUG-01), so Buffet Kitchen Processing ("All Caught Up!", Mark as Ready, order card colours, notes) cannot be automated until the developer confirms where kitchen staff sign in (probably the KitchenStaff Android app).

## D. Android apps
| App | Status | Pending |
|-----|--------|---------|
| Manager app FoodOnDemand_QA_v1.0.1 | Code written (test_apk_login.py 17, test_apk_dashboard.py 13) but not running: Appium helper crashes on the vivo phone | Create Order, View Orders, Chat, Reports, Settings screens, Send alert by token; needs a stable phone or emulator |
| Kitchen Staff app KitchenStaff_QA_v2.0.0 | Not started | Customer ID, login, Buffet Kitchen Processing, Mark as Ready, All Caught Up |

## E. Things that block or risk the automation
1. License banner on the dashboard says "License will expire in 1 day" (11-Nov-2026). When it expires, logins may stop and every test will fail. Get the license renewed first.
2. Appium helper crashes on the vivo phone (use an emulator or another phone).
3. Kitchen / outlet staff web login (BUG-01) needs a developer answer.
4. Super Admin credentials are needed for module 15.

## F. Suggested order for the pending work
1. Company Dashboard (small, quick)
2. Table QR Generator (needed for the guest flow)
3. Outlet List / Update Outlet
4. Manage Options and Manage Food Menu list actions
5. Guest ordering (mobile web)
6. Analytics: Total Orders / Order Details
7. Android Tabs and Manager Devices pages
8. Reset password, users list actions
9. Kitchen operations (after BUG-01 is answered)
10. Super Admin, then non-functional checks


---
## UPDATE 11-Nov-2026 - pending web modules now written (not yet run)
| Module | New file | Tests |
|--------|----------|-------|
| Company Dashboard + sidebar + logout | tests/test_dashboard.py | 20 |
| Table QR Generator | tests/test_table_qr.py | 13 |
| Outlet List + Update Outlet | tests/test_outlets.py | 9 |
| Manage Food Menu list (filters, search, paging) | tests/test_menu_list.py | 12 |
| Android Tabs + Manager Devices | tests/test_devices.py | 15 |
| Analytics (Total Orders, Order Details) | tests/test_analytics.py | 17 |
| Non-functional (access control, debug page, phone layout, speed, keyboard) | tests/test_nonfunctional_web.py | 30 |
Whole web suite now collects 226 tests.

Still not automated on the web: Super Admin (needs login), guest ordering from the table QR, Manage Options (add / edit / delete inside a menu), reset-password flow, Users List unassign, kitchen operations (blocked by BUG-01).
