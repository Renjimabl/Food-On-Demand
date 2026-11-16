"""
Phone helpers shared by all APK tests.

IMPORTANT: on this vivo phone Appium's own click/type on text boxes crashes its helper app
("socket hang up"). So we only READ the screen with Appium (find elements, text, position)
and do all tapping and typing with adb, which is stable.
"""
import time
from appium.webdriver.common.appiumby import AppiumBy

import helpers

PKG = "com.softland.foodondemand"
ID = PKG + ":id/"


# ---------------------------------------------------------------- finding things

def by_id(name):
    return (AppiumBy.ID, ID + name)


def by_text(text):
    return (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")')


def wait_for(d, name, seconds=40):
    """Wait for an element id; return it or None."""
    end = time.time() + seconds
    while time.time() < end:
        found = d.find_elements(*by_id(name))
        if found:
            return found[0]
        time.sleep(1)
    return None


def has_text(d, text):
    return len(d.find_elements(*by_text(text))) > 0


def wait_for_text(d, text, seconds=15):
    end = time.time() + seconds
    while time.time() < end:
        if has_text(d, text):
            return True
        time.sleep(1)
    return False


# ---------------------------------------------------------------- acting with adb

def tap(d, el):
    """Tap the centre of an element using adb."""
    r = el.rect
    helpers.adb("shell", "input", "tap", str(int(r["x"] + r["width"] / 2)), str(int(r["y"] + r["height"] / 2)))
    time.sleep(0.8)


def tap_id(d, name):
    tap(d, d.find_element(*by_id(name)))


def tap_text(d, text):
    tap(d, d.find_element(*by_text(text)))


def tap_xy_ratio(d, x_ratio, y_ratio):
    size = d.get_window_size()
    helpers.adb("shell", "input", "tap", str(int(size["width"] * x_ratio)), str(int(size["height"] * y_ratio)))
    time.sleep(0.8)


def type_text(text):
    """Type into the focused box with adb."""
    safe = text.replace(" ", "%s")
    for ch in "\\'\"`&|;<>()$~*?#":
        safe = safe.replace(ch, "\\" + ch)
    helpers.adb("shell", "input", "text", safe)


def press_back():
    helpers.adb("shell", "input", "keyevent", "4")
    time.sleep(1.2)


def hide_keyboard():
    helpers.adb("shell", "input", "keyevent", "111")  # ESC closes the keyboard
    time.sleep(0.8)


def clear_focused_box():
    helpers.adb("shell", "input", "keyevent", "123")                 # move to end
    helpers.adb("shell", "input", "keyevent", *(["67"] * 30))        # delete


def fill(d, field_id, text):
    tap_id(d, field_id)
    time.sleep(0.5)
    clear_focused_box()
    if text:
        type_text(text)


# ---------------------------------------------------------------- screens

def on_login_screen(d):
    return len(d.find_elements(*by_id("edit_text_username"))) > 0


def on_dashboard(d):
    return len(d.find_elements(*by_id("tv_stat_total"))) > 0


def do_login(d, user, pwd, wait=8):
    fill(d, "edit_text_username", user)
    fill(d, "edit_text_password", pwd)
    hide_keyboard()
    tap_id(d, "button_login")
    time.sleep(wait)


def activate_device(d, customer_id):
    """Customer-ID screen -> Check License."""
    first = wait_for(d, "digit1EditText", 30)
    if first is None:
        return
    tap(d, first)
    type_text(customer_id)
    time.sleep(1)
    tap_id(d, "checkLicenseButton")


def texts(d):
    """All visible texts on the screen, in reading order (parsed from the page source)."""
    # NOTE: d.page_source crashes Appium's helper on this vivo phone, so read the TextViews one by one.
    out = []
    # any widget with text (chips and buttons are not TextViews), still without page_source
    for el in d.find_elements("-android uiautomator", 'new UiSelector().textMatches(".+")'):
        try:
            t = (el.text or "").strip()
        except Exception:
            continue
        if t:
            out.append(t)
    return out


def has_text_like(d, part):
    """True when any text on screen contains `part` (case-insensitive)."""
    return any(part.lower() in t.lower() for t in texts(d))


def number_before(d, label):
    """Value shown above/before a label, e.g. the '5' in the tile  5 / TOTAL.  None if absent."""
    last = None
    for t in texts(d):
        if t.upper() == label.upper():
            return last
        last = int(t) if t.isdigit() else last
    return None


def chip_count(d, name):
    """Number on a filter chip such as 'Preparing 1' (one text) or 'Preparing' + '1' (two texts)."""
    import re
    ts = texts(d)
    for i, t in enumerate(ts):
        m = re.fullmatch(rf"{re.escape(name)}\s*(\d+)", t, re.I)
        if m:
            return int(m.group(1))
        if t.lower() == name.lower() and i + 1 < len(ts) and ts[i + 1].isdigit():
            return int(ts[i + 1])
    return None


def list_count(d, word):
    """The '5 orders' / '2 chats' label above a list."""
    import re
    for t in texts(d):
        m = re.fullmatch(rf"(\d+)\s+{word}s?", t, re.I)
        if m:
            return int(m.group(1))
    return None


def open_screen(d, tab, title, seconds=15):
    """From the dashboard tap a bottom tab and wait for the screen title."""
    tap_text(d, tab)
    return wait_for_text(d, title, seconds)


def logout_icon(d):
    """Round logout icon, top right of the dashboard."""
    tap_xy_ratio(d, 0.885, 0.096)
    time.sleep(1.2)
