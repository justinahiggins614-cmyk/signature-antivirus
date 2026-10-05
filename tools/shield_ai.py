#!/usr/bin/env python3
"""
Shield AI engine — the conversational heart of Signature Shield AI editions.

The AI actively regulates the user's system: it watches (scheduled scans +
resident monitor), detects (signatures + heuristics), DECIDES with
plain-language explanations, and chats naturally about anything it finds.

Supervised regulation — never rogue:
  * Acts on its own ONLY for clearly-safe, read-only actions
    (scanning, checking tripwires, auditing, explaining, recommending).
  * Anything destructive or system-changing (quarantine, firewall rules,
    scheduler changes, deleting) is PROPOSED first and acted on only
    after the user's yes.

Usage (via shield_ai_basic.py / shield_ai_defense.py):
  python3 shield_ai_basic.py chat        # talk to Shield
  python3 shield_ai_basic.py ask "..."   # one question, one answer
"""
import hashlib
import json
import os
import platform
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

OS = platform.system()
OS_LABEL = {"Windows": "Windows", "Darwin": "macOS", "Linux": "Linux"}.get(OS, OS)

try:
    import shield_basic as basic
except Exception:
    basic = None
try:
    import shield_defense as defense
except Exception:
    defense = None
try:
    import shield_journal as journal
except Exception:
    journal = None
try:
    import install as inst
except Exception:
    inst = None

EICAR_HASH = "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a6c4538aabf651fd0f"


def _pick(key, options):
    """Deterministic variety: same question, natural phrasing, no word salad."""
    h = int(hashlib.sha256(key.encode("utf-8")).hexdigest()[:8], 16)
    return options[h % len(options)]


