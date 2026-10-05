#!/usr/bin/env python3
"""
Signature Shield Basic — universal file scanner (download-only, no accounts).
Detects the OS at runtime and applies the matching protection profile.

What it really does:
  * SHA-256 signature scan of files against tools/signatures.json
    (starter DB ships the industry-standard EICAR test marker hash so the
    scanner is verifiable out of the box; add your own hashes with sig-add)
  * Flags known-bad filename patterns (double extensions like invoice.pdf.exe)
  * Quarantine: moves flagged files aside with a restore manifest
  * Scheduled scans: prints the exact command to schedule scans on YOUR os
    (schtasks on Windows, launchd plist on macOS, cron on Linux) — it never
    installs anything silently.

Usage:
  python3 shield_basic.py scan --type quick|full|custom|usb|startup|memory [--path P] [--clean] [--yes]
  python3 shield_basic.py scan <folder> [--quarantine]   (classic folder scan)
  python3 shield_basic.py sig-add <sha256> <label>
  python3 shield_basic.py quarantine-list
  python3 shield_basic.py restore <quarantine-id>
  python3 shield_basic.py schedule
  python3 shield_basic.py osinfo
  python3 shield_basic.py --self-test
"""
import hashlib
import json
import os
import platform
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SIG_DB = os.path.join(HERE, "signatures.json")

def _qdir():
    """Quarantine dir, resolved against the CURRENT working directory.

    The journal's rewind does os.chdir(home) before calling restore(),
    so this must be lazy — never bound at import time. An explicit
    module-global override (used by self-tests) still wins."""
    return globals().get("QDIR") or os.path.join(os.getcwd(), "shield_quarantine")

def _qmanifest():
    return globals().get("QMANIFEST") or os.path.join(_qdir(), "manifest.json")

def __getattr__(name):
    # PEP 562: keep QDIR/QMANIFEST readable as module attributes
    if name == "QDIR":
        return _qdir()
    if name == "QMANIFEST":
        return _qmanifest()
    raise AttributeError("module %r has no attribute %r" % (__name__, name))

OS = platform.system()  # Windows | Darwin | Linux | ...
OS_LABEL = {"Windows": "Windows", "Darwin": "macOS", "Linux": "Linux"}.get(OS, OS)

DOUBLE_EXT = (".pdf.exe", ".doc.exe", ".docx.exe", ".xls.exe", ".xlsx.exe",
              ".jpg.exe", ".png.exe", ".txt.exe", ".zip.exe", ".mp3.exe",
              ".scr", ".pif", ".bat.exe", ".cmd.exe")


def detect_os():
    return {"system": OS, "label": OS_LABEL,
            "release": platform.release(), "machine": platform.machine()}


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


def scan_dir(root, quarantine=False):
    """Scan every file under root. Returns list of finding dicts."""
    db = load_db()
    sigs = db.get("sha256", {})
    bad_names = [n.lower() for n in db.get("filenames", [])]
    findings = []
    scanned = 0
    for dirpath, _dirs, files in os.walk(root):
        if os.path.abspath(dirpath).startswith(os.path.abspath(_qdir())):
            continue
        for name in files:
            path = os.path.join(dirpath, name)
            scanned += 1
            try:
                digest = sha256_of(path)
            except OSError:
                continue
            reasons = []
            if digest in sigs:
                reasons.append("signature match: %s" % sigs[digest])
            low = name.lower()
            if low in bad_names:
                reasons.append("known-bad filename")
            if low.endswith(DOUBLE_EXT):
                reasons.append("double extension (classic malware disguise)")
            if reasons:
                findings.append({"path": path, "sha256": digest,
                                 "reasons": reasons})
                if quarantine:
                    quarantine_file(path, reasons)
    return {"scanned": scanned, "findings": findings,
            "quarantined": quarantine}


