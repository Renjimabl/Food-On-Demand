"""
Installs the Kitchen Staff APK if it is missing, finds the app's start screen, and saves it to kitchen.env.
Run once:   python kitchen_apk_tests/find_kitchen_app.py
"""
import os
import kitchen_lib as k

devs = k.connected_devices()
if not devs:
    raise SystemExit("No phone found. Connect by USB, turn on USB debugging and tap Allow on the phone.")
print("Phone:", devs[0])

installed = k.PKG in k.adb("shell", "pm", "list", "packages", k.PKG)
if not installed:
    apk = os.getenv("APK_PATH")
    if not apk or not os.path.exists(apk):
        raise SystemExit(f"APK not found: {apk}")
    print("Installing", os.path.basename(apk), "...")
    print(k.adb("install", "-r", "-g", apk))
else:
    print("Already installed:", k.PKG)

print(k.adb("shell", "dumpsys", "package", k.PKG).count("versionName"), "package info lines found")
for line in k.adb("shell", "dumpsys", "package", k.PKG).splitlines():
    if "versionName" in line:
        print(line.strip())
        break

out = k.adb("shell", "cmd", "package", "resolve-activity", "--brief", k.PKG).splitlines()
act = out[-1].strip() if out and "/" in out[-1] else ""
act = act.split("/")[-1]
if act.startswith("."):
    act = k.PKG + act
print("Start screen:", act or "(not found)")
if act:
    k.set_env_value("APP_ACTIVITY", act)
    print("Saved to kitchen.env")
