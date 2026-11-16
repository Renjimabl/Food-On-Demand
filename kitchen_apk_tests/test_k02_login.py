"""
MODULE 2 - Kitchen Staff login - Kitchen Staff APK
SRS: the kitchen staff signs in with a Utility User (Kitchen) account and opens Buffet Kitchen Processing.
"""
import os
import time
import pytest
import kitchen_lib as k

MODULE = "Login"
USER = os.getenv("KITCHEN_USERNAME", "kia")
PWD = os.getenv("KITCHEN_PASSWORD", "123")
MUSER = os.getenv("MANAGER_USERNAME", "buffet")
MPWD = os.getenv("MANAGER_PASSWORD", "123")


def stayed_out(d):
    return k.on_login_screen(d) and not k.on_kitchen_screen(d)


def test_login_screen_has_username_password_button(login_screen):
    """Open the login screen.
    Expected: a username box, a password box and a sign-in button."""
    assert len(k.edit_boxes(login_screen)) >= 2
    assert k.has(login_screen, k.LOGIN_BUTTON)


def test_password_is_masked(login_screen):
    """Type in the password box.
    Expected: the characters are hidden (dots)."""
    assert k.edit_boxes(login_screen)[1].get_attribute("password") == "true"


def test_valid_kitchen_login(login_screen):
    """Sign in with the Kitchen Staff account (kia / 123).
    Expected: the Buffet Kitchen Processing screen (or All Caught Up) is shown."""
    k.login(login_screen, USER, PWD, wait=10)
    assert k.on_kitchen_screen(login_screen), f"Kitchen screen not shown. Texts: {k.all_texts(login_screen)[:8]}"


@pytest.mark.parametrize("user,pwd", [
    (USER, "wrong_pw_999"),
    ("no_such_user_x", PWD),
    (USER, ""),
    ("", PWD),
    ("", ""),
    (" ", " "),
    ("' OR 1=1 --", "' OR 1=1 --"),
    ("<script>alert(1)</script>", "x"),
    ("A" * 200, "A" * 200),
])
def test_invalid_login_rejected(rejected_login, user, pwd):
    """Try an invalid username / password pair.
    Expected: the user stays on the login screen and is not signed in."""
    k.login(rejected_login, user, pwd, wait=6)
    assert stayed_out(rejected_login), f"Signed in with user='{user[:20]}' pwd='{pwd[:20]}'"


def test_password_is_case_sensitive(rejected_login):
    """Sign in with the password's letters changed to the other case.
    Expected: rejected (skipped when the password has no letters)."""
    if PWD.swapcase() == PWD:
        pytest.skip("Password has no letters")
    k.login(rejected_login, USER, PWD.swapcase(), wait=6)
    assert stayed_out(rejected_login)


def test_manager_account_cannot_use_kitchen_app(rejected_login):
    """Sign in on the Kitchen app with the Outlet Manager account (buffet / 123).
    Expected: rejected - only Kitchen Staff (Utility User) accounts may use the kitchen app."""
    k.login(rejected_login, MUSER, MPWD, wait=8)
    assert stayed_out(rejected_login), "An Outlet Manager account signed in on the Kitchen app"


def test_username_with_spaces_information(rejected_login):
    """Information: ' kia ' with spaces around it. Result is printed; passes either way.
    Expected: either accepted or rejected, but no crash."""
    k.login(rejected_login, f" {USER} ", PWD, wait=8)
    print("USERNAME WITH SPACES ->", "accepted" if k.on_kitchen_screen(rejected_login) else "rejected")