def quarantine_file(path, reasons):
    os.makedirs(_qdir(), exist_ok=True)
    qid = "q%08d" % (int(time.time() * 100) % 100000000)
    # guarantee uniqueness: two quarantines in the same centisecond must not collide
    taken = {e.get("id") for e in quarantine_list()}
    n = 0
    base = qid
    while qid in taken:
        n += 1
        qid = "%s_%d" % (base, n)
    dest = os.path.join(_qdir(), qid + "_" + os.path.basename(path))
    shutil.move(path, dest)
    manifest = []
    if os.path.exists(_qmanifest()):
        with open(_qmanifest(), "r", encoding="utf-8") as f:
            try:
                manifest = json.load(f)
            except ValueError:
                manifest = []
    manifest.append({"id": qid, "original": path, "quarantined": dest,
                     "reasons": reasons, "time": time.strftime("%Y-%m-%d %H:%M:%S")})
    with open(_qmanifest(), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    return qid


def quarantine_list():
    if not os.path.exists(_qmanifest()):
        return []
    with open(_qmanifest(), "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except ValueError:
            return []


def restore(qid):
    manifest = quarantine_list()
    for entry in manifest:
        if entry["id"] == qid:
            os.makedirs(os.path.dirname(entry["original"]), exist_ok=True)
            shutil.move(entry["quarantined"], entry["original"])
            manifest.remove(entry)
            with open(_qmanifest(), "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)
            return entry["original"]
    return None


def schedule_hint():
    script = os.path.abspath(__file__)
    if OS == "Windows":
        return ("Windows scheduled scan — run this in an admin Command Prompt:\n"
                '  schtasks /create /tn "SignatureShield" /tr "python \\"%s\\" scan %%USERPROFILE%%"\n'
                '    /sc weekly /d SUN /st 02:00' % script)
    if OS == "Darwin":
        return ("macOS scheduled scan — save as ~/Library/LaunchAgents/com.signature.shield.plist\n"
                "and run: launchctl load ~/Library/LaunchAgents/com.signature.shield.plist\n"
                "The plist should run: /usr/bin/python3 \"%s\" scan ~  (weekly, Sunday 02:00)" % script)
    return ("Linux scheduled scan — add to your crontab (crontab -e):\n"
            "  0 2 * * 0 /usr/bin/python3 \"%s\" scan ~" % script)


def self_test():
    import tempfile
    tmp = tempfile.mkdtemp(prefix="shieldtest_")
    try:
        # EICAR standard anti-malware test string (harmless by design)
        eicar = (r"X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*")
        with open(os.path.join(tmp, "eicar.com"), "w") as f:
            f.write(eicar)
        with open(os.path.join(tmp, "notes.txt"), "w") as f:
            f.write("just a clean note")
        with open(os.path.join(tmp, "invoice.pdf.exe"), "w") as f:
            f.write("suspicious name")
        res = scan_dir(tmp, quarantine=False)
        names = {os.path.basename(f["path"]) for f in res["findings"]}
        assert res["scanned"] == 3, "expected 3 files scanned, got %d" % res["scanned"]
        assert "eicar.com" in names, "EICAR test file NOT detected"
        assert "invoice.pdf.exe" in names, "double-extension file NOT flagged"
        assert "notes.txt" not in names, "clean file wrongly flagged"
        # quarantine + restore round-trip
        global QDIR, QMANIFEST
        QDIR = os.path.join(tmp, "q")
        QMANIFEST = os.path.join(QDIR, "manifest.json")
        qid = quarantine_file(os.path.join(tmp, "invoice.pdf.exe"), ["test"])
        assert not os.path.exists(os.path.join(tmp, "invoice.pdf.exe"))
        restored = restore(qid)
        assert restored and os.path.exists(restored), "restore failed"
        print("SELF-TEST PASS  os=%s  scanned=%d  detections=%d  quarantine+restore ok"
              % (OS, res["scanned"], len(res["findings"])))
        return 0
    except AssertionError as e:
        print("SELF-TEST FAIL: %s" % e)
        return 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv):
    if "--self-test" in argv or "selftest" in argv:
        return self_test()
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__.strip())
        return 0
    cmd = argv[0]
    if cmd == "osinfo":
        print(json.dumps(detect_os(), indent=2))
        return 0
    if cmd == "scan":
        # New style: scan --type quick|full|custom|usb|startup|memory [--path P] [--clean] [--yes]
        # Old style (still works): scan <folder> [--quarantine]
        if len(argv) > 1 and argv[1].startswith("--"):
            from shield_scan import run_scan, print_result, clean_findings, SCAN_TYPES
            args = argv[1:]
            stype, paths, clean, yes = "quick", [], False, False
            i = 0
            while i < len(args):
                a = args[i]
                if a == "--type" and i + 1 < len(args):
                    stype = args[i + 1]; i += 2
                elif a == "--path" and i + 1 < len(args):
                    paths.append(args[i + 1]); i += 2
                elif a == "--clean":
                    clean = True; i += 1
                elif a in ("--yes", "-y"):
                    yes = True; i += 1
                else:
                    i += 1
            if stype not in SCAN_TYPES:
                print("unknown scan type '%s' — choose: %s" % (stype, ", ".join(SCAN_TYPES)))
                return 2
            print("OS profile: %s" % OS_LABEL)
            res = run_scan(stype, paths=paths or None)
            print_result(res)
            if clean and res.get("findings"):
                n = clean_findings(res, quarantine_file, journal_home=os.getcwd(), assume_yes=yes)
                print("cleaned %d item(s) — restore anytime with: python3 %s restore <id>"
                      % (n, os.path.basename(__file__)))
            return 0
        root = argv[1] if len(argv) > 1 else "."
        quar = "--quarantine" in argv
        res = scan_dir(root, quarantine=quar)
        print("OS profile: %s" % OS_LABEL)
        print("Scanned %d files in %s" % (res["scanned"], root))
        if not res["findings"]:
            print("Clean — no threats found.")
        for f in res["findings"]:
            print("FLAGGED: %s" % f["path"])
            for r in f["reasons"]:
                print("    - %s" % r)
        return 0
    if cmd == "sig-add":
        digest, label = argv[1], " ".join(argv[2:]) or "custom"
        db = load_db()
        db.setdefault("sha256", {})[digest.lower()] = label
        with open(SIG_DB, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2)
        print("Added signature: %s (%s)" % (digest[:16] + "…", label))
        return 0
    if cmd == "quarantine-list":
        for e in quarantine_list():
            print("%s  %s  (%s)" % (e["id"], e["original"], "; ".join(e["reasons"])))
        return 0
    if cmd == "restore":
        dest = restore(argv[1])
        print("Restored to %s" % dest if dest else "Quarantine id not found.")
        return 0 if dest else 1
    if cmd == "schedule":
        print(schedule_hint())
        return 0
    print("Unknown command: %s (try: scan, quarantine-list, restore, schedule, osinfo)" % cmd)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
