#!/usr/bin/env python3
"""
Shield action journal — the fail-safe rewind.

Every action the AI (or installer) takes on the user's system is appended
here with its EXACT inverse. `rewind` undoes the last action, the last N,
or everything — newest first. Nothing the AI does is ever irreversible.

Journal: <home>/action_journal.jsonl  (JSON lines, append-only; undone
entries are marked, never deleted, so there's always an audit trail.)
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)


def _path(home):
    return os.path.join(home, "action_journal.jsonl")


def record(home, actor, action, detail, inverse):
    """Append one journal entry. inverse = {"op": ..., ...} describing the undo."""
    os.makedirs(home, exist_ok=True)
    entry = {"ts": time.time(),
             "when": time.strftime("%Y-%m-%d %H:%M:%S"),
             "actor": actor, "action": action,
             "detail": detail, "inverse": inverse,
             "undone": False}
    with open(_path(home), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def entries(home, include_undone=False):
    p = _path(home)
    if not os.path.exists(p):
        return []
    out = []
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("undone") and not include_undone:
            continue
        out.append(e)
    return out


def _describe(e):
    a = e["action"]
    d = e.get("detail") or {}
    if a == "quarantine":
        return "quarantined %s" % d.get("path", "a file")
    if a == "sigdb_update":
        return "updated signature database v%s → v%s" % (d.get("from", "?"), d.get("to", "?"))
    if a == "honeypot_plant":
        return "planted %d ransomware tripwires" % len(d.get("files", []))
    if a == "scheduler_install":
        return "installed scheduled scans (%s)" % d.get("kind", "?")
    if a == "firewall_generate":
        return "generated firewall rules file"
    if a == "monitor_start":
        return "started the background monitor"
    if a == "protection_off":
        return "turned protection OFF"
    if a == "protection_on":
        return "turned protection back ON"
    return a


def _undo_entry(home, e):
    """Execute the inverse of one entry. Returns (ok, message)."""
    inv = e.get("inverse") or {}
    op = inv.get("op")
    old = os.getcwd()
    try:
        if op == "restore_quarantine":
            os.chdir(home)
            import shield_basic as basic
            dest = basic.restore(inv["qid"])
            return (True, "restored %s" % dest) if dest else (False, "quarantine record not found")
        if op == "restore_sigdb":
            import shutil
            backup, target = inv.get("backup"), inv.get("target")
            if backup and target and os.path.exists(backup):
                shutil.copy2(backup, target)
                return True, "signature database rolled back to the previous version"
            return False, "backup copy not found"
        if op == "remove_files":
            gone = 0
            for p in inv.get("paths", []):
                try:
                    os.remove(p)
                    gone += 1
                except OSError:
                    pass
            return True, "removed %d file(s)" % gone
        if op == "remove_scheduler":
            sys.path.insert(0, HERE)
            import install as inst
            inst.remove_scheduler_entries()
            return True, "scheduler entries removed"
        if op == "stop_monitor":
            sys.path.insert(0, HERE)
            import install as inst
            inst.stop_monitor(home)
            return True, "monitor stopped"
        if op == "restore_config":
            with open(inv["path"], "w", encoding="utf-8") as f:
                f.write(inv["previous"])
            return True, "settings restored"
        if op == "protection_was_on":
            sys.path.insert(0, HERE)
            import install as inst
            inst.protection_on(home, quiet=True)
            return True, "protection turned back on"
        return False, "unknown inverse op: %s" % op
    except Exception as ex:
        return False, "undo failed: %s" % ex
    finally:
        try:
            os.chdir(old)
        except Exception:
            pass


def _mark_undone(home, target):
    p = _path(home)
    if not os.path.exists(p):
        return
    lines = open(p, encoding="utf-8").read().splitlines()
    out = []
    for line in lines:
        try:
            e = json.loads(line)
        except ValueError:
            out.append(line)
            continue
        if (not e.get("undone") and e.get("ts") == target.get("ts")
                and e.get("action") == target.get("action")):
            e["undone"] = True
            line = json.dumps(e)
        out.append(line)
    with open(p, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + ("\n" if out else ""))


def rewind(home, n=None, actor="user"):
    """
    Undo the last n actions (n=None = all), newest first.
    Returns {"undone": [...], "failed": [...]} with plain-language messages.
    """
    todo = entries(home)
    if n is not None:
        todo = todo[-n:]
    todo = list(reversed(todo))
    report = {"undone": [], "failed": []}
    for e in todo:
        ok, msg = _undo_entry(home, e)
        if ok:
            _mark_undone(home, e)
            report["undone"].append("%s — undone (%s)" % (_describe(e), msg))
        else:
            report["failed"].append("%s — FAILED: %s" % (_describe(e), msg))
    return report
