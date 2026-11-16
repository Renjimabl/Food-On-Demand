"""
MODULE 5 - Mark as Ready - Kitchen Staff APK
SRS: locate the order card, verify token and table number, click 'Mark as Ready', confirm the card is removed.
WARNING: this changes real orders on the QA server. Run only with test orders in the queue.
Each test skips when the queue is empty.
"""
import re
import time
import pytest
import kitchen_lib as k

MODULE = "Mark as Ready"


def cards(d):
    return d.find_elements(*k.by_text_regex(r"mark as ready"))


@pytest.fixture
def with_orders(on_kitchen):
    if not cards(on_kitchen):
        pytest.skip("No orders in the queue - place a guest order first")
    return on_kitchen


def test_mark_ready_removes_the_card(with_orders):
    """Tap 'Mark as Ready' on the first card.
    Expected: that card disappears from the active queue (one card fewer, or All Caught Up)."""
    before = len(cards(with_orders))
    k.tap(cards(with_orders)[0])
    time.sleep(2)
    for confirm in (r"^yes$", r"^confirm$", r"^ok$"):  # a confirmation pop-up, if the app has one
        if k.has(with_orders, confirm):
            k.tap_text(with_orders, confirm)
            break
    time.sleep(4)
    after = len(cards(with_orders))
    assert after == before - 1, f"Cards before={before}, after={after}"


def test_ready_order_does_not_return_after_refresh(with_orders):
    """Mark the first card ready, then close and reopen the app.
    Expected: the finished order does not come back in the queue."""
    before = len(cards(with_orders))
    k.tap(cards(with_orders)[0])
    time.sleep(4)
    k.force_stop(); k.launch(); time.sleep(10)
    assert len(cards(with_orders)) <= before - 1, "A finished order came back after restart"


def test_double_tap_marks_only_one_order(with_orders):
    """Tap 'Mark as Ready' twice quickly.
    Expected: only one order is finished (the next card is not marked by accident)."""
    before = len(cards(with_orders))
    if before < 2:
        pytest.skip("Needs at least two orders in the queue")
    btn = cards(with_orders)[0]
    k.tap(btn)
    k.tap(btn)
    time.sleep(4)
    assert len(cards(with_orders)) >= before - 1, "Two orders disappeared after a double tap"


def test_empty_state_after_last_order(on_kitchen):
    """Mark every remaining order ready.
    Expected: 'All Caught Up!' appears when the queue is empty."""
    if not cards(on_kitchen):
        pytest.skip("No orders in the queue")
    for _ in range(15):
        if not cards(on_kitchen):
            break
        k.tap(cards(on_kitchen)[0])
        time.sleep(3)
    assert k.has(on_kitchen, r"all caught up")
