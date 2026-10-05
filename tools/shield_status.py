#!/usr/bin/env python3
"""
shield_status.py — is your protection actually running? Plain-language answer.

Checks: installation, edition, scheduled scans, ransomware tripwires,
resident monitor heartbeat, quarantine contents, last scan.
Ends with PROTECTION: RUNNING / PARTIAL / NOT INSTALLED.

Usage: python3 shield_status.py [--home DIR]
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import platform
OS = platform.system()


def scheduler_present():
    try:
        if OS == "Windows":
            r = subprocess.run(["schtasks", "/query", "/tn", "SignatureShield"],
                               capture_output=True, timeout=10)
            return r.returncode == 0
        if OS == "Darwin":
            return os.path.exists(os.path.expanduser(
                "~/Library/LaunchAgents/com.signature.shield.plist"))
        out = subprocess.run(["crontab", "-l"], capture_output=True,
                             text=True, timeout=10)
        return "signature-antivirus" in (out.stdout or "")
    except Exception:
        return False


def main(argv):
    home = os.path.join(os.path.expanduser("~"), ".signature-antivirus")
    for i, a in enumerate(argv):
        if a == "--home" and i + 1 < len(argv):
            home = argv[i + 1]
    print("🛡️  Signature Shield status")
    cfg_path = os.path.join(home, "config.json")
    if not os.path.exists(cfg_path):
        print("PROTECTION: NOT INSTALLED — no installation found at %s." % home)
        print("Run: python3 install.py")
        return 1
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    print("Edition: %s" % cfg.get("edition_name", cfg.get("edition", "?")))
    print("Installed: %s" % cfg.get("installed_at", "?"))

    if cfg.get("protection") == "off":
        print()
        print("PROTECTION: OFF — paused by you. Everything stays installed; "
              "nothing is watching right now.")
        print("Resume with: python3 install.py --on  (or tell Shield \"turn on\")")
        return 3

    sched = scheduler_present()
    sandbox_sched = os.path.join(home, "sandbox-scheduler.txt")
    if not sched and os.path.exists(sandbox_sched):
        print("Scheduled scans: SET (sandbox record — real system scheduler untouched)")
        sched = True
    else:
        print("Scheduled scans: %s" % ("SET — I check automatically every day"
                                       if sched else "NOT SET"))

    is_defense = cfg.get("edition") in ("defense", "ai-defense")
    tw_ok = None
    if is_defense:
        can = os.path.join(home, "canaries")
        try:
            sys.path.insert(0, os.path.join(home, "bin"))
            import shield_defense as defense
            chk = defense.honeypot_check(target_dir=can)
            tw_ok = chk["ok"]
            print("Ransomware tripwires: %s" % (
                "PLANTED, untouched" if tw_ok else
                "ATTENTION — " + "; ".join(i["state"] for i in chk["issues"])))
        except Exception as e:
            print("Ransomware tripwires: check failed (%s)" % e)

    hb = os.path.join(home, "monitor.heartbeat.json")
    mon = "not running"
    if os.path.exists(hb):
        try:
            d = json.load(open(hb, encoding="utf-8"))
            age = time.time() - d.get("ts", 0)
            interval = cfg.get("monitor_interval", 900)
            mon = ("RUNNING — checked in %d min ago" % int(age // 60)
                   if age < interval * 2 + 60 else
                   "STALE — last check-in %d min ago" % int(age // 60))
        except Exception:
            mon = "heartbeat unreadable"
    print("Background monitor: %s" % mon)

    qm = os.path.join(home, "shield_quarantine", "manifest.json")
    nq = 0
    if os.path.exists(qm):
        try:
            nq = len(json.load(open(qm, encoding="utf-8")))
        except Exception:
            pass
    print("Quarantine: %d file(s) held safely" % nq)

    running = sched and mon.startswith("RUNNING") and (tw_ok is not False)
    print()
    if running:
        print("PROTECTION: RUNNING — everything is in place and watching.")
        return 0
    print("PROTECTION: PARTIAL — installed, but something needs attention "
          "(see above). Re-run install.py to fix, or ask Shield.")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
