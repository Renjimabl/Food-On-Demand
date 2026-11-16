"""
One command: run the Kitchen APK tests, then build the bug report.

    python run_kitchen_tests.py                 all modules
    python run_kitchen_tests.py k02             only one module (k01 ... k07)
    python run_kitchen_tests.py k02 k03         several modules
    python run_kitchen_tests.py --quick         skip the slow 10-minute idle test and Wi-Fi test
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
args = sys.argv[1:]
quick = "--quick" in args
mods = [a for a in args if a.startswith("k0")]

cmd = [sys.executable, "-m", "pytest", "-p", "no:cacheprovider",
       f"--junitxml={os.path.join(HERE, 'results', 'kitchen_junit.xml')}"]
if mods:
    cmd += [os.path.join(HERE, f) for f in sorted(os.listdir(HERE))
            if f.startswith("test_") and any(f.startswith(f"test_{m}") for m in mods)]
else:
    cmd += [HERE]
if quick:
    cmd += ["-k", "not ten_minutes and not wifi"]

print("Running:", " ".join(os.path.basename(c) if os.path.exists(c) else c for c in cmd))
subprocess.run(cmd, cwd=HERE)
subprocess.run([sys.executable, os.path.join(HERE, "generate_bug_report.py")], cwd=HERE)