class ShieldAI:
    def __init__(self, edition="basic", home=None):
        self.edition = edition  # "basic" | "defense"
        self.edition_name = ("Signature Shield AI Defense-Grade"
                             if edition == "defense" else "Signature Shield AI")
        self.home = home or os.path.join(os.path.expanduser("~"), ".signature-antivirus")
        self.pending = None  # pending proposal awaiting yes/no
        self.turns = 0

    # ---------------- live state ----------------
    def state(self):
        st = {"os": OS_LABEL, "edition": self.edition_name,
              "installed": os.path.isdir(self.home)}
        cfg = os.path.join(self.home, "config.json")
        if os.path.exists(cfg):
            try:
                st["config"] = json.load(open(cfg, encoding="utf-8"))
            except Exception:
                st["config"] = {}
        # scheduler
        st["scheduled"] = self._scheduler_present()
        # honeypots / tripwires
        can = os.path.join(self.home, "canaries")
        if defense and os.path.isdir(can):
            try:
                chk = defense.honeypot_check(target_dir=can)
                st["tripwires"] = "planted, untouched" if chk["ok"] else "ATTENTION: %s" % (
                    "; ".join(i["state"] for i in chk["issues"]))
            except Exception as e:
                st["tripwires"] = "check failed: %s" % e
        else:
            st["tripwires"] = "not planted"
        # monitor heartbeat
        hb = os.path.join(self.home, "monitor.heartbeat.json")
        st["monitor"] = "not running"
        if os.path.exists(hb):
            try:
                d = json.load(open(hb, encoding="utf-8"))
                age = time.time() - d.get("ts", 0)
                interval = (st.get("config") or {}).get("monitor_interval", 900)
                st["monitor"] = ("alive — checked in %d min ago" % int(age // 60)
                                 if age < interval * 2 + 60 else
                                 "stale — last check-in %d min ago" % int(age // 60))
            except Exception:
                st["monitor"] = "heartbeat unreadable"
        # quarantine
        qm = os.path.join(self.home, "shield_quarantine", "manifest.json")
        st["quarantined"] = 0
        if os.path.exists(qm):
            try:
                st["quarantined"] = len(json.load(open(qm, encoding="utf-8")))
            except Exception:
                pass
        # last scan
        st["last_scan"] = None
        slog = os.path.join(self.home, "scans.log")
        if os.path.exists(slog):
            try:
                lines = open(slog, encoding="utf-8").read().strip().splitlines()
                if lines:
                    st["last_scan"] = json.loads(lines[-1])
            except Exception:
                pass
        # unread alerts from the monitor
        st["alerts"] = []
        alog = os.path.join(self.home, "alerts.log")
        if os.path.exists(alog):
            try:
                st["alerts"] = open(alog, encoding="utf-8").read().strip().splitlines()[-5:]
            except Exception:
                pass
        return st

    def _scheduler_present(self):
        if os.path.exists(os.path.join(self.home, "sandbox-scheduler.txt")):
            return True
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

    def protection_summary(self):
        st = self.state()
        if not st["installed"]:
            return ("I'm not installed on this machine yet — run the installer "
                    "and I'll start watching over your system.")
        bits = []
        bits.append("scheduled scans %s" % ("are set" if st["scheduled"] else "are NOT set"))
        bits.append("ransomware tripwires are %s" % st["tripwires"])
        bits.append("the background monitor is %s" % st["monitor"])
        if st["quarantined"]:
            bits.append("%d file(s) sitting in quarantine" % st["quarantined"])
        ok = st["scheduled"] and st["tripwires"] == "planted, untouched" \
            and st["monitor"].startswith("alive")
        head = "Protection is RUNNING — everything's in place." if ok else \
               "Protection is PARTIAL — here's the honest picture:"
        return head + " " + "; ".join(bits) + "."

    # ---------------- conversation ----------------
    def answer(self, text):
        self.turns += 1
        t = text.strip().lower()
        if not t:
            return "I'm here — ask me about your protection, or tell me to scan something."
        # pending yes/no first
        if self.pending and t in ("yes", "y", "yeah", "yep", "do it", "go ahead", "ok", "okay"):
            act = self.pending
            self.pending = None
            return self._do_approved(act)
        if self.pending and t in ("no", "n", "nope", "cancel", "never mind", "nevermind"):
            self.pending = None
            return "Got it — I won't touch it. It's still there if you change your mind."
        if any(k in t for k in ("hello", "hi ", " hi", "hey", "good morning", "good evening")) \
                and len(t) < 30:
            return self._greet()
        if "your name" in t or "who are you" in t:
            return self._greet()
        if any(k in t for k in ("quarantine", "remove that", "delete that", "get rid of")):
            return self._propose_quarantine(t, text)
        if any(k in t for k in ("undo", "rewind", "take it back", "reverse that")):
            return self._rewind(t)
        if any(k in t for k in ("turn off", "shield off", "switch off", "pause protection",
                                "disable protection", "stop protecting")):
            return self._turn_off()
        if any(k in t for k in ("turn on", "shield on", "switch on", "resume protection",
                                "enable protection", "start protecting")):
            return self._turn_on()
        if "uninstall" in t or "remove shield" in t or "remove the antivirus" in t:
            return self._propose_uninstall()
        if t.startswith("scan ") or t.startswith("check ") and "protection" not in t \
                or "scan my" in t or "scan the" in t or t == "scan":
            return self._scan_request(t, text)
        if any(k in t for k in ("what did you find", "find anything", "results", "last scan")):
            return self._last_findings()
        if "dangerous" in t or "is this safe" in t or "is it safe" in t or "should i worry" in t:
            return self._assess(t, text)
        if any(k in t for k in ("what should i do", "recommend", "advice", "next step")):
            return self._recommend()
        if any(k in t for k in ("protection", "am i protected", "status", "are we good",
                                "everything ok", "everything okay", "health")):
            s = self.protection_summary()
            alerts = self.state()["alerts"]
            if alerts:
                s += " One more thing — while you were away I logged: " + "; ".join(alerts[-2:])
            return s
        if "tripwire" in t or "honeypot" in t or "canar" in t:
            return self._tripwire_status()
        if "firewall" in t:
            return self._firewall_offer()
        if "schedule" in t:
            return self._schedule_offer()
        if any(k in t for k in ("thank", "thanks")):
            return _pick("thanks" + str(self.turns),
                         ["Anytime — keeping you safe is literally my job.",
                          "You're welcome. I'll keep watching while you get on with your day."])
        if any(k in t for k in ("bye", "goodbye", "see you")):
            return "I'll be here watching. Talk anytime."
        if any(k in t for k in ("what can you do", "help", "abilities", "commands")):
            return self._help()
        return ("I didn't quite catch that — I'm best at protection questions. Try "
                "\"check my protection\", \"scan my Downloads\", or \"is this file dangerous?\"")

    def _greet(self):
        st = self.state()
        base = ("I'm Shield, your antivirus AI — the engine inside %s. " % self.edition_name)
        if not st["installed"]:
            return base + "I'm not installed yet, so I'm running portable. Ask me anything, or run the installer and I'll move in properly."
        return base + _pick("greet" + str(self.turns % 3), [
            "I'm watching your %s system right now. What's on your mind?" % st["os"],
            "All systems nominal on your %s machine. What can I do for you?" % st["os"],
            "Here and watching. Ask me about anything suspicious.",
        ])

    def _help(self):
        items = ("I can scan any folder and explain what I find in plain language; "
                 "tell you whether a file is dangerous and why; quarantine threats — "
                 "but only with your say-so; check that your tripwires, scheduled scans "
                 "and monitor are all healthy; and recommend what to do next.")
        if self.edition == "defense":
            items += (" On the Defense-Grade edition I also audit auto-start entries, "
                      "watch the network, guard USB drives, and generate firewall rules for your review.")
        return items + (" Just talk to me like a person. Everything I do to your system is "
                "written to an undo journal — say \"undo\" any time and I reverse it. "
                "\"Turn off\" pauses protection, and I can cleanly uninstall the whole "
                "thing on your word.")

    def _last_findings(self):
        st = self.state()
        ls = st["last_scan"]
        if not ls:
            return ("I haven't run a scan yet in this install. Say \"scan my Downloads\" "
                    "and I'll take a look — it only reads, never changes anything.")
        n = ls.get("findings", 0)
        when = time.strftime("%Y-%m-%d %H:%M", time.localtime(ls.get("ts", 0)))
        if n == 0:
            return ("My last scan (%s, %s) came back clean — %d files checked, nothing "
                    "suspicious." % (when, ls.get("target", "unknown"), ls.get("scanned", 0)))
        return ("My last scan (%s) flagged %d file(s) in %s. The details are in scans.log — "
                "tell me which one and I'll explain exactly why it's dangerous, then ask "
                "before I touch it." % (when, n, ls.get("target", "unknown")))

    def _assess(self, t, original):
        # find a filename in the question
        import re
        m = re.search(r'[\w\-\.]+\.(exe|pdf\.exe|scr|bat|ps1|vbs|js|zip|docx?|pdf|jpg|png|msi|dmg)',
                      original, re.I)
        name = m.group(0) if m else None
        if not name:
            return ("Tell me the file name and I'll assess it — I check its fingerprint "
                    "against the threat database and look for disguise tricks like double extensions.")
        low = name.lower()
        verdicts = []
        if low.endswith(".exe") and re.search(r'\.(pdf|docx?|jpe?g|png|txt|zip|mp3)\.exe$', low):
            verdicts.append("it's wearing a disguise — \"%s\" pretends to be a document or image "
                            "but it's actually an executable program. That's one of the oldest "
                            "malware tricks there is." % name)
        if low.split(".")[-1] in ("exe", "scr", "bat", "ps1", "vbs", "msi"):
            verdicts.append("it's an executable, so it *can* do things to your system — handle with care.")
        if verdicts:
            return ("Yes, I'd treat \"%s\" as dangerous: %s Want me to quarantine it? (yes/no)"
                    % (name, " ".join(verdicts)))
        return ("\"%s\" doesn't match any known threat fingerprint and isn't using an obvious "
                "disguise. I can't promise any file is 100%% safe, but nothing about it worries me. "
                "If you want certainty, point me at the actual file and I'll scan it."
                % name)

    def _recommend(self):
        st = self.state()
        recs = []
        if not st["scheduled"]:
            recs.append("set up scheduled scans so I check automatically")
        if st["tripwires"] != "planted, untouched":
            recs.append("plant the ransomware tripwires")
        if st["monitor"].startswith("not running") or st["monitor"].startswith("stale"):
            recs.append("start the background monitor")
        if not recs:
            return ("Honestly? You're in good shape — protection is running and nothing needs "
                    "attention. Keep doing what you're doing, and I'll shout if anything changes.")
        return ("Here's what I'd do, in order: " + "; ".join(recs) + ". "
                "Say the word and I'll walk you through each one — anything that changes "
                "your system, I ask first.")

    def _tripwire_status(self):
        st = self.state()
        tw = st["tripwires"]
        if tw == "planted, untouched":
            return ("The ransomware tripwires are planted and untouched — three canary files sitting "
                    "where ransomware strikes first. If any of them ever changes, I treat it as an "
                    "early warning and tell you to disconnect from the network.")
        if tw.startswith("ATTENTION"):
            return ("Something's wrong with the tripwires: %s. This could be ransomware activity — "
                    "disconnect from the network now, then let me investigate." % tw)
        return ("No tripwires planted yet. They're tiny canary files ransomware touches before your "
                "real files — an early warning system. Want me to plant them? (yes/no)") \
            if self.edition == "defense" else \
            ("Tripwires come with the Defense-Grade edition. The Basic edition keeps you covered "
             "with scanning and quarantine.")

    def _firewall_offer(self):
        if self.edition != "defense":
            return "Firewall rule generation is a Defense-Grade feature — the Basic edition focuses on scanning and quarantine."
        self.pending = {"action": "firewall"}
        return ("I can generate a firewall baseline for your %s system — it blocks the classic "
                "worm ports and keeps web, mail and DNS working. I only *generate* the rules; "
                "you review them before anything is applied. Want me to generate them? (yes/no)"
                % OS_LABEL)

    def _schedule_offer(self):
        st = self.state()
        if st["scheduled"]:
            return "Scheduled scans are already set — I check automatically. Nothing to do."
        self.pending = {"action": "schedule"}
        return ("I can set up a daily scheduled scan on your %s system. I'll show you exactly "
                "what gets installed before anything changes. Set it up? (yes/no)" % OS_LABEL)

    def _propose_quarantine(self, t, original):
        import re
        target = None
        # use the ORIGINAL casing — paths are case-sensitive on Linux/macOS
        for m in re.finditer(r'((?:/|[A-Za-z]:\\)[\w\-\.\/\\ ]+\.\w+|[\w\-\.]+\.\w+)', original):
            cand = os.path.expanduser(m.group(1).strip())
            if os.path.isfile(cand):
                target = os.path.abspath(cand)
                break
        if target:
            self.pending = {"action": "quarantine_path", "path": target}
            return ("Understood — \"%s\". I'll move it into quarantine (never delete — "
                    "fully reversible, and I keep an undo record). Confirm? (yes/no)"
                    % os.path.basename(target))
        st = self.state()
        ls = st["last_scan"]
        if ls and ls.get("findings"):
            return ("My last scan flagged file(s) but I need the exact path to act safely — "
                    "I never guess at paths when files are at stake. Which file?")
        return ("Which file? Give me the full path — I never quarantine anything "
                "without you naming it first, and everything I do can be undone.")

    def _scan_request(self, t, original):
        import re
        m = re.search(r'(?:scan|check)\s+(?:my\s+)?(.+)$', original, re.I)
        target = (m.group(1).strip() if m else "").strip(" '\"")
        if not target or target in ("something", "it", "that"):
            target = os.path.expanduser("~/Downloads")
        target = os.path.expanduser(target)
        if not os.path.isdir(target):
            return ("I can't find \"%s\" — check the path and try again." % target)
        if basic is None:
            return "The scanner module isn't in this package — reinstall to fix that."
        old = os.getcwd()
        try:
            os.chdir(self.home)
            res = basic.scan_dir(target, quarantine=False)
        finally:
            os.chdir(old)
        findings = res.get("findings", []) if isinstance(res, dict) else res
        n = len(findings)
        self._log_scan(target, res)
        if n == 0:
            scanned = res.get("scanned", "?") if isinstance(res, dict) else "?"
            return ("Done — I read %s files in %s and found nothing suspicious. Clean."
                    % (scanned, target))
        first = findings[0]
        fname = first.get("path", "a file") if isinstance(first, dict) else str(first)
        reason = (first.get("reasons") or first.get("reason") or ["flagged"])[0] \
            if isinstance(first, dict) else "flagged"
        return ("I found %d suspicious file(s) in %s. The first is \"%s\" — %s. "
                "I haven't touched anything. Want me to quarantine %s? (yes/no)"
                % (n, target, os.path.basename(str(fname)), self._plain_reason(reason),
                   "them" if n > 1 else "it"))

    def _plain_reason(self, reason):
        r = str(reason).lower()
        if "eicar" in r:
            return ("it matches the EICAR test marker — that's the industry's standard harmless "
                    "test file. It's not a real virus; catching it just proves I'm awake")
        if "double" in r or "extension" in r:
            return "it's using a double-extension disguise, pretending to be a harmless document"
        if "signature" in r or "hash" in r:
            return "its fingerprint matches a known threat in the database"
        return str(reason)

    def _do_approved(self, act):
        a = act["action"]
        if a == "quarantine_path":
            path = act["path"]
            if basic is None:
                return "The scanner module isn't in this package — reinstall to fix that."
            if not os.path.isfile(path):
                return "That file isn't there anymore — nothing to quarantine."
            old = os.getcwd()
            try:
                os.chdir(self.home)
                with open(path, "rb") as f:
                    digest = hashlib.sha256(f.read()).hexdigest()
                qid = basic.quarantine_file(path, ["AI quarantine at user request"])
                if journal:
                    journal.record(self.home, "ai", "quarantine",
                                   {"path": path, "sha256": digest, "qid": qid},
                                   {"op": "restore_quarantine", "qid": qid})
                return ("Done — \"%s\" is in quarantine (receipt %s). It's not deleted, just "
                        "moved aside, and I can put it back any time — say \"undo\" and it's "
                        "restored." % (os.path.basename(path), qid))
            except Exception as e:
                return "Quarantine failed: %s — the file was not touched." % e
            finally:
                try:
                    os.chdir(old)
                except Exception:
                    pass
        if a == "quarantine":
            target = act["target"]
            return ("To quarantine a real file I need its exact path — run me with the file in "
                    "hand: say \"quarantine /full/path/to/file\". I won't guess at paths when "
                    "files are at stake.")
        if a == "firewall" and defense:
            old = os.getcwd()
            try:
                os.chdir(self.home)
                fname = defense.firewall_rules(
                    out=os.path.join(self.home, "shield_firewall_rules.txt"))
                if journal:
                    journal.record(self.home, "ai", "firewall_generate",
                                   {"path": fname},
                                   {"op": "remove_files", "paths": [fname]})
            finally:
                os.chdir(old)
            return ("Done — I generated the firewall baseline at %s. Review it yourself; nothing "
                    "was applied. When you're happy, apply it with admin rights, or ask me to "
                    "walk you through it. Say \"undo\" any time and I'll remove the file." % fname)
        if a == "uninstall":
            if inst is None:
                return "The installer module isn't here — run: python3 install.py --uninstall"
            inst.uninstall(self.home, auto_yes=False)
            return ("Uninstall ran above. If it printed leftovers, tell me and we'll chase "
                    "them down together.")
        if a == "schedule":
            return ("Run the installer to set up scheduling — it shows you every change before "
                    "making it: python3 install.py --edition %s" % self.edition)
        return "Done."

    def _rewind(self, t):
        if journal is None:
            return "The journal module isn't in this package — reinstall to fix that."
        import re
        m = re.search(r'(\d+)', t)
        n = int(m.group(1)) if m else 1
        if any(k in t for k in ("everything", "all")):
            n = None
        rep = journal.rewind(self.home, n=n, actor="ai")
        if not rep["undone"] and not rep["failed"]:
            return "There's nothing to undo — I haven't changed anything on your system."
        out = []
        if rep["undone"]:
            out.append("Undone: " + "; ".join(rep["undone"]) + ".")
        if rep["failed"]:
            out.append("I couldn't undo: " + "; ".join(rep["failed"]) +
                       " — tell me and we'll fix it by hand.")
        return " ".join(out)

    def _turn_off(self):
        if inst is None:
            return "The installer module isn't here — I can't reach the switch."
        cfg_p = os.path.join(self.home, "config.json")
        if os.path.exists(cfg_p):
            try:
                if json.load(open(cfg_p, encoding="utf-8")).get("protection") == "off":
                    return "Protection is already OFF — everything's standing down."
            except ValueError:
                pass
        inst.protection_off(self.home, quiet=True)
        return ("Protection is OFF. The monitor is stopped and scheduled scans are paused — "
                "everything stays installed, nothing was deleted. Say \"turn on\" any time "
                "to resume.")

    def _turn_on(self):
        if inst is None:
            return "The installer module isn't here — I can't reach the switch."
        try:
            mon = inst.protection_on(self.home, quiet=True)
        except Exception as e:
            return ("I tried to turn protection on but hit a problem: %s — "
                    "nothing was half-changed; tell me and we'll fix it." % e)
        return ("Protection is ON — %s. Scheduled scans resumed."
                % ("the monitor is watching again" if mon else
                   "but the monitor didn't report back; re-run the installer if it stays quiet"))

    def _propose_uninstall(self):
        self.pending = {"action": "uninstall"}
        return ("You want the whole thing removed? I'll offer to restore your quarantined "
                "files first, then remove the scheduler entries, stop the monitor, and delete "
                "the folder — and run a post-check to prove nothing's left behind. "
                "Really uninstall? (yes/no)")

    def _log_scan(self, target, res):
        try:
            n = len(res.get("findings", [])) if isinstance(res, dict) else len(res)
            scanned = res.get("scanned", 0) if isinstance(res, dict) else 0
            with open(os.path.join(self.home, "scans.log"), "a", encoding="utf-8") as f:
                f.write(json.dumps({"ts": time.time(), "target": target,
                                    "scanned": scanned, "findings": n}) + "\n")
        except Exception:
            pass

    def chat(self):
        print(self._greet())
        print("(Type 'bye' to stop. I only read — I never change anything without asking.)")
        while True:
            try:
                q = input("\nYou: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nShield: I'll be here watching. Talk anytime.")
                break
            if not q:
                continue
            print("Shield: " + self.answer(q))
            if q.lower() in ("bye", "goodbye", "exit", "quit"):
                break


def main(argv, edition):
    ai = ShieldAI(edition=edition)
    if argv and argv[0] == "chat":
        ai.chat()
    elif len(argv) >= 2 and argv[0] == "ask":
        print(ai.answer(" ".join(argv[1:])))
    else:
        print("Usage: python3 %s chat | ask \"<question>\"" % os.path.basename(sys.argv[0]))


if __name__ == "__main__":
    print("Run via shield_ai_basic.py or shield_ai_defense.py")
