"""
REPORTS (Order Report) - Food On Demand manager APK.
Screen seen in the screenshots: title "Order Report", "Today's buffet orders", six tiles
(TOTAL, CREATED, PREPARING, READY, SERVED, CANCELLED), search box, chips (All / Created / Ready ...),
"N orders", token cards (Token #n, time, Counter, status badge, TABLE BOOKING n, N CALLS, guest, items).
"""
import re
import time
import pytest

import ui

MODULE = "Reports"
TITLE = "Order Report"
TILES = ["TOTAL", "CREATED", "PREPARING", "READY", "SERVED", "CANCELLED"]


@pytest.fixture
def report(home):
    assert ui.open_screen(home, "Reports", TITLE), "Reports tab did not open the 'Order Report' screen"
    time.sleep(4)
    return home


def test_report_screen_title(report):
    """Open the Reports tab.
    Expected: the 'Order Report' screen with 'Today's buffet orders' is shown."""
    assert ui.has_text(report, TITLE) and ui.has_text_like(report, "buffet orders")


@pytest.mark.parametrize("tile", TILES)
def test_report_summary_tiles_present(report, tile):
    """Look at the summary tiles.
    Expected: each status tile shows a number."""
    assert ui.number_before(report, tile) is not None, f"Tile {tile} has no number"


def test_report_tiles_add_up_to_total(report):
    """Add Created + Preparing + Ready + Served + Cancelled.
    Expected: the sum equals TOTAL."""
    total = ui.number_before(report, "TOTAL")
    parts = [ui.number_before(report, t) or 0 for t in TILES[1:]]
    assert sum(parts) == total, f"Tiles {dict(zip(TILES[1:], parts))} add up to {sum(parts)}, TOTAL says {total}"


def test_report_total_matches_dashboard(home):
    """Compare TOTAL on Report with TOTAL on Home.
    Expected: same number."""
    total = int(home.find_element(*ui.by_id("tv_stat_total")).text)
    assert ui.open_screen(home, "Reports", TITLE)
    time.sleep(4)
    assert ui.number_before(home, "TOTAL") == total


def test_report_served_matches_dashboard(home):
    """Compare SERVED on Report with SERVED on Home.
    Expected: same number on both screens."""
    served = int(home.find_element(*ui.by_id("tv_stat_served")).text)
    assert ui.open_screen(home, "Reports", TITLE)
    time.sleep(4)
    assert ui.number_before(home, "SERVED") == served, \
        f"Home says {served} served, Report says {ui.number_before(home, 'SERVED')}"


def test_report_status_matches_orders_screen(home):
    """Compare the Ready count on Orders with READY on Report.
    Expected: the same number of ready orders on both screens."""
    assert ui.open_screen(home, "Orders", "All Requests")
    time.sleep(3)
    ready_orders = ui.chip_count(home, "Ready")
    ui.press_back()
    time.sleep(2)
    assert ui.open_screen(home, "Reports", TITLE)
    time.sleep(4)
    assert ui.number_before(home, "READY") == ready_orders, \
        f"Orders screen: {ready_orders} ready, Report: {ui.number_before(home, 'READY')}"


def test_report_all_chip_matches_list_label(report):
    """Compare the All chip with the 'N orders' label.
    Expected: same number."""
    assert ui.chip_count(report, "All") == ui.list_count(report, "order")


def test_report_all_chip_matches_total(report):
    """Compare the All chip with TOTAL.
    Expected: same number."""
    assert ui.chip_count(report, "All") == ui.number_before(report, "TOTAL")


def test_report_cards_show_token_counter_status(report):
    """Look at the first card.
    Expected: Token #n, a Counter, a status badge and a calls count are shown."""
    ts = ui.texts(report)
    assert any(re.fullmatch(r"Token #\d+", t) for t in ts), "No token card"
    assert any("Counter" in t for t in ts)
    assert any(re.fullmatch(r"\d+ CALLS?", t, re.I) for t in ts)


def test_report_card_expands_items(report):
    """Tap a card with several items.
    Expected: the item lines (Counter x qty, notes, status) are listed."""
    ui.tap_text(report, [t for t in ui.texts(report) if re.fullmatch(r"\d+ items?", t, re.I)][0])
    time.sleep(2)
    assert any(re.search(r"x\d+", t) for t in ui.texts(report)), "Item lines were not shown"


def test_report_search_no_match(report):
    """Search for a token that does not exist (99999).
    Expected: no orders are listed."""
    ui.tap(report, report.find_elements("class name", "android.widget.EditText")[0])
    ui.type_text("99999")
    time.sleep(2)
    ui.hide_keyboard()
    assert (ui.list_count(report, "order") or 0) == 0


def test_report_search_by_token(report):
    """Search for an existing token number (5).
    Expected: at least that order is listed."""
    ui.tap(report, report.find_elements("class name", "android.widget.EditText")[0])
    ui.type_text("5")
    time.sleep(2)
    ui.hide_keyboard()
    assert (ui.list_count(report, "order") or 0) >= 1


def test_report_created_filter_matches_chip(report):
    """Tap the Created chip.
    Expected: the 'N orders' label equals the chip number."""
    n = ui.chip_count(report, "Created")
    if not n:
        pytest.skip("No created orders")
    ui.tap_text(report, [t for t in ui.texts(report) if t.lower().startswith("created")][0])
    time.sleep(2)
    assert ui.list_count(report, "order") == n


def test_report_back_returns_to_home(report):
    """Press Back on Order Report.
    Expected: back on Home."""
    ui.press_back()
    time.sleep(2)
    assert ui.on_dashboard(report)
