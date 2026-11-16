"""
MODULE 7 - Robustness - Kitchen Staff APK
A kitchen tablet runs all day: rotation, Wi-Fi loss, screen lock, back button must not break it.
"""
import time
import pytest
import kitchen_lib as k

MODULE = "Robustness"


def set_rotation(value):
    k.adb("shell", "settings", "put", "system", "accelerometer_rotation", "0")
    k.adb("shell", "settings", "put", "system", "user_rotation", str(value))
    time.sleep(3)


@pytest.fixture
def portrait_after():
    yield
    set_rotation(0)
    k.adb("shell", "svc", "wifi", "enable")


def test_back_button_does_not_leave_kitchen_screen_unexpectedly(on_kitchen):
    """Press the Back button once on the kitchen screen.
    Expected: the app does not sign the user out or crash (it may stay or ask to exit)."""
    k.press_back()
    time.sleep(2)
    k.launch()
    time.sleep(5)
    assert not k.on_login_screen(on_kitchen), "Back button signed the user out"
    assert not k.has(on_kitchen, r"keeps stopping|has stopped|isn't responding")


def test_landscape_rotation_keeps_screen(on_kitchen, portrait_after):
    """Rotate the phone to landscape.
    Expected: the kitchen screen is still shown, data not lost."""
    set_rotation(1)
    assert k.on_kitchen_screen(on_kitchen), "Kitchen screen lost after rotating to landscape"


def test_back_to_portrait_keeps_screen(on_kitchen, portrait_after):
    """Rotate to landscape and back to portrait.
    Expected: the kitchen screen is shown again."""
    set_rotation(1)
    set_rotation(0)
    assert k.on_kitchen_screen(on_kitchen)


def test_wifi_off_shows_message_or_keeps_screen(on_kitchen, portrait_after):
    """Turn Wi-Fi off for 15 seconds, then on.
    Expected: the app does not crash; the kitchen screen is back after the network returns."""
    out = k.adb("shell", "svc", "wifi", "disable")
    if "not" in out.lower() and "permission" in out.lower():
        pytest.skip("Cannot switch Wi-Fi from adb on this phone")
    time.sleep(15)
    k.adb("shell", "svc", "wifi", "enable")
    time.sleep(25)
    assert k.on_kitchen_screen(on_kitchen), "Kitchen screen did not recover after the network came back"


def test_screen_lock_and_unlock(on_kitchen):
    """Lock the screen (power button), wait 10 seconds, wake it.
    Expected: the kitchen screen is still there (swipe-up unlock may be needed by hand)."""
    k.adb("shell", "input", "keyevent", "26")
    time.sleep(10)
    k.adb("shell", "input", "keyevent", "224")
    time.sleep(3)
    k.adb("shell", "input", "swipe", "360", "1300", "360", "400", "300")
    time.sleep(4)
    assert k.on_kitchen_screen(on_kitchen)


def test_app_survives_force_stop_and_reopen(on_kitchen):
    """Force-stop the app and open it again.
    Expected: it opens normally without a crash dialog."""
    k.force_stop()
    k.launch()
    time.sleep(10)
    assert not k.has(on_kitchen, r"keeps stopping|has stopped|isn't responding")


def test_no_crash_after_ten_minutes_idle(on_kitchen):
    """Leave the app open for 10 minutes.
    Expected: still running on the kitchen screen. (Slow test.)"""
    time.sleep(600)
    assert k.on_kitchen_screen(on_kitchen)
