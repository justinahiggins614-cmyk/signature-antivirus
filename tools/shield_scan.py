#!/usr/bin/env python3
"""
Signature Shield — universal scan engine (download-only, stdlib only).

Every scan type is a "Signature" scan: SHA-256 fingerprint check against
tools/signatures.json + heuristic flags (double extensions, risky names,
executables in temp dirs, script keyword heuristics).

Scan types:
  quick    high-risk locations: Downloads, Desktop, home top level, temp dirs
  full     your whole home folder (bounded: skips quarantine, caches, system dirs)
  custom   paths you name:  scan --type custom --path ~/a --path ~/b
  usb      removable media (USB sticks, external drives, SD cards)
  startup  programs set to auto-start with your system (boot entries)
  memory   the program file behind each running process (NOT a RAM dump —
           a website-style "memory scan" can't dump RAM; this honestly checks
           what each running process IS against the threat database)

Usage:
  python3 shield_scan.py --type quick|full|custom|usb|startup|memory [--path P ...]
                         [--clean] [--yes] [--json]
  python3 shield_scan.py --self-test

--clean quarantines findings (asks first unless --yes). Every cleanup is
journaled when shield_journal.py is present, so it can be rewound.
"""
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time

OS = platform.system()  # Windows | Darwin | Linux | ...
HERE = os.path.dirname(os.path.abspath(__file__))
SIG_DB = os.path.join(HERE, "signatures.json")

SCAN_TYPES = ("quick", "full", "custom", "usb", "startup", "memory")

DOUBLE_EXT = (".pdf.exe", ".doc.exe", ".docx.exe", ".xls.exe", ".xlsx.exe",
              ".jpg.exe", ".jpeg.exe", ".png.exe", ".gif.exe", ".txt.exe",
              ".zip.exe", ".rar.exe", ".mp3.exe", ".mp4.exe", ".avi.exe",
              ".scr", ".pif", ".bat.exe", ".cmd.exe", ".lnk.exe")
RISKY_EXT = (".exe", ".scr", ".pif", ".bat", ".cmd", ".ps1", ".vbs", ".vbe",
             ".jse", ".wsf", ".msi", ".com", ".jar")
SUSPICIOUS_KEYWORDS = (
    "powershell -enc", "powershell -encodedcommand", "cmd /c", "wscript",
    "cscript", "regsvr32", "rundll32", "certutil -decode", "bitsadmin",
    "mimikatz", "invoke-mimikatz", "curl http", "wget http",
    "nc -e", "ncat -e", "/dev/tcp/", "chmod +x /tmp", "base64 -d",
    "eval(base64", 'createobject("wscript.shell")', "frombase64string",
    "downloadstring", "iex(", "start-process", "schtasks /create",
)
SKIP_DIRS = {".cache", ".npm", ".mozilla", ".config/google-chrome", "shield_quarantine",
             "__pycache__", ".git", "node_modules", ".venv", "venv"}


def load_db():
    try:
        with open(SIG_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"sha256": {}, "filenames": []}


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_file(path, db):
    """Return list of reasons the file is suspicious, [] if clean."""
    reasons = []
    name = os.path.basename(path)
    low = name.lower()
    sigs = db.get("sha256", {})
    bad_names = [n.lower() for n in db.get("filenames", [])]
    if low in bad_names:
        reasons.append("filename is on the known-threat list")
    for de in DOUBLE_EXT:
        if low.endswith(de):
            reasons.append("double extension disguise (%s) — pretends to be a document/image but is executable" % de)
            break
    try:
        digest = sha256_of(path)
    except OSError:
        return ["unreadable file"]
    if digest in sigs:
        label = sigs[digest] if isinstance(sigs[digest], str) else sigs[digest].get("label", "known threat")
        reasons.append("KNOWN THREAT — fingerprint matches: %s" % label)
    # executables hiding in temp dirs
    tmp = tempfile.gettempdir().lower()
    if low.endswith(RISKY_EXT) and os.path.dirname(os.path.abspath(path)).lower().startswith(tmp):
        reasons.append("executable sitting in a temp folder — a classic dropper hiding spot")
    # script keyword heuristics (small text files only)
    if low.endswith((".ps1", ".vbs", ".js", ".bat", ".cmd", ".sh", ".py")):
        try:
            if os.path.getsize(path) < 200000:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    head = f.read(20000).lower()
                hits = [k for k in SUSPICIOUS_KEYWORDS if k in head]
                if hits:
                    reasons.append("script contains suspicious commands: %s" % ", ".join(hits[:3]))
        except OSError:
            pass
    return reasons


