"""
MODULE 4 - Order cards - Kitchen Staff APK
SRS (kitchen processing): a new order card appears when a guest submits an order (red border = Created).
Staff read the Note field, prepare the item, then click Mark as Ready.

These tests need at least one order in the queue. Place a guest order from the table QR first
(Customer Journey). With an empty queue every test here is skipped.
"""
import re
import pytest
import kitchen_lib as k

MODULE = "Order Cards"


@pytest.fixture
def with_orders(on_kitchen):
    if not k.has(on_kitchen, r"mark as ready"):
        pytest.skip("No orders in the queue - place a guest order first")
    return on_kitchen


def test_card_has_mark_as_ready_button(with_orders):
    """Look at the first order card.
    Expected: a 'Mark as Ready' button."""
    assert k.has(with_orders, r"mark as ready")


def test_card_shows_token_number(with_orders):
    """Look for the guest's token number on the card.
    Expected: the word 'Token' followed by a number."""
    assert k.has(with_orders, r"token\s*(no\.?|number|#)?\s*:?\s*\d+"), \
        f"No token number. Texts: {k.all_texts(with_orders)[:12]}"


def test_card_shows_table_number(with_orders):
    """Look for the table number on the card.
    Expected: the word 'Table' followed by a number."""
    assert k.has(with_orders, r"table\s*(no\.?|number|#)?\s*:?\s*\d+"), \
        f"No table number. Texts: {k.all_texts(with_orders)[:12]}"


def test_card_shows_item_and_quantity(with_orders):
    """Look for the food item name and quantity.
    Expected: an item name and a quantity such as x2 / Qty 2 / 2 x."""
    assert k.has(with_orders, r"x\s*\d+|qty\s*:?\s*\d+|\d+\s*x"), \
        f"No quantity. Texts: {k.all_texts(with_orders)[:12]}"


def test_card_shows_note_field(with_orders):
    """Look for the Note on the card (guest's customisation).
    Expected: a 'Note' label (empty value allowed)."""
    assert k.has(with_orders, r"note"), f"No Note field. Texts: {k.all_texts(with_orders)[:12]}"


def test_card_shows_status_created(with_orders):
    """Look at the status of a new order.
    Expected: status text such as Created / New / Pending."""
    assert k.has(with_orders, r"created|new|pending"), f"No status. Texts: {k.all_texts(with_orders)[:12]}"


def test_only_mapped_counters_orders_are_shown(with_orders):
    """Look at counter names on the cards.
    Expected: only counters mapped to this kitchen user (Menu Mapping) appear."""
    print("CARD TEXTS:", k.all_texts(with_orders)[:20])
    assert not k.has(with_orders, r"unmapped|not assigned")


def test_oldest_order_is_first(with_orders):
    """Compare token numbers from top to bottom.
    Expected: orders are listed oldest (smallest token) first."""
    tokens = [int(m.group(1)) for t in k.all_texts(with_orders)
              for m in [re.search(r"token\D*(\d+)", t, re.I)] if m]
    print("TOKENS ON SCREEN:", tokens)
    if len(tokens) < 2:
        pytest.skip("Fewer than two cards on screen")
    assert tokens == sorted(tokens), f"Cards are not oldest first: {tokens}"
