"""
One command: run the Manager APK tests, then build the bug report.

    python run_apk_tests.py                 all tests
    python run_apk_tests.py login           only test files whose name contains "login"
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
words = [a for a in sys.argv[1:] if not a.startswith("-")]
cmd = [sys.executable, "-m", "pytest", "-p", "no:cacheprovider",
       f"--junitxml={os.path.join(HERE, 'results', 'apk_junit.xml')}"]
files = [os.path.join(HERE, f) for f in sorted(os.listdir(HERE))
         if f.startswith("test_") and f.endswith(".py") and (not words or any(w in f for w in words))]
cmd += files or [HERE]
subprocess.run(cmd, cwd=HERE)
subprocess.run([sys.executable, os.path.join(HERE, "generate_bug_report.py")], cwd=HERE)