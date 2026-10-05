#!/usr/bin/env python3
"""
Signature Shield AI Defense-Grade — the advanced AI edition (flagship download).

Everything in the Basic AI edition, plus the defense arsenal: the AI audits
auto-start entries, watches the network, guards USB drives, plants ransomware
tripwires, and generates firewall rules for your review. Same supervised rule:
it proposes, you approve — nothing destructive happens without your yes.

Usage:
  python3 shield_ai_defense.py chat          talk to Shield
  python3 shield_ai_defense.py ask "..."     one question, one answer
  python3 shield_ai_defense.py --self-test   prove it works
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from shield_ai import ShieldAI  # noqa: E402


def self_test():
    import tempfile
    import shutil
    home = tempfile.mkdtemp(prefix="aidef_")
    try:
        ai = ShieldAI(edition="defense", home=home)
        g = ai.answer("who are you")
        assert "Defense-Grade" in g, "greeting bad: %s" % g
        # defense extras are offered, supervised
        f = ai.answer("what about my firewall?")
        assert ai.pending is not None and ai.pending["action"] == "firewall", \
            "firewall not proposed: %s" % f
        y = ai.answer("yes")
        assert "generated" in y.lower() and "review" in y.lower(), \
            "firewall approval bad: %s" % y
        assert os.path.exists(os.path.join(home, "shield_firewall_rules.txt")), \
            "firewall file missing"
        t = ai.answer("are my tripwires ok?")
        assert "tripwire" in t.lower(), "tripwire bad: %s" % t
        h = ai.answer("what can you do")
        assert "firewall" in h.lower() and "usb" in h.lower(), "help bad: %s" % h
        ev = os.path.join(home, "evil.exe")
        open(ev, "w").write("x")
        q = ai.answer("quarantine %s" % ev)
        assert ai.pending is not None, "quarantine not proposed: %s" % q
        print("AI-DEFENSE SELF-TEST PASS — 6/6 defense conversations supervised")
        return 0
    except AssertionError as e:
        print("AI-DEFENSE SELF-TEST FAIL: %s" % e)
        return 1
    finally:
        shutil.rmtree(home, ignore_errors=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    from shield_ai import main as ai_main
    ai_main(sys.argv[1:], edition="defense")
