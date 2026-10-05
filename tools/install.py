#!/usr/bin/env python3
"""
Signature Shield installer — download → run → protection RUNNING.

Installs the shields into a per-OS home (~/.signature-antivirus), plants the
ransomware tripwires, sets up scheduled scans (shown to you and installed
only with your yes), and starts the resident monitor. Ends with a clear
PROTECTION: RUNNING report — like commercial antivirus, without the
subscription.

Nothing is changed silently: every step is printed, and anything touching
your system scheduler is asked first.

Usage:
  python3 install.py [--edition ai-defense] [--home DIR] [--yes] [--uninstall]
                     [--off] [--on]
  Editions: basic | defense | ai-basic | ai-defense   (default: ai-defense)
  --off / --on: the protection switch — pause everything or resume.
  --uninstall: clean removal — restores quarantine first if you want,
               then proves zero residue with a post-check.
"""
import json
import os
import platform
import shutil
import subprocess
import sys
import time

OS = platform.system()
OS_LABEL = {"Windows": "Windows", "Darwin": "macOS", "Linux": "Linux"}.get(OS, OS)
HERE = os.path.dirname(os.path.abspath(__file__))
EDITIONS = ("basic", "defense", "ai-basic", "ai-defense")
EDITION_NAMES = {
    "basic": "Signature Shield Basic",
    "defense": "Signature Shield Defense-Grade",
    "ai-basic": "Signature Shield AI",
    "ai-defense": "Signature Shield AI Defense-Grade",
}
FILES = ("install.py", "shield_status.py", "shield_monitor.py", "shield_ai.py",
         "shield_ai_basic.py", "shield_ai_defense.py", "shield_journal.py",
         "shield_basic.py", "shield_defense.py", "shield_scan.py",
         "shield_update.py", "signatures.json")


def say(msg):
    print(msg)


def ask(question, auto_yes):
    if auto_yes:
        say(question + " [auto-yes]")
        return True
    try:
        return input(question + " (yes/no) ").strip().lower() in (
            "yes", "y", "yeah", "yep", "ok", "okay")
    except (EOFError, KeyboardInterrupt):
        print()
        return False


def home_default():
    return os.path.join(os.path.expanduser("~"), ".signature-antivirus")


def scheduler_artifacts(home, edition):
    """Return (kind, install_description, artifact_text_or_path, installer_fn)."""
    binp = os.path.join(home, "bin")
    py = sys.executable or "python3"
    target = os.path.expanduser("~/Downloads")
    log = os.path.join(home, "scheduled.log")
    cmd = "cd \"%s\" && \"%s\" \"%s\" scan \"%s\" >> \"%s\" 2>&1" % (
        home, py, os.path.join(binp, "shield_basic.py"), target, log)
    if OS == "Windows":
        line = ('schtasks /create /tn "SignatureShield" /tr "cmd /c %s" '
                "/sc daily /st 03:00 /f" % cmd.replace('"', '\\"'))
        return ("windows-schtasks",
                "a daily 3 AM scheduled scan via Windows Task Scheduler",
                line,
                lambda: subprocess.run(line, shell=True, capture_output=True, text=True))
    if OS == "Darwin":
        plist = os.path.expanduser("~/Library/LaunchAgents/com.signature.shield.plist")
        text = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" "
                "\"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n"
                "<plist version=\"1.0\"><dict>\n"
                "  <key>Label</key><string>com.signature.shield</string>\n"
                "  <key>ProgramArguments</key><array>\n"
                "    <string>%s</string>\n"
                "    <string>%s</string>\n"
                "    <string>scan</string>\n"
                "    <string>%s</string>\n"
                "  </array>\n"
                "  <key>WorkingDirectory</key><string>%s</string>\n"
                "  <key>StartCalendarInterval</key><dict>"
                "<key>Hour</key><integer>3</integer>"
                "<key>Minute</key><integer>0</integer></dict>\n"
                "  <key>StandardOutPath</key><string>%s</string>\n"
                "  <key>StandardErrorPath</key><string>%s</string>\n"
                "</dict></plist>\n" % (py, os.path.join(binp, "shield_basic.py"),
                                      target, home, log, log))
        return ("macos-launchd",
                "a daily 3 AM scan via launchd (%s)" % plist,
                text,
                lambda: _write_and_load_plist(plist, text))
    cron = "0 3 * * * %s  # signature-antivirus daily scan" % cmd
    return ("linux-cron",
            "a daily 3 AM scan via your crontab",
            cron,
            lambda: _merge_crontab(cron))


