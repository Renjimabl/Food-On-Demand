"""
Saves a screenshot and the screen's element tree of whatever is open on the phone.
Use it to see the real field names when a locator fails.

Run:   python apk_tests/dump_screen.py
Creates screen.png and screen.xml in apk_tests.
"""
import os
import helpers

proc = helpers.start_appium()
driver = helpers.make_driver()
try:
    here = helpers.HERE
    driver.save_screenshot(os.path.join(here, "screen.png"))
    open(os.path.join(here, "screen.xml"), "w", encoding="utf-8").write(driver.page_source)
    print("Saved screen.png and screen.xml")
finally:
    driver.quit()
    if proc:
        proc.terminate()
