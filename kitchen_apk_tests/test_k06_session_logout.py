"""
MODULE 6 - Session and Logout - Kitchen Staff APK
Found on the Manager app: Logout did not end the session (BUG-APK-01). These tests check the Kitchen app.
"""
import time
import pytest
import kitchen_lib as k

MODULE = "Session and Logout"


def find_logout(d):
    """Return the Logout control, opening a menu first if needed. None if not found."""
    if k.has(d, r"^log ?out$|sign ?out"):
        return d.find_element(*k.by_text_regex(r"^log ?out$|sign ?out"))
    return None


def open_logout(d):
    el = find_logout(d)
    if el is None:  # try the top-right menu / settings icon
        size = d.get_window_size()
        k.adb("shell", "input", "tap", str(int(size["width"] * 0.9)), str(int(size["height"] * 0.07)))
        time.sleep(1.5)
        el = find_logout(d)
    return el


def test_session_kept_after_restart(on_kitchen):
    """Close the app completely and open it again.
    Expected: still signed in on the kitchen screen (no login asked)."""
    k.force_stop(); k.launch()
    time.sleep(10)
    assert k.on_kitchen_screen(on_kitchen), "Asked to sign in again after a restart"


def test_session_kept_after_going_to_home_screen(on_kitchen):
    """Press the phone Home button, wait, and come back.
    Expected: still on the kitchen screen."""
    k.press_home()
    time.sleep(8)
    k.launch()
    time.sleep(6)
    assert k.on_kitchen_screen(on_kitchen)


def test_logout_option_exists(on_kitchen):
    """Look for a Logout option (button or menu).
    Expected: Logout is available to the kitchen staff."""
    el = open_logout(on_kitchen)
    assert el is not None, f"No Logout found. Texts: {k.all_texts(on_kitchen)[:12]}"


def test_logout_cancel_keeps_user_signed_in(on_kitchen):
    """Tap Logout, then Cancel in the confirmation.
    Expected: the user stays on the kitchen screen. Skipped if there is no confirmation."""
    el = open_logout(on_kitchen)
    if el is None:
        pytest.skip("No Logout found")
    k.tap(el)
    time.sleep(1.5)
    if not k.has(on_kitchen, r"^cancel$|^no$"):
        pytest.skip("No confirmation pop-up")
    k.tap_text(on_kitchen, r"^cancel$|^no$")
    time.sleep(1.5)
    assert k.on_kitchen_screen(on_kitchen)


def test_logout_then_reopen_asks_for_login(kitchen):
    """Sign out, close the app, open it again.
    Expected: the login (or Customer ID) screen is shown - the previous user is not still signed in.
    NOTE: this signs the shared test user out; it runs last in the module."""
    el = open_logout(kitchen)
    if el is None:
        pytest.skip("No Logout found")
    k.tap(el)
    time.sleep(1.5)
    if k.has(kitchen, r"^log ?out$|^yes$|^confirm$"):
        k.tap_text(kitchen, r"^yes$|^confirm$|^log ?out$")
    time.sleep(4)
    k.force_stop(); k.launch()
    time.sleep(10)
    assert k.on_login_screen(kitchen) or k.on_customer_id_screen(kitchen), \
        "Reopening after Logout went back into the kitchen screen"
