"""
Shared helpers for the Kitchen Staff APK tests.

All TAPPING and TYPING is done with adb (Appium's own click/type crashes its helper app on the
vivo test phone). Appium is used only to READ the screen (find elements, text, position).
"""
import os
import re
import shutil
import subprocess
import time
import urllib.request

from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
ENV_FILE = os.path.join(HERE, "kitchen.env")
load_dotenv(ENV_FILE)

SERVER = "http://127.0.0.1:4723"
PKG = os.getenv("APP_PACKAGE", "com.softland.fod_kitchen_staff")


# ---------------------------------------------------------------- adb

def adb_candidates():
    return [
        os.path.join(PROJECT, "tools", "platform-tools", "adb.exe"),
        os.path.join(os.getenv("ANDROID_HOME", ""), "platform-tools", "adb.exe"),
        os.path.join(os.getenv("LOCALAPPDATA", ""), "Android", "Sdk", "platform-tools", "adb.exe"),
    ]


def adb_path():
    for p in adb_candidates():
        if os.path.exists(p):
            return p
    return shutil.which("adb")


def adb(*args, timeout=120):
    exe = adb_path()
    if not exe:
        raise RuntimeError("adb not found. Looked in:\n  " + "\n  ".join(adb_candidates()))
    return subprocess.run([exe, *args], capture_output=True, text=True, timeout=timeout).stdout.strip()


def connected_devices():
    return [l.split()[0] for l in adb("devices").splitlines()[1:] if l.strip().endswith("device")]


def set_env_value(key, value):
    lines = open(ENV_FILE, encoding="utf-8").read().splitlines()
    for i, l in enumerate(lines):
        if l.startswith(key + "="):
            lines[i] = f"{key}={value}"
            break
    else:
        lines.append(f"{key}={value}")
    open(ENV_FILE, "w", encoding="utf-8").write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- Appium

def appium_running():
    try:
        urllib.request.urlopen(SERVER + "/status", timeout=3)
        return True
    except Exception:
        return False


def start_appium():
    if appium_running():
        return None
    exe = shutil.which("appium")
    if not exe:
        raise RuntimeError("Appium not found. Install with: npm install -g appium")
    home = os.path.dirname(os.path.dirname(adb_path() or ""))
    env = dict(os.environ, ANDROID_HOME=home, ANDROID_SDK_ROOT=home)
    proc = subprocess.Popen([exe, "--address", "127.0.0.1", "--port", "4723"],
                            stdout=open(os.path.join(HERE, "appium.log"), "w"),
                            stderr=subprocess.STDOUT, env=env)
    for _ in range(30):
        if appium_running():
            return proc
        time.sleep(1)
    raise RuntimeError("Appium did not start. See kitchen_apk_tests/appium.log")


def make_driver():
    from appium import webdriver
    from appium.options.android import UiAutomator2Options
    o = UiAutomator2Options()
    o.platform_name = "Android"
    o.automation_name = "UiAutomator2"
    o.auto_grant_permissions = True
    o.new_command_timeout = 180
    o.no_reset = True
    o.app_package = PKG
    if os.getenv("APP_ACTIVITY"):
        o.app_activity = os.getenv("APP_ACTIVITY")
    return webdriver.Remote(SERVER, options=o)


# ---------------------------------------------------------------- reading the screen
from appium.webdriver.common.appiumby import AppiumBy  # noqa: E402


def by_text_regex(pattern):
    return (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textMatches("(?i).*({pattern}).*")')


def by_exact(text):
    return (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")')


def edit_boxes(d):
    return d.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")


def has(d, pattern):
    return len(d.find_elements(*by_text_regex(pattern))) > 0


def wait_text(d, pattern, seconds=20):
    end = time.time() + seconds
    while time.time() < end:
        if has(d, pattern):
            return True
        time.sleep(1)
    return False


def all_texts(d):
    return [e.text for e in d.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView") if e.text]


# ---------------------------------------------------------------- acting with adb

def tap(el):
    r = el.rect
    adb("shell", "input", "tap", str(int(r["x"] + r["width"] / 2)), str(int(r["y"] + r["height"] / 2)))
    time.sleep(0.8)


def tap_text(d, pattern):
    tap(d.find_element(*by_text_regex(pattern)))


def type_text(text):
    safe = text.replace(" ", "%s")
    for ch in "\\'\"`&|;<>()$~*?#":
        safe = safe.replace(ch, "\\" + ch)
    adb("shell", "input", "text", safe)


def clear_box():
    adb("shell", "input", "keyevent", "123")
    adb("shell", "input", "keyevent", *(["67"] * 30))


def fill_box(box, text):
    tap(box)
    time.sleep(0.4)
    clear_box()
    if text:
        type_text(text)


def press_back():
    adb("shell", "input", "keyevent", "4")
    time.sleep(1.2)


def hide_keyboard():
    adb("shell", "input", "keyevent", "111")
    time.sleep(0.8)


def press_home():
    adb("shell", "input", "keyevent", "3")
    time.sleep(1.5)


def force_stop():
    adb("shell", "am", "force-stop", PKG)


def launch():
    adb("shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1")
    time.sleep(3)


def clear_data():
    adb("shell", "pm", "clear", PKG)


# ---------------------------------------------------------------- app-level flows

LOGIN_BUTTON = r"log ?in|sign ?in"
ACTIVATE_BUTTON = r"check license|activate|continue|next|verify|submit"


def on_login_screen(d):
    return len(edit_boxes(d)) >= 2 and has(d, LOGIN_BUTTON)


def on_customer_id_screen(d):
    return has(d, r"customer id|customer-id|4-digit")


def on_kitchen_screen(d):
    return has(d, r"buffet kitchen processing|all caught up|mark as ready")


def enter_customer_id(d, cid):
    boxes = edit_boxes(d)
    if not boxes:
        return
    tap(boxes[0])
    type_text(cid)
    time.sleep(1)
    try:
        tap_text(d, ACTIVATE_BUTTON)
    except Exception:
        adb("shell", "input", "keyevent", "66")


def login(d, user, pwd, wait=8):
    boxes = edit_boxes(d)
    fill_box(boxes[0], user)
    fill_box(edit_boxes(d)[1], pwd)
    hide_keyboard()
    tap_text(d, LOGIN_BUTTON)
    time.sleep(wait)