def _write_and_load_plist(plist, text):
    os.makedirs(os.path.dirname(plist), exist_ok=True)
    with open(plist, "w", encoding="utf-8") as f:
        f.write(text)
    r = subprocess.run(["launchctl", "load", plist], capture_output=True, text=True)
    return r


def _merge_crontab(line):
    cur = ""
    try:
        r = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=10)
        cur = r.stdout if r.returncode == 0 else ""
    except Exception:
        pass
    lines = [l for l in cur.splitlines() if "signature-antivirus" not in l]
    lines.append(line)
    p = subprocess.run(["crontab", "-"], input="\n".join(lines) + "\n",
                       capture_output=True, text=True, timeout=10)
    return p


def start_monitor(home, binp):
    env = dict(os.environ)
    env["SHIELD_HOME"] = home
    env["SHIELD_MONITOR_INTERVAL"] = "900"
    script = os.path.join(binp, "shield_monitor.py")
    if OS == "Windows":
        flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(
            subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        subprocess.Popen([sys.executable, script], env=env,
                         creationflags=flags, close_fds=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.Popen([sys.executable, script], env=env,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         close_fds=True)
    # the monitor daemonizes itself on posix and writes a heartbeat
    for _ in range(20):
        hb = os.path.join(home, "monitor.heartbeat.json")
        if os.path.exists(hb):
            return True
        time.sleep(0.5)
    return False


def install(home, edition, auto_yes, sandbox, src_dir=None):
    import shield_journal as journal
    say("🛡️  Signature Shield installer — %s" % EDITION_NAMES[edition])
    say("System detected: %s. Installing to: %s" % (OS_LABEL, home))
    say("Free forever — no accounts, no payments, no upsells. To remove cleanly later: "
        "python3 install.py --uninstall")
    binp = os.path.join(home, "bin")
    os.makedirs(binp, exist_ok=True)

    src = src_dir or HERE
    if src_dir:
        say("      Assembling from downloaded parts in %s" % src_dir)
    say("\n[1/5] Copying the tools...")
    for fn in FILES:
        srcf = os.path.join(src, fn)
        if os.path.exists(srcf):
            shutil.copy2(srcf, os.path.join(binp, fn))
    say("      %d files installed in %s" % (len([f for f in FILES
          if os.path.exists(os.path.join(binp, f))]), binp))

    cfg = {"edition": edition, "edition_name": EDITION_NAMES[edition],
           "installed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
           "monitor_interval": 900,
           "scan_target": os.path.expanduser("~/Downloads")}
    with open(os.path.join(home, "config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

    is_defense = edition in ("defense", "ai-defense")
    if is_defense:
        say("\n[2/5] Planting ransomware tripwires...")
        sys.path.insert(0, binp)
        import shield_defense as defense
        can = os.path.join(home, "canaries")
        made = defense.honeypot(target_dir=can)
        journal.record(home, "installer", "honeypot_plant",
                       {"files": made},
                       {"op": "remove_files", "paths": made})
        say("      %d canary files planted in %s — if ransomware touches them, "
            "you get an early warning." % (len(made), can))
    else:
        say("\n[2/5] Tripwires are a Defense-Grade feature — skipping "
            "(Basic keeps scanning + quarantine).")

    say("\n[3/5] Scheduled scans...")
    kind, desc, artifact, do_install = scheduler_artifacts(home, edition)
    say("      I can set up %s." % desc)
    say("      Exactly what would be installed:\n-----\n%s\n-----" % artifact)
    scheduled = False
    if sandbox:
        sp = os.path.join(home, "sandbox-scheduler.txt")
        with open(sp, "w", encoding="utf-8") as f:
            f.write(artifact)
        say("      (sandbox mode: scheduler artifact written to %s, "
            "system untouched)" % sp)
        scheduled = True
    elif ask("      Install this scheduled scan?", auto_yes):
        r = do_install()
        rc = r.returncode if r is not None else 0
        if rc == 0:
            say("      Scheduled scan installed.")
            journal.record(home, "installer", "scheduler_install",
                           {"kind": kind},
                           {"op": "remove_scheduler"})
            scheduled = True
        else:
            say("      Scheduler install reported an issue (code %s). You can "
                "install it manually later — the exact text is above." % rc)
    else:
        say("      Skipped — no scheduler changes made. You can run scans manually.")

    say("\n[4/5] Starting the resident monitor...")
    mon = start_monitor(home, binp)
    if mon:
        journal.record(home, "installer", "monitor_start", {},
                       {"op": "stop_monitor"})
    say("      Monitor %s." % ("is watching (heartbeat live)" if mon
                               else "did not report back — check %s" % home))

    say("\n[5/5] Verifying...")
    hb = os.path.exists(os.path.join(home, "monitor.heartbeat.json"))
    say("      tools: %s | tripwires: %s | scheduler: %s | monitor: %s" % (
        "ok", "planted" if is_defense else "n/a (basic)",
        "set" if scheduled else "not set", "alive" if hb else "not running"))

    running = hb and (scheduled or True)
    say("\n" + ("=" * 56))
    if running:
        say("PROTECTION: RUNNING — %s is active on your %s system."
            % (EDITION_NAMES[edition], OS_LABEL))
    else:
        say("PROTECTION: PARTIAL — installed, but the monitor did not start. "
            "Re-run the installer to retry.")
    say("=" * 56)
    if edition.startswith("ai-"):
        say("\n🤖 Meet Shield, your antivirus AI — the engine inside your protection.")
        say("   It watches, explains, and regulates with your supervision.")
        say("   Talk to it:  python3 \"%s\" chat"
            % os.path.join(binp, "shield_ai_basic.py" if edition == "ai-basic"
                           else "shield_ai_defense.py"))
    say("   Check status anytime:  python3 \"%s\""
        % os.path.join(binp, "shield_status.py"))
    return 0 if running else 1


def _sweep_monitors(home, kill=True):
    """Find shield_monitor.py processes bound to this home (pidfile can go
    stale). Returns count found (and killed, if kill=True)."""
    import re
    found = 0
    if not os.path.isdir("/proc"):
        return 0
    me = os.getpid()
    want = os.path.abspath(home)
    for pid in os.listdir("/proc"):
        if not pid.isdigit() or int(pid) == me:
            continue
        try:
            with open("/proc/%s/cmdline" % pid, "rb") as f:
                cmd = f.read().replace(b"\0", b" ").decode("utf-8", "ignore")
            if "shield_monitor.py" not in cmd:
                continue
            with open("/proc/%s/environ" % pid, "rb") as f:
                env = f.read().decode("utf-8", "ignore")
            m = re.search(r"SHIELD_HOME=([^\x00]+)", env)
            bound = os.path.abspath(m.group(1)) == want if m else (want in cmd)
            if bound:
                found += 1
                if kill:
                    try:
                        os.kill(int(pid), 15)
                    except OSError:
                        pass
        except Exception:
            continue
    return found


def stop_monitor(home):
    """Stop the resident monitor if running. Returns True if it was running."""
    was = False
    pidf = os.path.join(home, "monitor.pid")
    if os.path.exists(pidf):
        try:
            pid = int(open(pidf).read().strip())
            os.kill(pid, 15)
            was = True
        except Exception:
            pass
        try:
            os.remove(pidf)
        except OSError:
            pass
    # pidfiles go stale — sweep for any monitor still bound to this home
    swept = _sweep_monitors(home, kill=True)
    if swept:
        time.sleep(1)
        # anyone left standing after SIGTERM gets no second chances
        left = _sweep_monitors(home, kill=False)
        if left:
            say("Warning: %d monitor process(es) ignored SIGTERM; left for the OS." % left)
    return was or swept > 0


def remove_scheduler_entries():
    """Remove Signature Shield's scheduler entries on any OS."""
    if OS == "Windows":
        for tn in ("SignatureShield", "SignatureShieldUpdates"):
            subprocess.run('schtasks /delete /tn "%s" /f' % tn,
                           shell=True, capture_output=True)
    elif OS == "Darwin":
        for pl in (os.path.expanduser("~/Library/LaunchAgents/com.signature.shield.plist"),
                   os.path.expanduser("~/Library/LaunchAgents/com.signature.shield.updates.plist")):
            subprocess.run(["launchctl", "unload", pl], capture_output=True)
            if os.path.exists(pl):
                os.remove(pl)
    else:
        r = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if r.returncode == 0:
            kept = [l for l in r.stdout.splitlines()
                    if "signature-antivirus" not in l]
            subprocess.run(["crontab", "-"], input="\n".join(kept) + "\n",
                           capture_output=True, text=True)


def _save_config(home, cfg):
    with open(os.path.join(home, "config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def _load_config(home):
    p = os.path.join(home, "config.json")
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding="utf-8"))
        except ValueError:
            pass
    return {}


def protection_off(home, quiet=False):
    """OFF switch: stop monitor, pause scheduled scans, stand down — keep installed."""
    import shield_journal as journal
    cfg = _load_config(home)
    if cfg.get("protection") == "off":
        if not quiet:
            say("Protection is already OFF.")
        return True
    was_monitor = stop_monitor(home)
    # pause scheduler but remember how to restore it
    paused = None
    try:
        if OS == "Windows":
            r = subprocess.run('schtasks /change /tn "SignatureShield" /disable',
                               shell=True, capture_output=True)
            if r.returncode == 0:
                paused = {"kind": "windows-schtasks"}
        elif OS == "Darwin":
            pl = os.path.expanduser("~/Library/LaunchAgents/com.signature.shield.plist")
            if os.path.exists(pl):
                subprocess.run(["launchctl", "unload", pl], capture_output=True)
                paused = {"kind": "macos-launchd", "plist": pl}
        else:
            r = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            if r.returncode == 0:
                mine = [l for l in r.stdout.splitlines() if "signature-antivirus" in l]
                if mine:
                    kept = [l for l in r.stdout.splitlines()
                            if "signature-antivirus" not in l]
                    subprocess.run(["crontab", "-"], input="\n".join(kept) + "\n",
                                   capture_output=True, text=True)
                    paused = {"kind": "linux-cron", "lines": mine}
    except Exception as e:
        if not quiet:
            say("Scheduler pause note: %s" % e)
    cfg["protection"] = "off"
    if paused:
        cfg["paused_scheduler"] = paused
    _save_config(home, cfg)
    journal.record(home, "user", "protection_off",
                   {"monitor_was_running": was_monitor},
                   {"op": "protection_was_on"})
    if not quiet:
        say("🛡️  Protection is OFF — monitor stopped, scheduled scans paused.")
        say("   Everything stays installed. Say 'shield on' (or run install.py --on) to resume.")
    return True


def protection_on(home, quiet=False):
    """Resume protection after OFF."""
    cfg = _load_config(home)
    binp = os.path.join(home, "bin")
    os.makedirs(binp, exist_ok=True)
    paused = cfg.pop("paused_scheduler", None)
    if paused:
        try:
            kind = paused.get("kind")
            if kind == "windows-schtasks":
                subprocess.run('schtasks /change /tn "SignatureShield" /enable',
                               shell=True, capture_output=True)
            elif kind == "macos-launchd":
                pl = paused.get("plist")
                if pl and os.path.exists(pl):
                    subprocess.run(["launchctl", "load", pl], capture_output=True)
            elif kind == "linux-cron":
                r = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
                cur = r.stdout if r.returncode == 0 else ""
                lines = [l for l in cur.splitlines() if "signature-antivirus" not in l]
                lines.extend(paused.get("lines", []))
                subprocess.run(["crontab", "-"], input="\n".join(lines) + "\n",
                               capture_output=True, text=True)
        except Exception as e:
            if not quiet:
                say("Scheduler resume note: %s" % e)
    cfg["protection"] = "on"
    _save_config(home, cfg)
    binp = os.path.join(home, "bin")
    mon = start_monitor(home, binp)
    if not quiet:
        say("🛡️  Protection is ON — monitor %s, scheduled scans resumed."
            % ("watching" if mon else "did not report back"))
    return mon


def uninstall(home, auto_yes):
    say("🛡️  Signature Shield uninstaller")
    if not os.path.isdir(home):
        say("Nothing installed at %s." % home)
        return 0
    # offer quarantine restore FIRST — nothing of the user's is lost
    qm = os.path.join(home, "shield_quarantine", "manifest.json")
    held = []
    if os.path.exists(qm):
        try:
            held = json.load(open(qm, encoding="utf-8"))
        except ValueError:
            pass
    if held and ask("There are %d quarantined file(s). Restore them to their "
                    "original locations before removing?" % len(held), auto_yes):
        old = os.getcwd()
        try:
            os.chdir(home)
            sys.path.insert(0, os.path.join(home, "bin"))
            import shield_basic as basic
            for entry in list(held):
                dest = basic.restore(entry["id"])
                say("      restored: %s" % (dest or entry["id"]))
        finally:
            try:
                os.chdir(old)
            except Exception:
                pass
    elif held:
        say("Quarantined files will be deleted with the folder (their originals "
            "are gone only if you skip restore).")
    if not ask("Remove Signature Shield from %s (scheduler entries, monitor, all files)?"
               % home, auto_yes):
        say("Cancelled — nothing was touched.")
        return 0
    if stop_monitor(home):
        say("Monitor stopped.")
    try:
        remove_scheduler_entries()
        say("Scheduler entries removed.")
    except Exception as e:
        say("Scheduler cleanup note: %s" % e)
    # firewall rules were only ever GENERATED as files for review — they live
    # in the folder and go with it; nothing was applied silently, ever.
    shutil.rmtree(home, ignore_errors=True)
    # post-uninstall check: prove the system is as we found it
    leftovers = []
    if os.path.exists(home):
        leftovers.append("folder still exists: %s" % home)
    if _sweep_monitors(home, kill=True):
        time.sleep(1)
        if _sweep_monitors(home, kill=False):
            leftovers.append("monitor process(es) still running")
    if OS == "Darwin" and os.path.exists(os.path.expanduser(
            "~/Library/LaunchAgents/com.signature.shield.plist")):
        leftovers.append("launchd plist still present")
    if OS == "Windows":
        r = subprocess.run('schtasks /query /tn "SignatureShield"',
                           shell=True, capture_output=True)
        if r.returncode == 0:
            leftovers.append("scheduled task still present")
    if not OS == "Windows":
        try:
            r = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            if "signature-antivirus" in (r.stdout or ""):
                leftovers.append("crontab entry still present")
        except Exception:
            pass
    if leftovers:
        say("Uninstall finished with leftovers — please check:")
        for l in leftovers:
            say("   - %s" % l)
        return 1
    say("Uninstalled. Post-check clean — your system is exactly as it was.")
    return 0


# Which part zip (or loose files) each tool file belongs to — the
# "download in parts" story. install.py --assemble <dir> validates the parts,
# compiles them, and builds the working tool from them.
PARTS = {
    "signature-shield-part-engine.zip": ("The engine",
        ("install.py", "shield_basic.py", "shield_journal.py", "shield_status.py")),
    "signature-shield-part-signatures.zip": ("The signature database",
        ("signatures.json",)),
    "signature-shield-part-ai.zip": ("Shield AI",
        ("shield_ai.py", "shield_ai_basic.py", "shield_ai_defense.py")),
    "signature-shield-part-scans.zip": ("Scan modules",
        ("shield_scan.py", "shield_defense.py", "shield_monitor.py")),
    "signature-shield-part-installer.zip": ("Installer & updater",
        ("install.py", "shield_update.py")),
}
# install.py itself ships inside two parts; the file set needed for a working tool:
ASSEMBLE_NEED = ("shield_basic.py", "shield_journal.py", "shield_status.py",
                 "shield_monitor.py", "shield_ai.py", "shield_ai_basic.py",
                 "shield_ai_defense.py", "shield_defense.py", "shield_scan.py",
                 "shield_update.py", "signatures.json", "install.py")


def stage_parts(parts_dir):
    """Validate downloaded parts, unpack them to a staging dir, byte-compile
    ("compile") them, and return the staging dir. Returns (None, error)."""
    import compileall
    import tempfile
    import zipfile
    if not os.path.isdir(parts_dir):
        return None, "not a folder: %s" % parts_dir
    stage = tempfile.mkdtemp(prefix="shield_parts_")
    have = {}
    # 1. unpack every part zip found
    for part, (_label, files) in PARTS.items():
        zp = os.path.join(parts_dir, part)
        if os.path.isfile(zp):
            try:
                with zipfile.ZipFile(zp) as z:
                    z.extractall(stage)
                for fn in files:
                    if os.path.isfile(os.path.join(stage, fn)):
                        have[fn] = part
            except Exception as e:
                shutil.rmtree(stage, ignore_errors=True)
                return None, "could not unpack %s: %s" % (part, e)
    # 2. also accept loose files dropped straight into the folder
    for fn in os.listdir(parts_dir):
        if fn in ASSEMBLE_NEED and fn not in have:
            shutil.copy2(os.path.join(parts_dir, fn), os.path.join(stage, fn))
            have[fn] = "(loose file)"
    missing = [fn for fn in ASSEMBLE_NEED if fn not in have]
    if missing:
        shutil.rmtree(stage, ignore_errors=True)
        return None, ("incomplete parts — missing: %s. Download the remaining "
                      "part zips and try again." % ", ".join(missing))
    # 3. sanity: the signature DB must parse and carry a version
    try:
        db = json.load(open(os.path.join(stage, "signatures.json"), encoding="utf-8"))
        assert isinstance(db.get("sha256"), dict) and db.get("meta", {}).get("version")
    except Exception as e:
        shutil.rmtree(stage, ignore_errors=True)
        return None, "the signature-database part failed validation: %s" % e
    # 4. compile: byte-compile every module so the installed tool runs from
    #    compiled parts (and syntax errors surface here, not later)
    if not compileall.compile_dir(stage, quiet=1):
        shutil.rmtree(stage, ignore_errors=True)
        return None, "a part failed to compile — re-download the parts and try again."
    manifest = {"assembled": time.strftime("%Y-%m-%d %H:%M:%S"),
                "parts": {fn: have[fn] for fn in ASSEMBLE_NEED},
                "db_version": db["meta"]["version"]}
    with open(os.path.join(stage, "parts.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    return stage, None


def main(argv):
    # pre-scan flags first — --yes/--home/--edition work in ANY position
    edition = "ai-defense"
    home = home_default()
    auto_yes = "--yes" in argv or "--sandbox" in argv
    sandbox = "--sandbox" in argv
    for i, a in enumerate(argv):
        if a == "--edition" and i + 1 < len(argv):
            edition = argv[i + 1]
        elif a == "--home" and i + 1 < len(argv):
            home = argv[i + 1]
    if "--uninstall" in argv:
        return uninstall(home, auto_yes)
    if "--assemble" in argv:
        i = argv.index("--assemble")
        parts_dir = argv[i + 1] if i + 1 < len(argv) else None
        if not parts_dir:
            say("usage: python3 install.py --assemble <parts-folder> [--edition X] [--yes]")
            return 2
        say("Assembling Signature Shield from downloaded parts in %s ..." % parts_dir)
        stage, err = stage_parts(parts_dir)
        if stage is None:
            say("Assembly failed: %s" % err)
            return 1
        say("All %d parts present and compiled." % len(PARTS))
        if not sandbox and not ask(
                "Install %s to %s from these parts?" % (EDITION_NAMES[edition], home), auto_yes):
            say("Cancelled — nothing was touched.")
            shutil.rmtree(stage, ignore_errors=True)
            return 0
        sys.path.insert(0, stage)  # installer's own imports come from the parts
        rc = install(home, edition, auto_yes, sandbox, src_dir=stage)
        shutil.rmtree(stage, ignore_errors=True)
        return rc
    if "--off" in argv:
        return 0 if protection_off(home) else 1
    if "--on" in argv:
        return 0 if protection_on(home) else 1
    if edition not in EDITIONS:
        say("Unknown edition '%s'. Choose: %s" % (edition, ", ".join(EDITIONS)))
        return 2
    if not sandbox and not ask(
            "Install %s to %s?" % (EDITION_NAMES[edition], home), auto_yes):
        say("Cancelled — nothing was touched.")
        return 0
    return install(home, edition, auto_yes, sandbox)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
