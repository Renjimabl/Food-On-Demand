# Manager APK - Test Scenarios (Food On Demand v1.0.1, outlet "zam", user buffet)

Legend: **A** = automated in `apk_tests`, **M** = manual (needs a second device, a real order, or a system setting),
**P** = pending - the screen has not been seen yet (need a screenshot / SRS section).

## 1. Activation and Login  (test_apk_login.py)  - A
Customer ID entry, wrong / blank / short ID, valid login (buffet/123), wrong password, blank fields, SQL/script text,
case-sensitive password, spaces around username, password masked, show-password toggle, texts on screen.

## 2. Home / Dashboard  (test_apk_dashboard.py)  - A
Greeting, outlet name, Today's Overview, TOTAL / ACTIVE / SERVED numbers, TOTAL >= ACTIVE+SERVED, quick actions
(Create Order, View Orders, Chat, Report, Settings), bottom tabs, version + device ID footer, Refresh, logout pop-up
(content, Cancel, Back), tab navigation both ways.

## 3. Orders - "All Requests"  (test_apk_orders.py)  - A
Title, Network/Server dots, search box, chips All/Preparing/Ready/Served with counts, "N orders" = All chip,
Home TOTAL = All chip, chip counts add up, card fields (Order #, TABLE, guest), newest first, Ready filter,
search no-match / by number / special characters, Back, cancelled item handling, rotation.
Manual: QR icon opens the QR / token, chat icon opens that order's chat, filter button options, pull to refresh,
card updates live when the kitchen marks an item ready.

## 4. Chat - "Active Chats"  (test_apk_chat.py)  - A
Title, status dots, search, chips All/Unread/Awaiting reply (+ Replied), "N chats" = All chip, card fields
(Order, Booking, Table, last message sender), Unread and Awaiting filters, search no-match / by guest, open a
conversation and Back, send a message (only with `RUN_DATA_TESTS=1`).
Manual: guest-side reply arrives and shows as Unread; unread badge clears after opening; push notification for a
new guest message; message with emoji / very long text.

## 5. Reports - "Order Report"  (test_apk_reports.py)  - A
Title, six tiles, tiles add up to TOTAL, Report TOTAL / SERVED / READY = Home / Orders screens (cross-screen
consistency), All chip = TOTAL, card fields (Token, Counter, calls), expand items, search, Created filter, Back.
Manual: filter button (date range / counter), export or share, calls counter increases after a manager call.

## 6. Create Order (take an order)  - P
Screen not yet seen. Planned scenarios: choose table, guest name / phone, pick counters and items, quantity
+/-, notes ("sugar", "pepper"), blank table / no item validation, create -> token number shown -> appears in
Orders, Report, Home TOTAL (+1) and in the Kitchen app; cancel before submit; double tap Create; order for a
booked table; large quantity.

## 7. Settings  - P
Screen not yet seen. Planned: each setting opens, change and persist after restart, language / theme, about,
device ID, change password (if present), logout.

## 8. End-to-end flows
| # | Flow | Status |
|---|---|---|
| E1 | Login -> Home -> Orders -> Chat -> Reports -> Home -> Logout | A (tabs) |
| E2 | Create Order -> appears in Orders, Report, Home TOTAL +1 | P (needs Create Order screen) |
| E3 | Manager creates order -> Kitchen app shows card -> Kitchen marks Ready -> Manager Orders shows Ready/Served | M (two apps / two phones) |
| E4 | Guest scans table QR, orders -> manager sees order and chat; manager replies -> guest sees reply | M |
| E5 | Cancel an item -> Orders shows "1 CANCELLED", Report counts it as Cancelled | P/M |
| E6 | Logout -> reopen app -> login asked (BUG-APK-01 currently fails) | A |

## 9. Non-functional (manual / partly automated)
Rotation (A on Orders), Wi-Fi off/on, lock screen, force-stop and reopen, low battery, slow network, large font,
Android versions 8..latest, tablet size, HTTPS only, no tokens in logcat, back-stack behaviour.

## Candidate bugs seen in the screenshots (to confirm by running)
1. **Counts differ between screens at the same minute** - Home 5 total / 1 active / 3 served; Orders chips
   Preparing 1 / Ready 2 / Served 1; Order Report Created 4 / Ready 1 / Served 0. (`test_report_served_matches_dashboard`,
   `test_report_status_matches_orders_screen`)
2. **Same order, different status** - Order #4 is "2/3 SERVED, 2 READY, 1 CANCELLED" on Orders but "CREATED" on Report.
3. **Guest name typos in data** ("Renjina" vs "Renjima") - data issue, not app.
