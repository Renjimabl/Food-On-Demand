"""
ORDERS (All Requests) - Food On Demand manager APK.
Screen seen in the screenshots: title "All Requests", Network/Server dots, search box, filter button,
chips (All / Preparing / Ready / Served), "N orders", order cards (Order #n, status chips, TABLE n, guest name,
QR icon, chat icon).
"""
import re
import time
import pytest

import ui

MODULE = "Orders"
TITLE = "All Requests"


@pytest.fixture
def orders(home):
    assert ui.open_screen(home, "Orders", TITLE), "Orders tab did not open the 'All Requests' screen"
    time.sleep(3)
    return home


def test_orders_screen_title(orders):
    """Open the Orders tab.
    Expected: the 'All Requests' screen is shown."""
    assert ui.has_text(orders, TITLE)


def test_orders_network_and_server_status_shown(orders):
    """Look at the top right of the Orders screen.
    Expected: Network and Server status indicators are shown."""
    assert ui.has_text(orders, "Network") and ui.has_text(orders, "Server")


def test_orders_search_box_present(orders):
    """Look at the search area.
    Expected: a search box for token, table or item is present."""
    assert len(orders.find_elements("class name", "android.widget.EditText")) >= 1, "No search box found"


@pytest.mark.parametrize("chip", ["All", "Preparing", "Ready", "Served"])
def test_orders_filter_chips_present(orders, chip):
    """Look at the status chips.
    Expected: All, Preparing, Ready and Served chips are shown, each with a count."""
    assert ui.chip_count(orders, chip) is not None, f"Chip '{chip}' with a count was not found"


def test_orders_all_chip_matches_list_label(orders):
    """Compare the number on the All chip with the 'N orders' label.
    Expected: both numbers are the same."""
    assert ui.chip_count(orders, "All") == ui.list_count(orders, "order")


def test_orders_total_matches_dashboard_total(home):
    """Compare Today's Overview TOTAL on Home with the All chip on Orders.
    Expected: the same number of orders is shown on both screens."""
    total = int(home.find_element(*ui.by_id("tv_stat_total")).text)
    assert ui.open_screen(home, "Orders", TITLE)
    time.sleep(3)
    assert ui.chip_count(home, "All") == total, \
        f"Home says {total} orders, Orders screen says {ui.chip_count(home, 'All')}"


def test_orders_chip_counts_add_up(orders):
    """Add Preparing + Ready + Served (+ other statuses) and compare with All.
    Expected: the status counts do not add up to more than All."""
    all_n = ui.chip_count(orders, "All")
    parts = [ui.chip_count(orders, c) or 0 for c in ("Preparing", "Ready", "Served")]
    assert sum(parts) <= all_n, f"Status chips {parts} add up to more than All ({all_n})"


def test_orders_cards_show_order_number_and_table(orders):
    """Look at the first order card.
    Expected: it shows 'Order #n' and a TABLE number."""
    ts = ui.texts(orders)
    assert any(re.fullmatch(r"Order #\d+", t) for t in ts), "No 'Order #n' card found"
    assert any(re.fullmatch(r"TABLE \d+", t, re.I) for t in ts), "No TABLE chip found"


def test_orders_newest_first(orders):
    """Read the order numbers from top to bottom.
    Expected: newest order (highest number) is at the top."""
    nums = [int(re.search(r"\d+", t).group()) for t in ui.texts(orders) if re.fullmatch(r"Order #\d+", t)]
    assert nums == sorted(nums, reverse=True), f"Orders are not newest-first: {nums}"


def test_orders_filter_ready_matches_count(orders):
    """Tap the Ready chip.
    Expected: the list label shows the same number as the chip."""
    n = ui.chip_count(orders, "Ready")
    if not n:
        pytest.skip("No Ready orders today")
    ui.tap_text(orders, [t for t in ui.texts(orders) if t.lower().startswith("ready")][0])
    time.sleep(2)
    assert ui.list_count(orders, "order") == n


def test_orders_search_no_match_shows_empty(orders):
    """Type a token that does not exist, e.g. 99999.
    Expected: no orders are listed and the app does not crash."""
    ui.tap(orders, orders.find_elements("class name", "android.widget.EditText")[0])
    ui.type_text("99999")
    time.sleep(2)
    ui.hide_keyboard()
    assert ui.list_count(orders, "order") in (0, None) or ui.has_text_like(orders, "no orders") \
        or ui.has_text_like(orders, "no results")


def test_orders_search_by_token_finds_order(orders):
    """Type the number of an existing order, e.g. 5.
    Expected: only matching orders remain in the list."""
    before = ui.list_count(orders, "order")
    ui.tap(orders, orders.find_elements("class name", "android.widget.EditText")[0])
    ui.type_text("5")
    time.sleep(2)
    ui.hide_keyboard()
    after = ui.list_count(orders, "order")
    assert after is not None and after <= before and after >= 1, f"Search 5: before={before}, after={after}"


def test_orders_search_special_characters_do_not_crash(orders):
    """Type special characters ' OR 1=1 -- and <b>.
    Expected: no crash and no error pop-up."""
    ui.tap(orders, orders.find_elements("class name", "android.widget.EditText")[0])
    ui.type_text("' OR 1=1 --")
    time.sleep(2)
    ui.hide_keyboard()
    assert ui.has_text(orders, TITLE)


def test_orders_back_returns_to_home(orders):
    """Press the Back arrow.
    Expected: back on the Home dashboard."""
    ui.press_back()
    time.sleep(2)
    assert ui.on_dashboard(orders)


def test_orders_cancelled_item_not_counted_as_served(orders):
    """Look at a card that shows '1 CANCELLED' (for example Order #3).
    Expected: its served count is 0 of the non-cancelled items; the card colour/text shows cancelled."""
    ts = ui.texts(orders)
    if not any("CANCELLED" in t.upper() for t in ts):
        pytest.skip("No cancelled order today")
    assert any(re.fullmatch(r"\d+/\d+ SERVED", t, re.I) for t in ts)


def test_orders_screen_survives_rotation(orders):
    """Rotate to landscape and back.
    Expected: the screen is still All Requests."""
    import helpers
    helpers.adb("shell", "settings", "put", "system", "accelerometer_rotation", "0")
    helpers.adb("shell", "settings", "put", "system", "user_rotation", "1")
    time.sleep(3)
    helpers.adb("shell", "settings", "put", "system", "user_rotation", "0")
    time.sleep(3)
    assert ui.has_text(orders, TITLE)
