import os
import time
import pytest
import kitchen_lib as k

USER = os.getenv("KITCHEN_USERNAME", "kia")
PWD = os.getenv("KITCHEN_PASSWORD", "123")
CID = os.getenv("KITCHEN_CUSTOMER_ID", "0711")


@pytest.fixture(scope="session")
def server():
    if not k.adb_path():
        pytest.exit("adb not found. Looked in:\n  " + "\n  ".join(k.adb_candidates()), returncode=2)
    if not k.connected_devices():
        pytest.exit("No phone connected - USB cable, USB debugging, tap Allow on the phone", returncode=2)
    proc = k.start_appium()
    yield
    if proc:
        proc.terminate()


def _open_fresh(through_activation):
    """Clear app data and open it; optionally pass the Customer ID screen (if the app has one)."""
    last = None
    for _ in range(3):  # the Appium helper crashes now and then on this phone, so retry
        drv = None
        try:
            drv = k.make_driver()
            k.force_stop()
            k.clear_data()
            k.launch()
            time.sleep(6)
            if through_activation and k.on_customer_id_screen(drv):
                k.enter_customer_id(drv, CID)
                time.sleep(10)
            return drv
        except Exception as e:
            last = e
            try:
                if drv:
                    drv.quit()
            except Exception:
                pass
            time.sleep(3)
    raise last


def _quit(d):
    try:
        d.quit()
    except Exception:
        pass


@pytest.fixture
def first_screen(server):
    """Fresh app, nothing entered (Customer ID screen, or login if the app has no Customer ID)."""
    d = _open_fresh(False)
    yield d
    _quit(d)


@pytest.fixture
def login_screen(server):
    """Fresh app on the login screen."""
    d = _open_fresh(True)
    if not k.on_login_screen(d):
        _quit(d)
        pytest.fail("Login screen not reached - check kitchen.env (KITCHEN_CUSTOMER_ID) or run dump_screen.py")
    yield d
    _quit(d)


@pytest.fixture(scope="module")
def shared_login(server):
    """One login screen shared by tests that never get past it (rejected logins)."""
    d = _open_fresh(True)
    yield d
    _quit(d)


@pytest.fixture
def rejected_login(shared_login):
    d = shared_login
    if not k.on_login_screen(d):
        k.force_stop(); k.launch(); time.sleep(6)
    for box in k.edit_boxes(d)[:2]:
        k.fill_box(box, "")
    k.hide_keyboard()
    return d


@pytest.fixture(scope="module")
def kitchen(server):
    """Logged in as the Kitchen Staff user, on the Buffet Kitchen Processing screen."""
    d = _open_fresh(True)
    k.login(d, USER, PWD, wait=10)
    if not k.on_kitchen_screen(d):
        _quit(d)
        pytest.fail("Kitchen screen not reached after login - check KITCHEN_USERNAME / KITCHEN_PASSWORD and the "
                    "mapping in Menu Mapping")
    yield d
    _quit(d)


@pytest.fixture
def on_kitchen(kitchen):
    """Each test starts on the kitchen screen."""
    if not k.on_kitchen_screen(kitchen):
        k.press_back()
    return kitchen


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when in ("call", "setup") and rep.failed:
        for name in ("first_screen", "login_screen", "rejected_login", "on_kitchen", "kitchen", "shared_login"):
            d = item.funcargs.get(name)
            if d is not None:
                os.makedirs(os.path.join(k.HERE, "failures"), exist_ok=True)
                try:
                    d.save_screenshot(os.path.join(k.HERE, "failures", item.name + ".png"))
                except Exception:
                    pass
                break
