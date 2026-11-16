"""
Builds the Kitchen APK bug report from the last test run.

    python generate_bug_report.py                   (reads results/kitchen_junit.xml)
    python generate_bug_report.py other_results.xml

Writes  Bug_Report_Kitchen_APK.md  and  Bug_Report_Kitchen_APK.html  next to this file.

How tests are sorted:
  * PASSED   - works
  * FAILED   - a real finding: becomes a numbered bug (KBUG-01, KBUG-02 ...)
  * ERROR / failures caused by the test tool (Appium crash, phone disconnected) are listed under
    "Environment problems" and are NOT counted as bugs
  * SKIPPED  - not run (no orders in queue, screen not in this build ...) with the reason
  * XFAIL    - known issue already marked in the test
"""
import ast
import glob
import html
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import OrderedDict
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_XML = os.path.join(HERE, "results", "kitchen_junit.xml")

ENV_PATTERNS = re.compile(
    r"socket hang up|instrumentation process|Could not proxy|invalid session id|session is either terminated|"
    r"adb not found|No phone connected|device .* not found|ECONNREFUSED|Appium did not start|"
    r"Login screen not reached|Kitchen screen not reached|NewConnectionError|cannot connect",
    re.I,
)
HIGH_WORDS = re.compile(r"manager account|sql|script|injection|password|signed in|logged in|crash|logout|session", re.I)
LOW_WORDS = re.compile(r"version|title|label|name is shown|text", re.I)


