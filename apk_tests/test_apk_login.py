"""
Login tests - Food On Demand manager APK (QA v1.0.1).
Flow: Customer ID (0711) -> Check License -> Login (buffet / 123) -> Dashboard.
"""
import os
import time
import pytest

import helpers
import ui
from ui import by_id, wait_for, on_login_screen, on_dashboard, PKG

USER = os.getenv("APK_USERNAME", "buffet")
PWD = os.getenv("APK_PASSWORD", "123")


def not_logged_in(d):
    return on_login_screen(d) and not on_dashboard(d)


# ------------------------------------------------------------ activation (Customer ID) screen

def test_customer_id_screen_shows_four_boxes(fresh):
    for i in range(1, 5):
        assert fresh.find_elements(*by_id(f"digit{i}EditText")), f"digit{i} box missing"
    assert fresh.find_element(*by_id("checkLicenseButton")).is_displayed()


def test_app_version_is_1_0_1(fresh):
    assert "1.0.1" in fresh.find_element(*by_id("footerVersionTxt")).text


def test_device_id_is_shown(fresh):
    assert "Device ID" in fresh.find_element(*by_id("footerDeviceIdTxt")).text


def test_wrong_customer_id_rejected(fresh):
    ui.tap_id(fresh, "digit1EditText")
    ui.type_text("9999")
    time.sleep(1)
    ui.tap_id(fresh, "checkLicenseButton")
    time.sleep(10)
    assert not on_login_screen(fresh), "A wrong Customer ID (9999) was accepted"


def test_check_license_with_empty_id_rejected(fresh):
    ui.tap_id(fresh, "checkLicenseButton")
    time.sleep(4)
    assert not on_login_screen(fresh), "Empty Customer ID moved on to the login screen"


# ------------------------------------------------------------ login screen layout

def test_login_screen_elements(login_screen):
    assert login_screen.find_element(*by_id("edit_text_username")).is_displayed()
    assert login_screen.find_element(*by_id("edit_text_password")).is_displayed()
    assert login_screen.find_element(*by_id("button_login")).is_displayed()


def test_login_screen_texts(login_screen):
    assert ui.has_text(login_screen, "Welcome back")
    assert ui.has_text(login_screen, "Sign in with your outlet manager account")


def test_password_is_masked(login_screen):
    assert login_screen.find_element(*by_id("edit_text_password")).get_attribute("password") == "true"


def test_show_password_toggle(login_screen):
    ui.fill(login_screen, "edit_text_password", PWD)
    ui.hide_keyboard()
    ui.tap_id(login_screen, "text_input_end_icon")
    time.sleep(1)
    assert login_screen.find_element(*by_id("edit_text_password")).get_attribute("password") == "false", \
        "Eye icon did not reveal the password"


# ------------------------------------------------------------ valid login

def test_valid_login(app):
    ui.do_login(app, USER, PWD)
    assert on_dashboard(app), "Dashboard not shown after a valid login"


def test_dashboard_greets_logged_in_user(app):
    ui.do_login(app, USER, PWD)
    assert wait_for(app, "text_view_user_greeting", 20), "Dashboard greeting missing"
    assert app.find_element(*by_id("text_view_user_greeting")).text.lower() == USER.lower()


# ------------------------------------------------------------ invalid logins (must stay on login)

@pytest.mark.parametrize("user,pwd", [
    (USER, "wrong_pw_999"),       # wrong password
    ("no_such_user_x", PWD),      # unknown user
    (USER, ""),                   # empty password
    ("", PWD),                    # empty username
    ("", ""),                     # both empty
    (" ", " "),                   # spaces only
    ("' OR 1=1 --", "' OR 1=1 --"),   # SQL injection text
    ("<script>alert(1)</script>", "x"),  # script text
    ("A" * 200, "A" * 200),       # very long values
])
def test_invalid_login_rejected(login_screen, user, pwd):
    ui.do_login(login_screen, user, pwd, wait=6)
    assert not_logged_in(login_screen), f"Logged in with user='{user[:20]}' pwd='{pwd[:20]}'"


def test_password_is_case_sensitive(login_screen):
    if PWD.swapcase() == PWD:
        pytest.skip("Password has no letters to change case")
    ui.do_login(login_screen, USER, PWD.swapcase(), wait=6)
    assert not_logged_in(login_screen)


def test_username_with_surrounding_spaces(login_screen):
    """Information only: ' buffet ' - result is printed, test passes either way."""
    ui.do_login(login_screen, f" {USER} ", PWD, wait=8)
    print("USERNAME WITH SPACES ->", "accepted" if on_dashboard(login_screen) else "rejected")


# ------------------------------------------------------------ session

def test_session_kept_after_app_restart(app):
    ui.do_login(app, USER, PWD)
    assert on_dashboard(app)
    app.terminate_app(PKG)
    app.activate_app(PKG)
    assert wait_for(app, "tv_stat_total", 30), "Asked to log in again after restart (session not kept)"


def test_logout_cancel_keeps_user_logged_in(app):
    ui.do_login(app, USER, PWD)
    ui.logout_icon(app)
    assert ui.wait_for_text(app, "Are you sure you want to logout?", 8), "Logout pop-up did not open"
    ui.tap_text(app, "Cancel")
    time.sleep(1.5)
    assert on_dashboard(app), "Cancel on the logout pop-up still logged the user out"


@pytest.mark.xfail(reason="BUG-APK-01: after Logout the app closes, and reopening it goes straight back "
                          "to the dashboard as the same user")
def test_logout_then_reopen_asks_for_login(app):
    ui.do_login(app, USER, PWD)
    ui.logout_icon(app)
    ui.tap_text(app, "Logout")
    time.sleep(4)
    app.activate_app(PKG)
    time.sleep(10)
    assert on_login_screen(app), "Reopening after Logout did not show the login screen"
