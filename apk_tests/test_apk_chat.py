"""
CHAT (Active Chats) - Food On Demand manager APK.
Screen seen in the screenshots: title "Active Chats", "Talk to guests", search box, chips
(All / Unread / Awaiting reply / Replied), "N chats", chat cards (guest name, Order #n, Booking, Table,
last message "Guest: ..." or "Manager: ...", time, QR and chat icons).

Sending a real message changes QA data, so that test only runs when RUN_DATA_TESTS=1 is set.
"""
import os
import re
import time
import pytest

import ui

MODULE = "Chat"
TITLE = "Active Chats"
DATA_TESTS = os.getenv("RUN_DATA_TESTS") == "1"


@pytest.fixture
def chats(home):
    assert ui.open_screen(home, "Chat", TITLE), "Chat tab did not open the 'Active Chats' screen"
    time.sleep(3)
    return home


def test_chat_screen_title(chats):
    """Open the Chat tab.
    Expected: the 'Active Chats' screen is shown with the line 'Talk to guests'."""
    assert ui.has_text(chats, TITLE) and ui.has_text(chats, "Talk to guests")


def test_chat_network_and_server_status_shown(chats):
    """Look at the top right.
    Expected: Network and Server indicators are shown."""
    assert ui.has_text(chats, "Network") and ui.has_text(chats, "Server")


def test_chat_search_box_present(chats):
    """Look at the search area.
    Expected: a search box for order, guest, table or message is present."""
    assert len(chats.find_elements("class name", "android.widget.EditText")) >= 1


@pytest.mark.parametrize("chip", ["All", "Unread", "Awaiting reply"])
def test_chat_filter_chips_present(chats, chip):
    """Look at the chips.
    Expected: All, Unread and Awaiting reply chips are shown with counts."""
    assert ui.chip_count(chats, chip) is not None, f"Chip '{chip}' with a count was not found"


def test_chat_all_chip_matches_list_label(chats):
    """Compare the All chip with the 'N chats' label.
    Expected: both numbers are the same."""
    assert ui.chip_count(chats, "All") == ui.list_count(chats, "chat")


def test_chat_cards_show_order_booking_table(chats):
    """Look at the first chat card.
    Expected: it shows the guest name, Order #n, Booking number and Table."""
    ts = " | ".join(ui.texts(chats))
    if ui.list_count(chats, "chat") in (0, None):
        pytest.skip("No chats today")
    assert re.search(r"Order #\d+", ts) and re.search(r"Booking \d+", ts) and re.search(r"Table \d+", ts)


def test_chat_cards_show_last_message_sender(chats):
    """Look at the last message line on each card.
    Expected: it starts with 'Guest:' or 'Manager:'."""
    if ui.list_count(chats, "chat") in (0, None):
        pytest.skip("No chats today")
    assert any(t.startswith(("Guest:", "Manager:")) for t in ui.texts(chats))


def test_chat_unread_filter_matches_count(chats):
    """Tap the Unread chip.
    Expected: the 'N chats' label equals the number on the chip."""
    n = ui.chip_count(chats, "Unread")
    ui.tap_text(chats, [t for t in ui.texts(chats) if t.lower().startswith("unread")][0])
    time.sleep(2)
    assert (ui.list_count(chats, "chat") or 0) == (n or 0)


def test_chat_awaiting_reply_filter_matches_count(chats):
    """Tap the Awaiting reply chip.
    Expected: the 'N chats' label equals the number on the chip."""
    n = ui.chip_count(chats, "Awaiting reply")
    ui.tap_text(chats, [t for t in ui.texts(chats) if t.lower().startswith("awaiting")][0])
    time.sleep(2)
    assert (ui.list_count(chats, "chat") or 0) == (n or 0)


def test_chat_search_no_match(chats):
    """Search for text that does not exist (zzzzqqq).
    Expected: no chats are listed and the app does not crash."""
    ui.tap(chats, chats.find_elements("class name", "android.widget.EditText")[0])
    ui.type_text("zzzzqqq")
    time.sleep(2)
    ui.hide_keyboard()
    assert (ui.list_count(chats, "chat") or 0) == 0


def test_chat_search_by_guest_name(chats):
    """Search for part of an existing guest name (Renj).
    Expected: matching chats remain."""
    before = ui.list_count(chats, "chat") or 0
    if before == 0:
        pytest.skip("No chats today")
    ui.tap(chats, chats.find_elements("class name", "android.widget.EditText")[0])
    ui.type_text("Renj")
    time.sleep(2)
    ui.hide_keyboard()
    assert 1 <= (ui.list_count(chats, "chat") or 0) <= before


def test_chat_open_conversation(chats):
    """Tap the first chat card.
    Expected: the conversation opens (the 'Active Chats' list is replaced); Back returns to the list."""
    if (ui.list_count(chats, "chat") or 0) == 0:
        pytest.skip("No chats today")
    name = [t for t in ui.texts(chats) if re.fullmatch(r"Order #\d+", t)][0]
    ui.tap_text(chats, name)
    time.sleep(3)
    assert not ui.has_text(chats, "Talk to guests"), "Conversation did not open"
    ui.press_back()
    time.sleep(2)
    assert ui.has_text(chats, TITLE)


@pytest.mark.skipif(not DATA_TESTS, reason="Sends a real chat message - set RUN_DATA_TESTS=1 to run")
def test_chat_manager_can_send_message(chats):
    """Open the first chat, type 'AUTO-TEST hello' and send.
    Expected: the message appears in the conversation as a Manager message."""
    name = [t for t in ui.texts(chats) if re.fullmatch(r"Order #\d+", t)][0]
    ui.tap_text(chats, name)
    time.sleep(3)
    box = chats.find_elements("class name", "android.widget.EditText")
    assert box, "No message box in the conversation"
    ui.tap(chats, box[0])
    ui.type_text("AUTO-TEST hello")
    ui.hide_keyboard()
    sends = [e for e in chats.find_elements("class name", "android.widget.ImageButton")]
    assert sends, "No send button found"
    ui.tap(chats, sends[-1])
    time.sleep(3)
    assert ui.has_text_like(chats, "AUTO-TEST hello")


def test_chat_back_returns_to_home(chats):
    """Press Back on Active Chats.
    Expected: back on the Home dashboard."""
    ui.press_back()
    time.sleep(2)
    assert ui.on_dashboard(chats)
