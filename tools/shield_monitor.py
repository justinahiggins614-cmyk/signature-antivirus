#!/usr/bin/env python3
"""
Shield resident monitor — the AI's eyes while you're away.

Read-only loop: checks the ransomware tripwires, writes a heartbeat so
shield_status.py can tell it's alive, and appends anything alarming to
alerts.log for the AI to report next time you talk. It NEVER quarantines,
deletes, or changes anything on its own.

Started by install.py; one instance guarded by a PID file.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

HOME = os.environ.get("SHIELD_HOME") or os.path.join(os.path.expanduser("~"),
                                                     ".signature-antivirus")
INTERVAL = int(os.environ.get("SHIELD_MONITOR_INTERVAL", "900"))
PIDFILE = os.path.join(HOME, "monitor.pid")
HEARTBEAT = os.path.join(HOME, "monitor.heartbeat.json")
ALERTS = os.path.join(HOME, "alerts.log")


def alert(msg):
    line = "%s  %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    try:
        with open(ALERTS, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def beat():
    try:
        with open(HEARTBEAT, "w", encoding="utf-8") as f:
            json.dump({"ts": time.time(), "pid": os.getpid()}, f)
    except OSError:
        pass


def check_once():
    try:
        import shield_defense as defense
        can = os.path.join(HOME, "canaries")
        if os.path.isdir(can):
            chk = defense.honeypot_check(target_dir=can)
            if not chk["ok"]:
                for i in chk["issues"]:
                    alert("TRIPWIRE %s: %s — possible ransomware activity. "
                          "Disconnect from the network." % (i["file"], i["state"]))
    except Exception as e:
        alert("monitor check error: %s" % e)


def already_running():
    if os.path.exists(PIDFILE):
        try:
            pid = int(open(PIDFILE).read().strip())
            os.kill(pid, 0)
            return True
        except Exception:
            pass
    # pidfile can go stale — check for a live monitor bound to this HOME
    if os.path.isdir("/proc"):
        me = os.getpid()
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
                import re
                m = re.search(r"SHIELD_HOME=([^\x00]+)", env)
                if (m and os.path.abspath(m.group(1)) == os.path.abspath(HOME)) \
                        or os.path.abspath(HOME) in cmd:
                    return True
            except Exception:
                continue
    return False


def main():
    os.makedirs(HOME, exist_ok=True)
    if already_running():
        print("Monitor already running.")
        return 0
    # daemonize: double-fork so it survives the terminal
    if os.name == "posix" and "--no-daemon" not in sys.argv:
        if os.fork() > 0:
            print("Monitor started in background.")
            return 0
        os.setsid()
        if os.fork() > 0:
            os._exit(0)
    try:
        with open(PIDFILE, "w") as f:
            f.write(str(os.getpid()))
        beat()
        check_once()
        while True:
            time.sleep(INTERVAL)
            beat()
            check_once()
    except KeyboardInterrupt:
        pass
    finally:
        try:
            os.remove(PIDFILE)
        except OSError:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
