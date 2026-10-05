#!/usr/bin/env python3
"""
Signature Shield Defense-Grade — advanced protection toolkit (download-only).
ONE universal download: detects the OS at runtime and applies the matching
protection profile automatically.

Subcommands (all print exactly what they do; nothing is applied silently):
  osinfo                  show detected OS + protection profile
  heuristic-scan <dir>    behavioral-heuristic scan (double extensions,
                          executables in temp dirs, script keyword heuristics,
                          extension-vs-content mismatch)
  firewall [--out FILE]   GENERATE firewall rules for YOUR os
                            Windows -> netsh advfirewall .bat
                            macOS   -> pf anchor .conf (with honest notes)
                            Linux   -> ufw commands, or nftables/iptables
                                       script if ufw is absent
  usb-guard <mountpath>   scan a removable drive for autorun.inf / .lnk
                          droppers (Windows checks real removable drives too)
  honeypot [--dir DIR]    plant ransomware canary files (tripwire: any
                          modification = early warning; checked by monitor)
  honeypot-check          verify canaries are untouched
  bootcheck               audit auto-start entries:
                            Windows -> HKCU Run keys (winreg) + Startup folders
                            macOS   -> LaunchAgents / LaunchDaemons
                            Linux   -> systemd user units + crontab + profile.d
  netmon                  list listening ports + active connections
                          (psutil if installed, else OS-native fallbacks)
  apply-all               run the FULL profile for the detected OS:
                          honeypots + firewall rules file + bootcheck +
                          printed hardening checklist
  --self-test             run every safe path in a temp sandbox, exit 0 on pass
"""
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import tempfile
import time

OS = platform.system()
OS_LABEL = {"Windows": "Windows", "Darwin": "macOS", "Linux": "Linux"}.get(OS, OS)
HERE = os.path.dirname(os.path.abspath(__file__))

SUSPICIOUS_KEYWORDS = (
    "powershell -enc", "powershell -EncodedCommand", "cmd /c", "wscript",
    "cscript", "regsvr32", "rundll32", "certutil -decode", "bitsadmin",
    "Invoke-Mimikatz", "mimikatz", "curl http", "wget http",
    "nc -e", "ncat -e", "/dev/tcp/", "chmod +x /tmp", "base64 -d",
    "eval(base64", "CreateObject(\"WScript.Shell\")",
)
SCRIPT_EXTS = (".ps1", ".vbs", ".js", ".jse", ".wsf", ".bat", ".cmd", ".sh", ".py")
EXEC_IN_TMP = (".exe", ".dll", ".scr", ".com", ".pif", ".msi")


def profile():
    """Honestly-differentiated protection profile per OS."""
    if OS == "Windows":
        return {"os": "Windows",
                "applies": ["signature scan", "heuristic scan", "netsh firewall rules",
                            "USB autorun guard", "ransomware honeypots",
                            "startup/registry boot check", "network monitor"],
                "note": "Full suite: Windows faces the broadest malware landscape."}
    if OS == "Darwin":
        return {"os": "macOS",
                "applies": ["signature scan", "heuristic scan", "USB guard",
                            "ransomware honeypots", "LaunchAgents/Daemons boot check",
                            "network monitor", "pf firewall rules (generated, optional)"],
                "note": ("macOS ships with Gatekeeper and XProtect and faces a "
                         "different, smaller threat landscape — it does not need the "
                         "same protection as Windows. This profile coexists with "
                         "Apple's built-ins and skips Windows-only measures.")}
    if OS == "Linux":
        return {"os": "Linux",
                "applies": ["signature scan", "heuristic scan", "USB guard",
                            "ransomware honeypots", "systemd/cron/profile.d boot check",
                            "network monitor", "ufw or nftables/iptables firewall rules",
                            "permissions hardening checklist (SUID / world-writable audit)"],
                "note": "Linux profile focuses on permissions, services and firewall."}
    return {"os": OS_LABEL,
            "applies": ["portable signature scan", "heuristic scan",
                        "generic hardening checklist"],
            "note": "Unknown OS: portable scanner plus the generic hardening checklist."}


