# Bug Report - Manager APK

Generated: 16-Nov-2026 16:44  |  Source: `results\apk_junit.xml`  |  App: Manager QA v1.0.1 (com.softland.foodondemand)

## 1. Summary

| Result | Count |
|---|---|
| Passed | 8 |
| Failed - real findings (bugs) | 6 |
| Environment problem (not a bug) | 4 |
| Skipped (not run) | 1 |
| Known issue (expected failure) | 0 |
| Setup error | 0 |
| **Total tests** | **19** |

> 4 test(s) did not finish because the test tool or phone failed (Appium helper crash, phone not connected, login screen not reached). They are listed in section 4 and are not bugs.

## 2. Results by module

| Module | Passed | Failed | Env problem | Skipped | Known |
|---|---|---|---|---|---|
| Orders | 8 | 6 | 4 | 1 | 0 |

## 3. Bugs found

| ID | Module | Failed check | Severity | Result |
|---|---|---|---|---|
| MBUG-01 | Orders | Orders filter chips present[Preparing] | High | AssertionError: Chip 'Preparing' with a count was not found |
| MBUG-02 | Orders | Orders filter chips present[Ready] | High | AssertionError: Chip 'Ready' with a count was not found |
| MBUG-03 | Orders | Orders filter chips present[Served] | High | AssertionError: Chip 'Served' with a count was not found |
| MBUG-04 | Orders | Orders all chip matches list label | High | assert None == 5 |
| MBUG-05 | Orders | Orders total matches dashboard total | High | AssertionError: Home says 5 orders, Orders screen says None |
| MBUG-06 | Orders | Orders chip counts add up | High | TypeError: '<=' not supported between instances of 'int' and 'NoneTyp… |

Full steps / expected / actual for each: `python generate_bug_report.py --detail`

## 4. Environment problems (not application bugs)

4 test(s) could not finish because the Appium helper / phone failed. Re-run them; they are not bugs.

## 5. Skipped tests

1 test(s) skipped (nothing to test today, e.g. no Ready orders).

## 6. Known issues already marked in the tests

None.