def read_doc_info():
    """Map test function name -> (module title, docstring) by reading the test files."""
    info = {}
    for path in sorted(glob.glob(os.path.join(HERE, "test_*.py"))):
        tree = ast.parse(open(path, encoding="utf-8").read())
        module_title = ""
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "MODULE" for t in node.targets):
                module_title = ast.literal_eval(node.value)
        mdoc = (ast.get_docstring(tree) or "").splitlines()
        module_title = module_title or (mdoc[0] if mdoc else os.path.basename(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                info[node.name] = (module_title, ast.get_docstring(node) or "")
    return info


def split_doc(doc):
    """'Do this.\nExpected: that.' -> (steps, expected)"""
    m = re.search(r"Expected:\s*(.*)", doc, re.S)
    expected = m.group(1).strip() if m else ""
    steps = doc[: m.start()].strip() if m else doc.strip()
    return " ".join(steps.split()), " ".join(expected.split())


def short(text, n=300):
    text = " ".join((text or "").split())
    return text if len(text) <= n else text[: n - 1] + "…"


def parse(xml_path):
    root = ET.parse(xml_path).getroot()
    rows = []
    for tc in root.iter("testcase"):
        name = tc.get("name", "")
        base = re.sub(r"\[.*\]$", "", name)
        param = name[len(base):]
        status, message = "passed", ""
        for tag, st in (("failure", "failed"), ("error", "error"), ("skipped", "skipped")):
            el = tc.find(tag)
            if el is not None:
                status, message = st, (el.get("message") or "") + " " + (el.text or "")
                if st == "skipped" and (el.get("type") == "pytest.xfail" or "xfail" in message.lower()):
                    status = "xfail"
                break
        rows.append({
            "file": (tc.get("classname") or "").split(".")[-1],
            "name": name, "base": base, "param": param,
            "status": status, "message": message.strip(),
            "time": float(tc.get("time") or 0),
        })
    return rows


def classify(rows):
    for r in rows:
        r["kind"] = r["status"]
        if r["status"] in ("failed", "error") and ENV_PATTERNS.search(r["message"]):
            r["kind"] = "env"
    return rows


def severity(title, message):
    if HIGH_WORDS.search(title) or HIGH_WORDS.search(message[:200]):
        return "High"
    if LOW_WORDS.search(title):
        return "Low"
    return "Medium"


def build(rows, docs, xml_path):
    now = datetime.now().strftime("%d-%b-%Y %H:%M")
    counts = OrderedDict((k, 0) for k in ("passed", "failed", "env", "skipped", "xfail", "error"))
    for r in rows:
        counts[r["kind"]] = counts.get(r["kind"], 0) + 1
    total = len(rows)

    # numbered bugs
    bugs = []
    for r in rows:
        if r["kind"] in ("failed", "error"):
            module, doc = docs.get(r["base"], ("", ""))
            steps, expected = split_doc(doc)
            title = r["base"].replace("test_", "").replace("_", " ").strip().capitalize() + r["param"]
            msg = short(r["message"].split("\n")[0] if r["message"] else "", 300)
            shot = os.path.join("failures", r["name"] + ".png")
            bugs.append({
                "id": f"KBUG-{len(bugs) + 1:02d}", "module": module or r["file"], "title": title,
                "steps": steps or "(see test)", "expected": expected or "(see test)",
                "actual": msg or "(no message)", "severity": severity(title, r["message"]),
                "shot": shot if os.path.exists(os.path.join(HERE, shot)) else "",
                "test": f"{r['file']}.py::{r['name']}",
            })

    # module table
    mods = OrderedDict()
    for r in rows:
        module = docs.get(r["base"], (r["file"], ""))[0]
        m = mods.setdefault(module, {"passed": 0, "failed": 0, "env": 0, "skipped": 0, "xfail": 0, "error": 0})
        m[r["kind"]] = m.get(r["kind"], 0) + 1

    md = []
    md.append("# Bug Report - Kitchen Staff APK\n")
    md.append(f"Generated: {now}  |  Source: `{os.path.relpath(xml_path, HERE)}`  |  App: KitchenStaff_QA v2.0.0 "
              f"(com.softland.fod_kitchen_staff)\n")
    md.append("## 1. Summary\n")
    md.append("| Result | Count |\n|---|---|")
    labels = {"passed": "Passed", "failed": "Failed - real findings (bugs)", "env": "Environment problem (not a bug)",
              "skipped": "Skipped (not run)", "xfail": "Known issue (expected failure)", "error": "Setup error"}
    for key, label in labels.items():
        md.append(f"| {label} | {counts.get(key, 0)} |")
    md.append(f"| **Total tests** | **{total}** |\n")
    if counts.get("env"):
        md.append(f"> {counts['env']} test(s) did not finish because the test tool or phone failed (Appium helper "
                  f"crash, phone not connected, login screen not reached). They are listed in section 4 and are not bugs.\n")

    md.append("## 2. Results by module\n")
    md.append("| Module | Passed | Failed | Env problem | Skipped | Known |\n|---|---|---|---|---|---|")
    for name, m in mods.items():
        md.append(f"| {name} | {m['passed']} | {m['failed'] + m.get('error', 0)} | {m['env']} | {m['skipped']} | {m['xfail']} |")
    md.append("")

    md.append("## 3. Bugs found\n")
    if not bugs:
        md.append("No failures caused by the application in this run.\n")
    else:
        md.append("| ID | Module | Title | Severity |\n|---|---|---|---|")
        for b in bugs:
            md.append(f"| {b['id']} | {b['module']} | {b['title']} | {b['severity']} |")
        md.append("")
        for b in bugs:
            md.append(f"### {b['id']} - {b['title']}")
            md.append(f"- Module: {b['module']}  |  Severity: {b['severity']}  |  Status: Open")
            md.append(f"- Steps: {b['steps']}")
            md.append(f"- Expected: {b['expected']}")
            md.append(f"- Actual: {b['actual']}")
            md.append(f"- Test: `{b['test']}`")
            if b["shot"]:
                md.append(f"- Screenshot: `{b['shot']}`")
            md.append("")

    md.append("## 4. Environment problems (not application bugs)\n")
    envs = [r for r in rows if r["kind"] == "env"]
    if not envs:
        md.append("None.\n")
    else:
        reasons = OrderedDict()
        for r in envs:
            key = short(r["message"].split("\n")[0], 140)
            reasons.setdefault(key, []).append(r["name"])
        for reason, names in reasons.items():
            md.append(f"- **{reason}** - {len(names)} test(s), e.g. `{names[0]}`")
        md.append("\nFixes to try: reconnect the phone and tap Allow; run `python find_kitchen_app.py`; check "
                  "`kitchen.env`; try an Android emulator or a non-vivo phone if the Appium helper keeps crashing.\n")

    md.append("## 5. Skipped tests\n")
    skipped = [r for r in rows if r["kind"] == "skipped"]
    if not skipped:
        md.append("None.\n")
    else:
        md.append("| Test | Reason |\n|---|---|")
        for r in skipped:
            md.append(f"| `{r['name']}` | {short(r['message'].split(chr(10))[0].replace('|', '/'), 120)} |")
        md.append("")

    md.append("## 6. Known issues already marked in the tests\n")
    known = [r for r in rows if r["kind"] == "xfail"]
    md.append("None.\n" if not known else "\n".join(f"- `{r['name']}`" for r in known) + "\n")

    return "\n".join(md), bugs, counts, mods


def to_html(md_text, title):
    """Very small Markdown-to-HTML so the report can be opened in a browser or printed."""
    out, in_table = [], False
    for line in md_text.splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):
                continue
            if not in_table:
                out.append("<table>")
                in_table = True
                out.append("<tr>" + "".join(f"<th>{html.escape(c)}</th>" for c in cells) + "</tr>")
            else:
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
            continue
        if in_table:
            out.append("</table>")
            in_table = False
        if line.startswith("### "):
            out.append(f"<h3>{inline(line[4:])}</h3>")
        elif line.startswith("## "):
            out.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("# "):
            out.append(f"<h1>{inline(line[2:])}</h1>")
        elif line.startswith("- "):
            out.append(f"<li>{inline(line[2:])}</li>")
        elif line.startswith("> "):
            out.append(f"<blockquote>{inline(line[2:])}</blockquote>")
        elif line.strip():
            out.append(f"<p>{inline(line)}</p>")
    if in_table:
        out.append("</table>")
    css = ("body{font-family:Segoe UI,Arial,sans-serif;max-width:960px;margin:24px auto;padding:0 16px;color:#222}"
           "table{border-collapse:collapse;width:100%;margin:10px 0}th,td{border:1px solid #ccc;padding:6px 8px;text-align:left}"
           "th{background:#f2f2f2}code{background:#f4f4f4;padding:1px 4px}blockquote{background:#fff7e6;border-left:4px solid #e69500;"
           "margin:10px 0;padding:6px 12px}h1{color:#c45500}")
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(title)}</title><style>{css}</style></head><body>" \
           + "\n".join(out) + "</body></html>"


def inline(text):
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", text)


def main():
    xml_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_XML
    if not os.path.exists(xml_path):
        raise SystemExit(f"Results file not found: {xml_path}\nRun  python run_kitchen_tests.py  first.")
    rows = classify(parse(xml_path))
    md, bugs, counts, _ = build(rows, read_doc_info(), xml_path)
    md_path = os.path.join(HERE, "Bug_Report_Kitchen_APK.md")
    html_path = os.path.join(HERE, "Bug_Report_Kitchen_APK.html")
    open(md_path, "w", encoding="utf-8").write(md)
    open(html_path, "w", encoding="utf-8").write(to_html(md, "Bug Report - Kitchen Staff APK"))
    print(f"Tests: {len(rows)}  passed: {counts['passed']}  bugs: {len(bugs)}  env problems: {counts['env']}  "
          f"skipped: {counts['skipped']}")
    print("Wrote:", md_path)
    print("Wrote:", html_path)


if __name__ == "__main__":
    main()
