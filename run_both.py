"""
Run the WEB tests and the MANAGER APK tests at the same time.

    python run_both.py            web (headless) + Manager APK together
    python run_both.py --headed   web in a visible browser

They do not disturb each other: the web tests use a browser on the PC,
the APK tests use the phone through Appium.
Results: results/web_junit.xml and apk_tests/results/apk_junit.xml
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
APK = os.path.join(HERE, "apk_tests")
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
os.makedirs(os.path.join(APK, "results"), exist_ok=True)

web_cmd = [sys.executable, "-m", "pytest", "tests", "-p", "no:cacheprovider",
           f"--junitxml={os.path.join(HERE, 'results', 'web_junit.xml')}"]
if "--headed" in sys.argv:
    web_cmd.append("--headed")
apk_cmd = [sys.executable, "-m", "pytest", "-p", "no:cacheprovider",
           f"--junitxml={os.path.join(APK, 'results', 'apk_junit.xml')}"]

print("Starting web tests and Manager APK tests together...")
web = subprocess.Popen(web_cmd, cwd=HERE)
apk = subprocess.Popen(apk_cmd, cwd=APK)
web_code, apk_code = web.wait(), apk.wait()

print("\n==== FINISHED ====")
print("Web tests    :", "PASSED" if web_code == 0 else f"issues (exit {web_code})")
print("Manager APK  :", "PASSED" if apk_code == 0 else f"issues (exit {apk_code})")
sys.exit(1 if (web_code or apk_code) else 0)