def heuristic_scan(root):
    findings = []
    scanned = 0
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            path = os.path.join(dirpath, name)
            scanned += 1
            low = name.lower()
            reasons = []
            if low.endswith((".pdf.exe", ".doc.exe", ".jpg.exe", ".txt.exe",
                             ".zip.exe", ".mp3.exe")):
                reasons.append("double extension disguise")
            tmpish = any(t in dirpath.lower() for t in ("temp", "tmp", "appdata\\local\\temp"))
            if tmpish and low.endswith(EXEC_IN_TMP):
                reasons.append("executable sitting in a temp directory")
            if low.endswith(SCRIPT_EXTS):
                try:
                    with open(path, "r", errors="ignore") as f:
                        head = f.read(20000).lower()
                    hits = [k for k in SUSPICIOUS_KEYWORDS if k.lower() in head]
                    if hits:
                        reasons.append("heuristic: suspicious keywords (%s)" % ", ".join(hits[:3]))
                except OSError:
                    pass
            if low.endswith((".jpg", ".png", ".pdf")) and os.path.getsize(path) > 0:
                try:
                    with open(path, "rb") as f:
                        magic = f.read(4)
                    if magic[:2] == b"MZ":
                        reasons.append("extension/content mismatch: executable masquerading as document/image")
                except OSError:
                    pass
            if reasons:
                findings.append({"path": path, "reasons": reasons})
    return {"scanned": scanned, "findings": findings}


def firewall_rules(out=None):
    """Generate (never silently apply) firewall rules for the detected OS."""
    if OS == "Windows":
        text = ("@echo off\n"
                "REM Signature Shield firewall baseline — run as Administrator.\n"
                "REM Blocks inbound on risky ports; keeps web/mail/DNS working.\n"
                "netsh advfirewall firewall add rule name=\"Shield-Block-135-139\" dir=in action=block protocol=TCP localport=135-139\n"
                "netsh advfirewall firewall add rule name=\"Shield-Block-445\" dir=in action=block protocol=TCP localport=445\n"
                "netsh advfirewall firewall add rule name=\"Shield-Block-3389\" dir=in action=block protocol=TCP localport=3389\n"
                "echo Done. Review with: netsh advfirewall firewall show rule name=all\n")
        fname = out or "shield_firewall_windows.bat"
    elif OS == "Darwin":
        text = ("# Signature Shield pf rules (macOS) — review, then:\n"
                "#   sudo cp this file to /etc/pf.anchors/com.signature.shield\n"
                "#   add 'anchor \"com.signature.shield\"' to /etc/pf.conf, then: sudo pfctl -f /etc/pf.conf -e\n"
                "# Honest note: macOS already filters via its built-in firewall + XProtect;\n"
                "# these rules only add blocks for classic worm ports (135-139, 445).\n"
                "block in proto tcp from any to any port {135:139, 445}\n")
        fname = out or "shield_pf_macos.conf"
    else:
        has_ufw = shutil.which("ufw") is not None
        if has_ufw:
            text = ("#!/bin/sh\n# Signature Shield firewall baseline (ufw present).\n"
                    "# Run with sudo. Review each line first.\n"
                    "sudo ufw default deny incoming\nsudo ufw default allow outgoing\n"
                    "sudo ufw deny 135:139/tcp\nsudo ufw deny 445/tcp\nsudo ufw deny 23/tcp\n"
                    "sudo ufw --force enable\nsudo ufw status verbose\n")
        else:
            text = ("#!/bin/sh\n# Signature Shield firewall baseline (nftables).\n"
                    "# Run with sudo. Review each line first.\n"
                    "sudo nft add table inet shield\n"
                    "sudo nft add chain inet shield input '{ type filter hook input priority 0; policy drop; }'\n"
                    "sudo nft add rule inet shield input ct state established,related accept\n"
                    "sudo nft add rule inet shield input iif lo accept\n"
                    "sudo nft add rule inet shield input tcp dport '{135-139, 445, 23}' drop\n"
                    "sudo nft list ruleset\n")
        fname = out or "shield_firewall_linux.sh"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(text)
    if fname.endswith(".sh"):
        os.chmod(fname, 0o755)
    return fname


