"""
Installs the APK on the connected phone and finds its package name + launch screen,
then saves them into apk.env.

Run once:   python apk_tests/find_app.py
"""
import os
import re
from helpers import adb, connected_devices, set_env_value, ENV_FILE  # noqa: F401
import helpers

devs = connected_devices()
if not devs:
    raise SystemExit("No phone found. Connect by USB, turn on USB debugging, accept the prompt on the phone.")
print("Phone:", devs[0])

apk = os.getenv("APK_PATH")
if not apk or not os.path.exists(apk):
    raise SystemExit(f"APK not found: {apk}")

before = set(adb("shell", "pm", "list", "packages", "-3").split())
print("Installing", os.path.basename(apk), "... (this can take a minute)")
print(adb("install", "-r", "-g", apk))
after = set(adb("shell", "pm", "list", "packages", "-3").split())

new = sorted(after - before)
if len(new) == 1:
    pkg = new[0].replace("package:", "")
else:
    # Already installed earlier: pick the package whose name looks like this app
    cands = [p.replace("package:", "") for p in sorted(after)]
    guess = [p for p in cands if re.search(r"food|dine|flash|buffet|softland|demand", p, re.I)]
    print("Installed third-party packages:", *cands, sep="\n  ")
    if len(guess) != 1:
        raise SystemExit("Could not pick the package. Put the right one in apk.env as APP_PACKAGE=")
    pkg = guess[0]

out = adb("shell", "cmd", "package", "resolve-activity", "--brief", pkg).splitlines()
act = out[-1].split("/")[-1] if out and "/" in out[-1] else ""
if act.startswith("."):
    act = pkg + act
print("Package :", pkg)
print("Activity:", act)
set_env_value("APP_PACKAGE", pkg)
set_env_value("APP_ACTIVITY", act)
print("Saved to apk.env. You can now run the tests.")
