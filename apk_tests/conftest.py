import os
import time
import pytest
import helpers
import ui
from ui import PKG, by_id, wait_for


USER = os.getenv("APK_USERNAME", "buffet")
PWD = os.getenv("APK_PASSWORD", "123")
CUSTOMER_ID = os.getenv("APK_CUSTOMER_ID", "0711")


@pytest.fixture(scope="session")
def server():
    if not helpers.adb_path():
        pytest.exit("adb not found. Looked in:\n  " + "\n  ".join(helpers.adb_candidates())
                    + "\nCopy platform-tools into dineflash-tests\\tools (see README_APK.md step 1).", returncode=2)
    if not helpers.connected_devices():
        pytest.exit("No phone connected - check USB cable and USB debugging", returncode=2)
    if not os.getenv("APP_PACKAGE"):
        pytest.exit("APP_PACKAGE is empty - run: python apk_tests/find_app.py", returncode=2)
    proc = helpers.start_appium()
    yield
    if proc:
        proc.terminate()


_FAILS = {"n": 0}
_SHARED = {}


def _prepare(to_login):
    """Clear the app data, then go to the Customer ID screen (or on to the login screen).
    Retries with a new Appium session if the helper app crashes."""
    last = None
    for _ in range(3):
        drv = None
        try:
            drv = helpers.make_driver()
            helpers.adb("shell", "pm", "clear", PKG)
            drv.activate_app(PKG)
            if to_login:
                ui.activate_device(drv, CUSTOMER_ID)
                assert wait_for(drv, "edit_text_username", 60), "Login screen did not appear after Customer ID"
            else:
                assert wait_for(drv, "digit1EditText", 30), "Customer ID screen did not appear"
            _FAILS["n"] = 0
            return drv
        except Exception as e:
            last = e
            try:
                if drv:
                    drv.quit()
            except Exception:
                pass
            time.sleep(3)
    # Stop early instead of letting every remaining test wait for a crashed helper (was 38 minutes)
    _FAILS["n"] += 1
    if _FAILS["n"] >= 3:
        pytest.exit("Appium helper keeps crashing on this phone (3 setups in a row failed).\n"
                    "Fix: phone Settings > Developer options > turn OFF 'Permission monitoring' / "
                    "turn ON 'Install via USB' and 'USB debugging (Security settings)'; "
                    "Battery > allow 'UiAutomator' and 'io.appium.settings' to run in background; "
                    "then run again. Last error: " + str(last)[:200], returncode=3)
    raise last


def _quit(drv):
    try:
        drv.quit()
    except Exception:
        pass


@pytest.fixture
def app(server):
    """Fresh app on the login screen (data cleared, Customer ID entered)."""
    drv = _prepare(True)
    yield drv
    _quit(drv)


@pytest.fixture
def fresh(server):
    """Fresh app on the Customer ID screen."""
    drv = _prepare(False)
    yield drv
    _quit(drv)


@pytest.fixture(scope="module")
def shared_login(server):
    """One login screen reused by tests that never get past it (rejected logins)."""
    _SHARED["login"] = _prepare(True)
    yield _SHARED["login"]
    _quit(_SHARED["login"])


@pytest.fixture
def login_screen(shared_login):
    """Shared login screen with both boxes emptied before each test.
    If the Appium helper crashed since the last test, a new session is built first."""
    d = _SHARED["login"]
    try:
        on_login = ui.on_login_screen(d)
    except Exception:
        _quit(d)
        d = _SHARED["login"] = _prepare(True)
        on_login = True
    if not on_login:
        d.activate_app(PKG)
        assert wait_for(d, "edit_text_username", 20), "Not on the login screen any more"
    ui.fill(d, "edit_text_username", "")
    ui.fill(d, "edit_text_password", "")
    ui.hide_keyboard()
    return d


@pytest.fixture(scope="module")
def dashboard(server):
    """Logged in as the outlet manager, sitting on the Home dashboard (shared by a module)."""
    _SHARED["dash"] = _logged_in()
    yield _SHARED["dash"]
    _quit(_SHARED["dash"])


def _logged_in():
    drv = _prepare(True)
    ui.do_login(drv, USER, PWD, wait=10)
    if not ui.wait_for(drv, "tv_stat_total", 30):
        _quit(drv)
        pytest.fail("Could not log in to reach the dashboard - check APK_USERNAME / APK_PASSWORD")
    return drv


@pytest.fixture
def home(dashboard):
    """Make sure each test starts on the Home tab. If the Appium helper crashed, log in again with a new session."""
    d = _SHARED["dash"]
    try:
        on_home = ui.on_dashboard(d)
    except Exception:
        _quit(d)
        d = _SHARED["dash"] = _logged_in()
        on_home = True
    if not on_home:
        ui.press_back()
        if not ui.on_dashboard(d):
            ui.tap_text(d, "Home")
            time.sleep(1.5)
    return d


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Save a phone screenshot when a test fails."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        for name in ("app", "fresh", "login_screen", "home", "dashboard"):
            drv = item.funcargs.get(name)
            if drv is not None:
                os.makedirs(os.path.join(helpers.HERE, "failures"), exist_ok=True)
                try:
                    drv.save_screenshot(os.path.join(helpers.HERE, "failures", item.name + ".png"))
                except Exception:
                    pass
                break