def scan_paths(paths, db=None, quarantine_fn=None, max_depth=None):
    """Scan every file under the given paths. Returns result dict.
    max_depth: None = fully recursive; 0 = top-level files only."""
    db = db or load_db()
    findings = []
    scanned = 0
    skipped = 0
    qdir = os.path.abspath(os.path.join(os.getcwd(), "shield_quarantine"))
    for root in paths:
        root = os.path.expanduser(root)
        if os.path.isfile(root):
            todo = [(os.path.dirname(root), [], [os.path.basename(root)])]
        elif os.path.isdir(root):
            todo = None
        else:
            skipped += 1
            continue
        if todo is None:
            walker = os.walk(root)
        else:
            walker = iter(todo)
        base_depth = os.path.abspath(root).count(os.sep)
        for dirpath, _dirs, files in walker:
            if max_depth is not None and todo is None:
                if os.path.abspath(dirpath).count(os.sep) - base_depth > max_depth:
                    _dirs[:] = []
                    continue
            if os.path.abspath(dirpath).startswith(qdir):
                continue
            if os.path.basename(dirpath) in SKIP_DIRS:
                continue
            for name in files:
                path = os.path.join(dirpath, name)
                scanned += 1
                try:
                    reasons = check_file(path, db)
                except OSError:
                    skipped += 1
                    continue
                if reasons:
                    f = {"path": path, "reasons": reasons}
                    try:
                        f["sha256"] = sha256_of(path)
                    except OSError:
                        pass
                    findings.append(f)
                    if quarantine_fn:
                        f["quarantined_as"] = quarantine_fn(path, reasons)
    return {"scanned": scanned, "findings": findings, "skipped": skipped}


# ---------------- scan-type target discovery ----------------

def quick_targets():
    # (path, max_depth): home itself is top-level only so "quick" stays quick
    home = os.path.expanduser("~")
    cands = [(os.path.join(home, "Downloads"), None),
             (os.path.join(home, "Desktop"), None),
             (os.path.join(home, "Documents"), None),
             (tempfile.gettempdir(), 1),
             (home, 0)]
    return [(c, d) for c, d in cands if os.path.isdir(c)]


def full_targets():
    return [os.path.expanduser("~")]


def usb_targets():
    found = []
    if OS == "Linux":
        user = os.environ.get("USER", "")
        for base in ("/media/" + user, "/run/media/" + user, "/media", "/mnt"):
            if os.path.isdir(base):
                for e in os.listdir(base):
                    p = os.path.join(base, e)
                    if os.path.isdir(p) and (os.path.ismount(p) or True):
                        # only real mounts, not the base dir itself
                        if p != base and os.path.ismount(p):
                            found.append(p)
    elif OS == "Darwin":
        vol = "/Volumes"
        if os.path.isdir(vol):
            for e in os.listdir(vol):
                if e != "Macintosh HD":
                    p = os.path.join(vol, e)
                    if os.path.isdir(p):
                        found.append(p)
    elif OS == "Windows":
        try:
            import ctypes
            getdt = ctypes.windll.kernel32.GetDriveTypeW
            for i in range(68, 91):  # D:..Z:
                d = chr(i) + ":\\"
                if os.path.exists(d) and getdt(d) == 2:  # DRIVE_REMOVABLE
                    found.append(d)
        except Exception:
            for i in range(68, 91):
                d = chr(i) + ":\\"
                if os.path.exists(d):
                    found.append(d)
    return found


