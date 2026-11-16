"""
Saves a screenshot and the element list of whatever is open on the phone (no restart of the app).
Use it to find the real names when a test cannot find something.

Run:   python kitchen_apk_tests/dump_screen.py
Creates screen.png, screen.xml and screen_elements.txt in kitchen_apk_tests.
"""
import os
import re
import kitchen_lib as k
from appium import webdriver
from appium.options.android import UiAutomator2Options

proc = k.start_appium()
o = UiAutomator2Options()
o.platform_name = "Android"
o.automation_name = "UiAutomator2"
o.app_package = k.PKG
o.auto_launch = False      # attach to the screen that is open, do not restart the app
o.no_reset = True
d = webdriver.Remote(k.SERVER, options=o)
try:
    d.save_screenshot(os.path.join(k.HERE, "screen.png"))
    xml = d.page_source
    open(os.path.join(k.HERE, "screen.xml"), "w", encoding="utf-8").write(xml)
    rows = []
    for m in re.finditer(r"<([\w.]+) [^>]*?>", xml):
        tag = m.group(0)
        text = re.search(r' text="([^"]*)"', tag)
        rid = re.search(r'resource-id="([^"]*)"', tag)
        desc = re.search(r'content-desc="([^"]*)"', tag)
        clk = re.search(r'clickable="(\w+)"', tag)
        if (text and text.group(1)) or (desc and desc.group(1)) or ("EditText" in m.group(1)) or ("Button" in m.group(1)):
            rows.append(f"{m.group(1).split('.')[-1]:12} id={(rid.group(1).split('/')[-1] if rid else ''):28} "
                        f"text='{text.group(1) if text else ''}' desc='{desc.group(1) if desc else ''}' "
                        f"click={clk.group(1) if clk else ''}")
    open(os.path.join(k.HERE, "screen_elements.txt"), "w", encoding="utf-8").write("\n".join(rows))
    print("\n".join(rows))
    print("\nSaved screen.png, screen.xml, screen_elements.txt")
finally:
    d.quit()
    if proc:
        proc.terminate()
