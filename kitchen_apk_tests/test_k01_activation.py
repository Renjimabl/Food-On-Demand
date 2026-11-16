"""
MODULE 1 - Activation (Customer ID screen) - Kitchen Staff APK
SRS: the device is activated with the company's 4-digit Customer ID before the login screen.
If the Kitchen app has no Customer ID screen, these tests skip.
"""
import time
import pytest
import kitchen_lib as k

MODULE = "Activation"


def need_activation_screen(d):
    if not k.on_customer_id_screen(d):
        pytest.skip("This build does not show a Customer ID screen first")


def test_first_screen_is_customer_id_or_login(first_screen):
    """Open the app after clearing its data.
    Expected: the Customer ID screen (or the login screen) is shown, not a blank or crashed screen."""
    assert k.on_customer_id_screen(first_screen) or k.on_login_screen(first_screen), \
        f"Neither Customer ID nor login shown. Texts: {k.all_texts(first_screen)[:8]}"


def test_customer_id_screen_has_boxes_and_button(first_screen):
    """Look at the Customer ID screen.
    Expected: input box(es) for the 4 digits and an activate / check button."""
    need_activation_screen(first_screen)
    assert len(k.edit_boxes(first_screen)) >= 1
    assert k.has(first_screen, k.ACTIVATE_BUTTON)


def test_app_version_is_shown(first_screen):
    """Look at the bottom of the first screen.
    Expected: the app version (2.0.0) is displayed."""
    assert k.has(first_screen, r"2\.0\.0|version"), f"No version text. Texts: {k.all_texts(first_screen)[:8]}"


def test_empty_customer_id_rejected(first_screen):
    """Tap the activate button with no ID entered.
    Expected: the app stays on the Customer ID screen and does not reach the login screen."""
    need_activation_screen(first_screen)
    k.tap_text(first_screen, k.ACTIVATE_BUTTON)
    time.sleep(4)
    assert not k.on_login_screen(first_screen), "Empty Customer ID reached the login screen"


@pytest.mark.parametrize("bad_id", ["9999", "0000", "12", "abcd"])
def test_wrong_customer_id_rejected(first_screen, bad_id):
    """Enter a wrong Customer ID and activate.
    Expected: the app does not move on to the login screen."""
    need_activation_screen(first_screen)
    k.enter_customer_id(first_screen, bad_id)
    time.sleep(10)
    assert not k.on_login_screen(first_screen), f"Customer ID '{bad_id}' was accepted"


def test_valid_customer_id_reaches_login(first_screen):
    """Enter the valid Customer ID (from kitchen.env) and activate.
    Expected: the login screen is shown."""
    need_activation_screen(first_screen)
    import conftest
    k.enter_customer_id(first_screen, conftest.CID)
    assert k.wait_text(first_screen, k.LOGIN_BUTTON, 40), "Login screen not reached with the valid Customer ID"
