"""Shared helpers for the APK tests: paths, adb, Appium server, driver."""
import os
import shutil
import subprocess
import time
import urllib.request

from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(HERE, "apk.env")
load_dotenv(ENV_FILE)

SERVER = "http://127.0.0.1:4723"


def sdk():
    return os.getenv("ANDROID_HOME") or os.path.join(os.getenv("LOCALAPPDATA", ""), "Android", "Sdk")


def adb_candidates():
    project = os.path.dirname(HERE)
    return [
        os.path.join(project, "tools", "platform-tools", "adb.exe"),   # copy kept inside the project
        os.path.join(sdk(), "platform-tools", "adb.exe"),
        os.path.join(os.getenv("LOCALAPPDATA", ""), "Android", "Sdk", "platform-tools", "adb.exe"),
        os.path.join(os.path.expanduser("~"), "AppData", "Local", "Android", "Sdk", "platform-tools", "adb.exe"),
    ]


def adb_path():
    for p in adb_candidates():
        if os.path.exists(p):
            return p
    return shutil.which("adb")


def adb(*args):
    exe = adb_path()
    if not exe:
        raise RuntimeError("adb not found. Install Android platform-tools (see README_APK.md, step 1).")
    return subprocess.run([exe, *args], capture_output=True, text=True, timeout=120).stdout.strip()


def connected_devices():
    out = adb("devices").splitlines()[1:]
    return [l.split()[0] for l in out if l.strip().endswith("device")]


def set_env_value(key, value):
    """Write KEY=value into apk.env."""
    lines = open(ENV_FILE, encoding="utf-8").read().splitlines()
    for i, l in enumerate(lines):
        if l.startswith(key + "="):
            lines[i] = f"{key}={value}"
            break
    else:
        lines.append(f"{key}={value}")
    open(ENV_FILE, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def appium_running():
    try:
        urllib.request.urlopen(SERVER + "/status", timeout=3)
        return True
    except Exception:
        return False


def start_appium():
    """Start the Appium server in the background if it is not already running."""
    if appium_running():
        return None
    exe = shutil.which("appium")
    if not exe:
        raise RuntimeError("Appium not found. Install with: npm install -g appium")
    # Appium finds adb through ANDROID_HOME\platform-tools, so point it at the folder that holds adb.
    adb_folder = os.path.dirname(adb_path() or "")
    home = os.path.dirname(adb_folder) if adb_folder else sdk()
    env = dict(os.environ, ANDROID_HOME=home, ANDROID_SDK_ROOT=home)
    proc = subprocess.Popen([exe, "--address", "127.0.0.1", "--port", "4723"],
                            stdout=open(os.path.join(HERE, "appium.log"), "w"),
                            stderr=subprocess.STDOUT, env=env)
    for _ in range(30):
        if appium_running():
            return proc
        time.sleep(1)
    raise RuntimeError("Appium server did not start. See apk_tests/appium.log")


def make_driver(use_package=True):
    from appium import webdriver
    from appium.options.android import UiAutomator2Options

    opts = UiAutomator2Options()
    opts.platform_name = "Android"
    opts.automation_name = "UiAutomator2"
    opts.auto_grant_permissions = True
    opts.new_command_timeout = 180
    opts.no_reset = True
    # Settings that keep the UiAutomator2 helper alive on vivo / Funtouch phones
    opts.set_capability("appium:disableWindowAnimation", True)
    opts.set_capability("appium:uiautomator2ServerLaunchTimeout", 90000)
    opts.set_capability("appium:uiautomator2ServerInstallTimeout", 90000)
    opts.set_capability("appium:adbExecTimeout", 60000)
    opts.set_capability("appium:skipDeviceInitialization", False)
    opts.set_capability("appium:settings[waitForIdleTimeout]", 0)
    opts.set_capability("appium:settings[waitForSelectorTimeout]", 0)
    pkg, act = os.getenv("APP_PACKAGE"), os.getenv("APP_ACTIVITY")
    if use_package and pkg:
        opts.app_package = pkg
        if act:
            opts.app_activity = act
    else:
        opts.app = os.getenv("APK_PATH")
    return webdriver.Remote(SERVER, options=opts)