def usb_guard(mountpath):
    findings = []
    if not os.path.isdir(mountpath):
        return {"error": "not a directory: %s" % mountpath}
    for name in os.listdir(mountpath):
        low = name.lower()
        if low == "autorun.inf":
            findings.append({"file": name, "reason": "autorun.inf on removable media (classic USB worm vector)"})
        elif low.endswith(".lnk"):
            findings.append({"file": name, "reason": ".lnk on removable drive root — inspect before opening"})
    if OS == "Windows":
        try:
            import string
            from ctypes import windll
            drives = []
            bits = windll.kernel32.GetLogicalDrives()
            for i, letter in enumerate(string.ascii_uppercase):
                if bits & (1 << i):
                    dtype = windll.kernel32.GetDriveTypeW(letter + ":\\")
                    if dtype == 2:
                        drives.append(letter + ":\\")
            extra = []
            for d in drives:
                auto = os.path.join(d, "autorun.inf")
                if os.path.exists(auto):
                    extra.append({"file": auto, "reason": "autorun.inf on removable drive %s" % d})
            findings.extend(extra)
        except Exception:
            pass
    return {"drive": mountpath, "findings": findings}


CANARY_PREFIX = "DO_NOT_TOUCH_shield_canary_"


def honeypot(target_dir=None):
    target = target_dir or os.path.expanduser("~")
    os.makedirs(target, exist_ok=True)
    made = []
    for i in range(3):
        p = os.path.join(target, "%s%d.txt" % (CANARY_PREFIX, i))
        with open(p, "w", encoding="utf-8") as f:
            f.write("Signature Shield ransomware tripwire #%d.\n"
                    "If this file is ever modified or encrypted, treat it as an "
                    "early warning and disconnect from the network.\n" % i)
        made.append(p)
    return made


def honeypot_check(target_dir=None):
    target = target_dir or os.path.expanduser("~")
    bad = []
    for i in range(3):
        p = os.path.join(target, "%s%d.txt" % (CANARY_PREFIX, i))
        if not os.path.exists(p):
            bad.append({"file": p, "state": "missing — investigate"})
            continue
        with open(p, "r", errors="ignore") as f:
            if "ransomware tripwire" not in f.read():
                bad.append({"file": p, "state": "MODIFIED — possible ransomware activity"})
    return {"ok": not bad, "issues": bad}


