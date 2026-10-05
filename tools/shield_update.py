#!/usr/bin/env python3
"""
Signature Shield signature-database updater.

This is the "internal AI regulates updates" piece: it checks the canonical
Signature threat database for new data and applies it — with confirmation
and a journaled, rewindable record, like every other Shield action.

    python3 shield_update.py check          # is newer signature data available?
    python3 shield_update.py apply [--yes]  # download + install it (asks first)
    python3 shield_update.py version        # local DB version/date
    python3 shield_update.py --self-test    # sandbox test (no network)

The canonical database lives at SHIELD_SIG_URL (default: this project's own
GitHub Pages copy of tools/signatures.json). Tests point it at a file:// URL.

Stdlib only. Never touches the network without being asked.
"""
import json
import os
import shutil
import sys
import tempfile
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SIG_DB = os.path.join(HERE, "signatures.json")

DEFAULT_URL = ("https://justinahiggins614-cmyk.github.io"
               "/signature-antivirus/tools/signatures.json")


def canonical_url():
    return os.environ.get("SHIELD_SIG_URL", DEFAULT_URL)


def ver_tuple(v):
    try:
        return tuple(int(x) for x in str(v).split("."))
    except ValueError:
        return (0,)


def local_db():
    try:
        with open(SIG_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def local_version():
    return local_db().get("meta", {}).get("version", "0")


def fetch_remote(url):
    req = urllib.request.Request(url, headers={"User-Agent": "SignatureShield/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def validate_db(db):
    if not isinstance(db, dict):
        return "not a JSON object"
    if not isinstance(db.get("sha256"), dict):
        return "missing 'sha256' fingerprint map"
    if not isinstance(db.get("filenames"), list):
        return "missing 'filenames' list"
    meta = db.get("meta") or {}
    if not meta.get("version"):
        return "missing meta.version"
    return None


def check():
    """Return (status, message, remote_db_or_None). Never writes anything."""
    lv = local_version()
    try:
        remote = fetch_remote(canonical_url())
    except Exception as e:
        return ("error", "Could not reach the signature database: %s" % e, None)
    problem = validate_db(remote)
    if problem:
        return ("error", "Downloaded database failed validation: %s" % problem, None)
    rv = remote["meta"]["version"]
    if ver_tuple(rv) > ver_tuple(lv):
        return ("update",
                "New signature data available: v%s (local v%s)." % (rv, lv),
                remote)
    return ("current",
            "Protection current as of %s — signature database v%s is the latest."
            % (remote["meta"].get("updated", "?"), rv),
            remote)


def apply_update(remote=None, journal_home=None, assume_yes=False):
    """Install a newer DB. Returns (ok, message). Journaled + rewindable."""
    try:
        import shield_journal as journal
    except ImportError:
        journal = None
    if remote is None:
        status, msg, remote = check()
        if status == "error":
            return (False, msg)
        if status == "current":
            return (True, msg)
    problem = validate_db(remote)
    if problem:
        return (False, "Downloaded database failed validation: %s" % problem)
    rv = remote["meta"]["version"]
    lv = local_version()
    if ver_tuple(rv) <= ver_tuple(lv):
        return (True, "Already on v%s — nothing to do." % lv)
    if not assume_yes:
        ans = input("Install signature database v%s (local v%s)? [y/N] "
                    % (rv, lv)).strip().lower()
        if ans not in ("y", "yes"):
            return (False, "Cancelled — database unchanged.")
    # back up the current DB next to itself, then replace atomically
    backup = SIG_DB + ".bak"
    try:
        if os.path.exists(SIG_DB):
            shutil.copy2(SIG_DB, backup)
        tmp = SIG_DB + ".new"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(remote, f, indent=2)
        os.replace(tmp, SIG_DB)
    except OSError as e:
        return (False, "Could not write the new database: %s" % e)
    if journal and journal_home:
        journal.record(journal_home, "shield_update", "sigdb_update",
                       {"from": lv, "to": rv,
                        "updated": remote["meta"].get("updated", "?")},
                       {"op": "restore_sigdb", "backup": backup,
                        "target": SIG_DB})
    return (True, "Protection current as of %s — signature database v%s installed."
            % (remote["meta"].get("updated", "?"), rv))


def update_scheduler_artifacts(home):
    """Return (kind, description, artifact_text, installer_fn) for a WEEKLY
    automatic signature-database update check — same per-OS pattern the
    installer uses for scheduled scans. Journaled with the shared
    remove_scheduler inverse, so 'undo' removes it."""
    import platform
    import subprocess
    os_name = platform.system()
    upd = os.path.join(home, "bin", "shield_update.py")
    if not os.path.exists(upd):
        upd = os.path.join(HERE, "shield_update.py")
    py = sys.executable or "python3"
    log = os.path.join(home, "update.log")
    cmd = "cd \"%s\" && \"%s\" \"%s\" apply --yes >> \"%s\" 2>&1" % (home, py, upd, log)
    if os_name == "Windows":
        line = ('schtasks /create /tn "SignatureShieldUpdates" /tr "cmd /c %s" '
                "/sc weekly /d SUN /st 04:00 /f" % cmd.replace('"', '\\"'))
        return ("windows-schtasks",
                "a weekly Sunday 4 AM signature-database update via Windows Task Scheduler",
                line,
                lambda: subprocess.run(line, shell=True, capture_output=True, text=True))
    if os_name == "Darwin":
        plist = os.path.expanduser("~/Library/LaunchAgents/com.signature.shield.updates.plist")
        text = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" "
                "\"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n"
                "<plist version=\"1.0\"><dict>\n"
                "  <key>Label</key><string>com.signature.shield.updates</string>\n"
                "  <key>ProgramArguments</key><array>\n"
                "    <string>%s</string>\n"
                "    <string>%s</string>\n"
                "    <string>apply</string>\n"
                "    <string>--yes</string>\n"
                "  </array>\n"
                "  <key>WorkingDirectory</key><string>%s</string>\n"
                "  <key>StartCalendarInterval</key><dict>"
                "<key>Weekday</key><integer>0</integer>"
                "<key>Hour</key><integer>4</integer>"
                "<key>Minute</key><integer>0</integer></dict>\n"
                "  <key>StandardOutPath</key><string>%s</string>\n"
                "  <key>StandardErrorPath</key><string>%s</string>\n"
                "</dict></plist>\n" % (py, upd, home, log, log))

        def do_plist():
            with open(plist, "w", encoding="utf-8") as f:
                f.write(text)
            return subprocess.run(["launchctl", "load", plist],
                                  capture_output=True, text=True)
        return ("macos-launchd",
                "a weekly Sunday 4 AM signature update via launchd (%s)" % plist,
                text, do_plist)
    cron = "0 4 * * 0 %s  # signature-antivirus weekly signature update" % cmd

    def do_cron():
        cur = ""
        try:
            r = subprocess.run(["crontab", "-l"], capture_output=True,
                               text=True, timeout=10)
            cur = r.stdout if r.returncode == 0 else ""
        except Exception:
            pass
        lines = [l for l in cur.splitlines()
                 if "signature-antivirus weekly signature update" not in l]
        lines.append(cron)
        return subprocess.run(["crontab", "-"], input="\n".join(lines) + "\n",
                              capture_output=True, text=True, timeout=10)
    return ("linux-cron",
            "a weekly Sunday 4 AM signature update via your crontab",
            cron, do_cron)


def self_test():
    tmp = tempfile.mkdtemp(prefix="updtest_")
    ok = True
    try:
        # fake "canonical" server: a local file with a newer version
        newer = {"meta": {"version": "2099.1.1.1", "updated": "2099-01-01",
                          "source": "test"},
                 "sha256": {"abc": "TEST-MARKER"}, "filenames": ["evil.exe"]}
        srv = os.path.join(tmp, "signatures.json")
        with open(srv, "w", encoding="utf-8") as f:
            json.dump(newer, f)
        os.environ["SHIELD_SIG_URL"] = "file://" + srv
        status, msg, remote = check()
        assert status == "update", "expected update, got %s (%s)" % (status, msg)
        print("check detects newer: OK (%s)" % msg)
        # validation rejects garbage
        assert validate_db({"nope": 1}) is not None
        assert validate_db(newer) is None
        print("validate_db: OK")
        # apply with --yes journals to a sandbox home
        home = os.path.join(tmp, "home")
        ok2, msg2 = apply_update(remote, journal_home=home, assume_yes=True)
        assert ok2, msg2
        assert local_version() == "2099.1.1.1", local_version()
        print("apply: OK (%s)" % msg2)
        # journal entry exists and rewind restores the old DB
        import shield_journal as journal
        es = journal.entries(home)
        assert any(e["action"] == "sigdb_update" for e in es), "no journal entry"
        rep = journal.rewind(home, 1, actor="test")
        assert rep["undone"], "rewind failed: %s" % rep
        assert local_version() != "2099.1.1.1", "DB not restored"
        print("journal + rewind: OK")
    except AssertionError as e:
        print("UPDATE SELF-TEST FAIL: %s" % e)
        ok = False
    finally:
        # restore the real DB no matter what
        bak = SIG_DB + ".bak"
        if os.path.exists(bak):
            try:
                os.replace(bak, SIG_DB)
            except OSError:
                pass
        shutil.rmtree(tmp, ignore_errors=True)
        os.environ.pop("SHIELD_SIG_URL", None)
    print("UPDATE SELF-TEST " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    if not argv or argv[0] == "version":
        db = local_db()
        m = db.get("meta", {})
        print("Signature database v%s, updated %s" % (m.get("version", "?"),
                                                      m.get("updated", "?")))
        print("Signatures: %d fingerprints, %d bad filenames"
              % (len(db.get("sha256", {})), len(db.get("filenames", []))))
        return 0
    if argv[0] == "check":
        _s, msg, _r = check()
        print(msg)
        return 0
    if argv[0] == "apply":
        home = os.path.join(os.path.expanduser("~"), ".signature-antivirus")
        ok, msg = apply_update(journal_home=home if os.path.isdir(home) else os.getcwd(),
                               assume_yes="--yes" in argv)
        print(msg)
        return 0 if ok else 1
    print(__doc__.strip().splitlines()[0])
    print("usage: shield_update.py [check|apply [--yes]|version|--self-test]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
