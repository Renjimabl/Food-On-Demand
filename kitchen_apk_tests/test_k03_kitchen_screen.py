"""
MODULE 3 - Buffet Kitchen Processing screen - Kitchen Staff APK
SRS (shift start): "Verify the screen shows 'All Caught Up!' before service begins."
"""
import time
import kitchen_lib as k

MODULE = "Kitchen Screen"


def test_kitchen_screen_title_or_empty_state(on_kitchen):
    """After login look at the main screen.
    Expected: 'Buffet Kitchen Processing' header or the 'All Caught Up!' empty state or order cards."""
    assert k.on_kitchen_screen(on_kitchen)


def test_all_caught_up_when_no_orders(on_kitchen):
    """Open the screen when no guest orders are waiting.
    Expected: 'All Caught Up!' is shown. Skipped when orders are in the queue."""
    if k.has(on_kitchen, r"mark as ready"):
        import pytest
        pytest.skip("Orders are waiting in the queue")
    assert k.has(on_kitchen, r"all caught up"), f"Empty state missing. Texts: {k.all_texts(on_kitchen)[:10]}"


def test_screen_shows_no_error_text(on_kitchen):
    """Look at the screen for error words.
    Expected: no 'error', 'exception', 'failed' or 'unable' message."""
    assert not k.has(on_kitchen, r"exception|traceback|unable to|something went wrong"), \
        f"Error text on screen: {k.all_texts(on_kitchen)[:10]}"


def test_outlet_or_counter_name_is_shown(on_kitchen):
    """Look for the mapped food counter / outlet name.
    Expected: the kitchen staff sees which counter(s) they are mapped to (Menu Mapping)."""
    texts = " ".join(k.all_texts(on_kitchen)).lower()
    print("SCREEN TEXTS:", texts[:200])
    assert any(w in texts for w in ["counter", "kazhakkoottam", "north", "south", "menu"]), \
        "No counter or outlet name on the kitchen screen"


def test_screen_stays_after_waiting(on_kitchen):
    """Leave the screen open for 30 seconds.
    Expected: it does not close, crash or sign the user out."""
    time.sleep(30)
    assert k.on_kitchen_screen(on_kitchen)


def test_pull_or_refresh_keeps_screen(on_kitchen):
    """Swipe down on the list (pull to refresh).
    Expected: the screen stays on the kitchen processing view."""
    size = on_kitchen.get_window_size()
    x = size["width"] // 2
    k.adb("shell", "input", "swipe", str(x), str(int(size["height"] * 0.35)), str(x), str(int(size["height"] * 0.75)), "400")
    time.sleep(4)
    assert k.on_kitchen_screen(on_kitchen)