def _win_startup_entries():
    entries = []
    try:
        import winreg
        for hive, sub in ((winreg.HKEY_CURRENT_USER,
                           r"Software\Microsoft\Windows\CurrentVersion\Run"),
                          (winreg.HKEY_CURRENT_USER,
                           r"Software\Microsoft\Windows\CurrentVersion\RunOnce")):
            try:
                with winreg.OpenKey(hive, sub) as k:
                    for i in range(winreg.QueryInfoKey(k)[1]):
                        name, val, _t = winreg.EnumValue(k, i)
                        entries.append(("registry Run: " + name, str(val)))
            except OSError:
                pass
    except ImportError:
        pass
    startup = os.path.join(os.environ.get("APPDATA", ""),
                           r"Microsoft\Windows\Start Menu\Programs\Startup")
    if os.path.isdir(startup):
        for e in os.listdir(startup):
            entries.append(("Startup folder", os.path.join(startup, e)))
    return entries


def _mac_startup_entries():
    import plistlib
    entries = []
    dirs = [os.path.expanduser("~/Library/LaunchAgents"),
            "/Library/LaunchAgents", "/Library/LaunchDaemons"]
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for e in os.listdir(d):
            if not e.endswith(".plist"):
                continue
            p = os.path.join(d, e)
            try:
                with open(p, "rb") as f:
                    pl = plistlib.load(f)
                prog = pl.get("Program") or (pl.get("ProgramArguments") or [None])[0]
                if prog:
                    entries.append(("launchd: " + e, str(prog)))
            except Exception:
                pass
    return entries