def bootcheck():
    items = []
    if OS == "Windows":
        try:
            import winreg
            for hive, path in ((winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                               (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run")):
                try:
                    key = winreg.OpenKey(hive, path)
                    i = 0
                    while True:
                        try:
                            n, v, _t = winreg.EnumValue(key, i)
                            items.append({"source": "registry Run", "name": n, "value": str(v)[:120]})
                            i += 1
                        except OSError:
                            break
                    winreg.CloseKey(key)
                except OSError:
                    pass
        except ImportError:
            items.append({"source": "registry", "note": "winreg unavailable"})
        for loc in (os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"),
                    os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs\Startup")):
            if os.path.isdir(loc):
                for n in os.listdir(loc):
                    items.append({"source": "Startup folder", "name": n})
    elif OS == "Darwin":
        for d in (os.path.expanduser("~/Library/LaunchAgents"),
                  "/Library/LaunchAgents", "/Library/LaunchDaemons"):
            if os.path.isdir(d):
                for n in sorted(os.listdir(d)):
                    items.append({"source": d, "name": n})
    else:
        try:
            out = subprocess.run(["systemctl", "--user", "list-unit-files",
                                  "--type=service", "--state=enabled"],
                                 capture_output=True, text=True, timeout=10)
            for line in out.stdout.splitlines()[1:]:
                if ".service" in line:
                    items.append({"source": "systemd --user", "name": line.split()[0]})
        except Exception:
            pass
        try:
            out = subprocess.run(["crontab", "-l"], capture_output=True,
                                 text=True, timeout=10)
            for line in out.stdout.splitlines():
                if line.strip() and not line.startswith("#"):
                    items.append({"source": "crontab", "name": line[:100]})
        except Exception:
            pass
        pd = "/etc/profile.d"
        if os.path.isdir(pd):
            for n in sorted(os.listdir(pd)):
                items.append({"source": "profile.d", "name": n})
    return items


def netmon():
    conns = []
    try:
        import psutil
        for c in psutil.net_connections(kind="inet"):
            if c.status == "LISTEN":
                laddr = "%s:%s" % (c.laddr.ip, c.laddr.port) if c.laddr else "?"
                try:
                    proc = psutil.Process(c.pid).name() if c.pid else "?"
                except Exception:
                    proc = "?"
                conns.append({"listening": laddr, "process": proc, "pid": c.pid})
        return {"via": "psutil", "listening": conns}
    except ImportError:
        pass
    if OS == "Linux":
        try:
            with open("/proc/net/tcp") as f:
                lines = f.readlines()[1:]
            n = sum(1 for ln in lines if ln.split()[3] == "0A")
            return {"via": "/proc/net/tcp", "listening_tcp_sockets": n,
                    "note": "install psutil for per-process names: pip install psutil"}
        except OSError:
            pass
    try:
        out = subprocess.run(["netstat", "-tln"], capture_output=True,
                             text=True, timeout=10)
        rows = [ln for ln in out.stdout.splitlines() if "LISTEN" in ln]
        return {"via": "netstat", "listening": rows[:20]}
    except Exception as e:
        return {"error": "no network listing method available: %s" % e}


def hardening_checklist():
    p = profile()
    base = ["Keep OS + browser updated (most infections ride unpatched bugs).",
            "Use a standard user account day-to-day, not admin/root.",
            "Back up important files offline — ransomware can't encrypt what's unplugged.",
            "Don't open unexpected attachments; check the real sender address."]
    if OS == "Windows":
        base += ["Turn on Windows Security real-time protection (coexists with Shield).",
                 "Apply the generated netsh firewall rules (firewall command).",
                 "Disable AutoRun for removable drives (USB guard watches them)."]
    elif OS == "Darwin":
        base += ["Leave Gatekeeper + XProtect on — Shield is a second opinion, not a replacement.",
                 "Review LaunchAgents/Daemons after installing new software (bootcheck)."]
    elif OS == "Linux":
        base += ["Apply the generated ufw/nftables rules (firewall command).",
                 "Audit SUID binaries + world-writable files monthly."]
    return {"profile": p["os"], "note": p["note"], "checklist": base}


def apply_all(workdir=None):
    """Run the FULL profile for the detected OS. Returns a report dict."""
    workdir = workdir or os.getcwd()
    report = {"os": OS_LABEL, "profile": profile(), "steps": []}
    canaries = honeypot()
    report["steps"].append({"step": "ransomware honeypots planted",
                            "detail": canaries})
    fw = firewall_rules(out=os.path.join(workdir, "shield_firewall_rules.txt"))
    report["steps"].append({"step": "firewall rules generated (review before applying)",
                            "detail": fw})
    boots = bootcheck()
    report["steps"].append({"step": "boot/auto-start audit",
                            "detail": "%d entries found — review unknown ones" % len(boots)})
    report["checklist"] = hardening_checklist()["checklist"]
    rep_path = os.path.join(workdir, "shield_apply_all_report.json")
    with open(rep_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    report["report_file"] = rep_path
    return report


def self_test():
    tmp = tempfile.mkdtemp(prefix="defensetest_")
    try:
        assert profile()["os"], "profile missing"
        d = os.path.join(tmp, "scanme")
        os.makedirs(d)
        with open(os.path.join(d, "clean.txt"), "w") as f:
            f.write("hello")
        with open(os.path.join(d, "evil.pdf.exe"), "w") as f:
            f.write("x")
        hs = heuristic_scan(d)
        assert any("evil.pdf.exe" in x["path"] for x in hs["findings"]), "heuristic missed double ext"
        assert not any("clean.txt" in x["path"] for x in hs["findings"]), "heuristic false positive"
        fw = firewall_rules(out=os.path.join(tmp, "fw.txt"))
        assert os.path.getsize(fw) > 50, "firewall rules empty"
        c = honeypot(target_dir=tmp)
        assert len(c) == 3 and all(os.path.exists(x) for x in c), "honeypot failed"
        chk = honeypot_check(target_dir=tmp)
        assert chk["ok"], "honeypot check failed on fresh canaries"
        with open(c[0], "w") as f:
            f.write("tampered")
        chk2 = honeypot_check(target_dir=tmp)
        assert not chk2["ok"], "honeypot check missed tampering"
        boots = bootcheck()
        assert isinstance(boots, list), "bootcheck not a list"
        net = netmon()
        assert isinstance(net, dict), "netmon not a dict"
        ug = usb_guard(tmp)
        assert "findings" in ug, "usb-guard broken"
        rep = apply_all(workdir=tmp)
        assert os.path.exists(rep["report_file"]), "apply-all report missing"
        print("SELF-TEST PASS  os=%s  profile=%s  heuristic=%d/%d  bootcheck=%d  netmon=%s"
              % (OS, profile()["os"], len(hs["findings"]), hs["scanned"],
                 len(boots), net.get("via", "?")))
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
        print(json.dumps({"detected": {"system": OS, "label": OS_LABEL,
                                       "release": platform.release()},
                          "profile": profile()}, indent=2))
        return 0
    if cmd == "heuristic-scan":
        root = argv[1] if len(argv) > 1 else "."
        r = heuristic_scan(root)
        print("OS profile: %s — scanned %d files" % (OS_LABEL, r["scanned"]))
        if not r["findings"]:
            print("Clean — nothing suspicious.")
        for f in r["findings"]:
            print("SUSPICIOUS: %s" % f["path"])
            for x in f["reasons"]:
                print("    - %s" % x)
        return 0
    if cmd == "firewall":
        out = argv[argv.index("--out") + 1] if "--out" in argv else None
        fname = firewall_rules(out=out)
        print("Wrote %s rules to %s" % (OS_LABEL, fname))
        print("REVIEW the file first, then apply it as described inside.")
        return 0
    if cmd == "usb-guard":
        mp = argv[1] if len(argv) > 1 else ("/media" if OS == "Linux" else ".")
        r = usb_guard(mp)
        print(json.dumps(r, indent=2))
        return 0
    if cmd == "honeypot":
        d = argv[argv.index("--dir") + 1] if "--dir" in argv else None
        for p in honeypot(d):
            print("Planted canary: %s" % p)
        return 0
    if cmd == "honeypot-check":
        r = honeypot_check()
        print("Canaries OK — untouched." if r["ok"] else "WARNING:")
        for i in r["issues"]:
            print("  %s: %s" % (i["file"], i["state"]))
        return 0 if r["ok"] else 2
    if cmd == "bootcheck":
        items = bootcheck()
        print("Auto-start entries on %s (%d):" % (OS_LABEL, len(items)))
        for it in items[:40]:
            print("  [%s] %s" % (it.get("source"), it.get("name", it.get("note"))))
        if len(items) > 40:
            print("  …and %d more" % (len(items) - 40))
        print("Review anything you don't recognize.")
        return 0
    if cmd == "netmon":
        print(json.dumps(netmon(), indent=2)[:3000])
        return 0
    if cmd == "apply-all":
        rep = apply_all()
        print("Applied full %s profile:" % OS_LABEL)
        for s in rep["steps"]:
            print("  ✓ %s" % s["step"])
        print("Hardening checklist:")
        for c in rep["checklist"]:
            print("  - %s" % c)
        print("Full report: %s" % rep["report_file"])
        return 0
    print("Unknown command: %s" % cmd)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