def _linux_startup_entries():
    entries = []
    ad = os.path.expanduser("~/.config/autostart")
    if os.path.isdir(ad):
        for e in os.listdir(ad):
            if e.endswith(".desktop"):
                try:
                    with open(os.path.join(ad, e), encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if line.startswith("Exec="):
                                entries.append(("autostart: " + e, line[5:].strip()))
                                break
                except OSError:
                    pass
    try:
        out = subprocess.run(["crontab", "-l"], capture_output=True, text=True,
                             timeout=10).stdout
        for line in out.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                entries.append(("crontab", line))
    except Exception:
        pass
    return entries


def _exe_from_entry(value):
    """Pull the executable path out of a startup entry value."""
    import re
    v = value.strip().strip('"')
    m = re.match(r'^"([^"]+)"', value.strip())
    if m:
        return m.group(1)
    m = re.match(r"^'([^']+)'", value.strip())
    if m:
        return m.group(1)
    tok = v.split()[0]
    # crontab lines: skip schedule fields
    if re.match(r"^(@|\*|[\d,/\-]+\s+){5}", v):
        rest = re.sub(r"^(@\w+|(\*|[\d,/\-]+)\s+){5,6}", "", v).strip()
        tok = rest.split()[0] if rest else ""
    return tok


def startup_targets():
    if OS == "Windows":
        raw = _win_startup_entries()
    elif OS == "Darwin":
        raw = _mac_startup_entries()
    else:
        raw = _linux_startup_entries()
    targets = []
    for label, val in raw:
        exe = _exe_from_entry(val)
        if exe and os.path.isfile(exe):
            targets.append({"label": label, "path": exe})
        elif exe:
            targets.append({"label": label, "path": exe, "missing": True})
    return targets


def memory_targets():
    """Program files behind running processes. Honest: not a RAM dump."""
    procs = []
    if OS == "Linux" and os.path.isdir("/proc"):
        for pid in os.listdir("/proc"):
            if not pid.isdigit():
                continue
            exe = os.path.join("/proc", pid, "exe")
            try:
                target = os.readlink(exe)
                if target and not target.startswith("["):
                    procs.append({"pid": int(pid), "exe": target})
            except OSError:
                pass
    elif OS == "Darwin":
        try:
            out = subprocess.run(["ps", "-axo", "pid=,comm="], capture_output=True,
                                 text=True, timeout=15).stdout
            for line in out.splitlines():
                parts = line.strip().split(None, 1)
                if len(parts) == 2 and parts[0].isdigit():
                    procs.append({"pid": int(parts[0]), "exe": parts[1]})
        except Exception:
            pass
    elif OS == "Windows":
        try:
            out = subprocess.run(["wmic", "process", "get", "ProcessId,ExecutablePath",
                                  "/FORMAT:CSV"], capture_output=True, text=True,
                                 timeout=30).stdout
            for line in out.splitlines():
                parts = [p.strip() for p in line.split(",")]
                if len(parts) == 3 and parts[2].isdigit() and parts[1]:
                    procs.append({"pid": int(parts[2]), "exe": parts[1]})
        except Exception:
            pass
    # dedupe by exe path
    seen, uniq = set(), []
    for p in procs:
        if p["exe"] not in seen:
            seen.add(p["exe"])
            uniq.append(p)
    return uniq


# ---------------- run ----------------

SCAN_DESCRIPTIONS = {
    "quick": "Quick scan — Downloads, Desktop, Documents, temp folders and your home top level. The everyday check.",
    "full": "Full scan — your entire home folder. Thorough; takes a while.",
    "custom": "Custom scan — only the folders or files you name.",
    "usb": "USB / removable media scan — every plugged-in stick, drive and card.",
    "startup": "Startup scan — every program set to auto-start with your system, checked one by one.",
    "memory": "Memory scan — the program file behind each running process, checked against the threat database. (Honest note: this checks what each process IS, not a RAM dump.)",
}


def run_scan(scan_type, paths=None, db=None, quarantine_fn=None):
    db = db or load_db()
    t0 = time.time()
    result = {"type": scan_type, "description": SCAN_DESCRIPTIONS[scan_type],
              "os": OS, "findings": [], "scanned": 0, "skipped": 0,
              "notes": []}
    if scan_type == "quick":
        r = {"scanned": 0, "findings": [], "skipped": 0}
        for path, depth in quick_targets():
            one = scan_paths([path], db, quarantine_fn, max_depth=depth)
            r["scanned"] += one["scanned"]
            r["findings"] += one["findings"]
            r["skipped"] += one["skipped"]
    elif scan_type == "full":
        r = scan_paths(full_targets(), db, quarantine_fn)
    elif scan_type == "custom":
        if not paths:
            return dict(result, error="custom scan needs --path <folder>")
        r = scan_paths(paths, db, quarantine_fn)
    elif scan_type == "usb":
        targets = usb_targets()
        if not targets:
            result["notes"].append("no removable media found plugged in")
            r = {"scanned": 0, "findings": [], "skipped": 0}
        else:
            result["targets"] = targets
            r = scan_paths(targets, db, quarantine_fn)
    elif scan_type == "startup":
        entries = startup_targets()
        result["entries"] = [{"label": e["label"], "path": e["path"],
                              "missing": e.get("missing", False)} for e in entries]
        files = [e["path"] for e in entries if not e.get("missing") and os.path.isfile(e["path"])]
        missing = [e for e in entries if e.get("missing")]
        if missing:
            result["notes"].append("%d auto-start entry points at a missing file" % len(missing))
            for e in missing:
                result["findings"].append(
                    {"path": e["path"],
                     "reasons": ["auto-start entry (%s) points at a file that no longer exists — "
                                 "a classic sign of a removed-but-not-cleaned infection" % e["label"]]})
        r = scan_paths(files, db, quarantine_fn) if files else {"scanned": 0, "findings": [], "skipped": 0}
    elif scan_type == "memory":
        procs = memory_targets()
        result["processes"] = len(procs)
        files = [p["exe"] for p in procs if os.path.isfile(p["exe"])]
        r = scan_paths(files, db, quarantine_fn) if files else {"scanned": 0, "findings": [], "skipped": 0}
        # attach owning pids to findings
        bypath = {}
        for p in procs:
            bypath.setdefault(p["exe"], []).append(p["pid"])
        for f in r["findings"]:
            f["pids"] = bypath.get(f["path"], [])
    else:
        return dict(result, error="unknown scan type: %s" % scan_type)
    result.update({k: r[k] for k in ("scanned", "findings", "skipped") if k in r})
    result["seconds"] = round(time.time() - t0, 1)
    return result


def print_result(res):
    print("Signature %s scan — %s" % (res["type"], res.get("description", "")))
    print("Scanned %d files in %ss." % (res["scanned"], res.get("seconds", "?")))
    for n in res.get("notes", []):
        print("Note: %s" % n)
    if res.get("error"):
        print("ERROR: %s" % res["error"])
        return
    if not res["findings"]:
        print("Clean — nothing suspicious found.")
        return
    print("FOUND %d suspicious item(s):" % len(res["findings"]))
    for f in res["findings"]:
        extra = ("  [running as PID %s]" % ",".join(map(str, f["pids"]))) if f.get("pids") else ""
        print("  ! %s%s" % (f["path"], extra))
        for r in f["reasons"]:
            print("      - %s" % r)
        if f.get("quarantined_as"):
            print("      quarantined -> %s" % f["quarantined_as"])


def clean_findings(res, quarantine_fn, journal_home=None, assume_yes=False):
    """Quarantine every finding, with confirmation + journaling. Returns count."""
    try:
        import shield_journal
    except ImportError:
        shield_journal = None
    done = 0
    for f in res.get("findings", []):
        if f.get("quarantined_as"):
            continue
        if not assume_yes:
            ans = input("Quarantine %s? [y/N] " % f["path"]).strip().lower()
            if ans not in ("y", "yes"):
                print("  skipped.")
                continue
        qid = quarantine_fn(f["path"], f["reasons"])
        f["quarantined_as"] = qid
        done += 1
        print("  quarantined (%s)" % qid)
        if shield_journal and journal_home:
            shield_journal.record(journal_home, "shield_scan", "quarantine",
                                  {"path": f["path"], "reasons": f["reasons"]},
                                  {"op": "restore_quarantine", "qid": qid})
    return done


def self_test():
    tmp = tempfile.mkdtemp(prefix="scantest_")
    ok = True
    try:
        # EICAR standard test marker
        eicar = (r"X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*")
        p1 = os.path.join(tmp, "eicar.com")
        with open(p1, "w") as f:
            f.write(eicar)
        p2 = os.path.join(tmp, "invoice.pdf.exe")
        with open(p2, "w") as f:
            f.write("hello")
        p3 = os.path.join(tmp, "notes.txt")
        with open(p3, "w") as f:
            f.write("just notes")
        db = load_db()
        eicar_hit = any("KNOWN THREAT" in r for r in check_file(p1, db))
        dbl_hit = any("double extension" in r for r in check_file(p2, db))
        clean_ok = check_file(p3, db) == []
        print("eicar:%s double-ext:%s clean:%s" % (eicar_hit, dbl_hit, clean_ok))
        ok = ok and eicar_hit and dbl_hit and clean_ok
        for t in ("quick", "custom", "startup", "memory"):
            try:
                if t == "custom":
                    r = run_scan(t, paths=[tmp])
                else:
                    r = run_scan(t)
                assert r["type"] == t and "findings" in r
                print("scan-type %s ok (scanned %d)" % (t, r["scanned"]))
            except Exception as e:
                print("scan-type %s FAILED: %s" % (t, e))
                ok = False
        r = run_scan("custom", paths=[tmp])
        names = {os.path.basename(f["path"]) for f in r["findings"]}
        assert "eicar.com" in names and "invoice.pdf.exe" in names, names
        print("custom scan found both test threats")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("SCAN SELF-TEST " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    stype = "quick"
    paths = []
    clean = False
    yes = False
    as_json = False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--type" and i + 1 < len(argv):
            stype = argv[i + 1]; i += 2
        elif a == "--path" and i + 1 < len(argv):
            paths.append(argv[i + 1]); i += 2
        elif a == "--clean":
            clean = True; i += 1
        elif a in ("--yes", "-y"):
            yes = True; i += 1
        elif a == "--json":
            as_json = True; i += 1
        elif a in ("--self-test", "selftest"):
            return self_test()
        elif a in ("-h", "--help", "help"):
            print(__doc__.strip()); return 0
        else:
            i += 1
    if stype not in SCAN_TYPES:
        print("unknown scan type '%s' — choose: %s" % (stype, ", ".join(SCAN_TYPES)))
        return 2
    res = run_scan(stype, paths=paths or None)
    if clean and res.get("findings"):
        # quarantine directly (no per-file callback): use local quarantine dir
        qdir = os.path.join(os.getcwd(), "shield_quarantine")
        os.makedirs(qdir, exist_ok=True)
        def _q(path, reasons):
            dest = os.path.join(qdir, "%d_%s" % (int(time.time() * 1000), os.path.basename(path)))
            shutil.move(path, dest)
            return dest
        n = clean_findings(res, _q, journal_home=os.getcwd(), assume_yes=yes)
        print("cleaned %d item(s)" % n)
    if as_json:
        print(json.dumps(res, indent=2))
    else:
        print_result(res)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
