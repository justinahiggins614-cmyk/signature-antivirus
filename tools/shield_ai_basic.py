#!/usr/bin/env python3
"""
Signature Shield AI — the Basic AI edition (flagship download).

The AI is the engine: it watches your system, detects threats, explains them
in plain language, and regulates with your supervision — it acts on its own
only for safe, read-only checks, and always asks before changing anything.

Usage:
  python3 shield_ai_basic.py chat          talk to Shield
  python3 shield_ai_basic.py ask "..."     one question, one answer
  python3 shield_ai_basic.py --self-test   prove it works
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
    home = tempfile.mkdtemp(prefix="aibasic_")
    try:
        ai = ShieldAI(edition="basic", home=home)
        # 1. greeting is natural
        g = ai.answer("who are you")
        assert "Shield" in g and "watch" in g.lower(), "greeting bad: %s" % g
        # 2. dangerous assessment is plain-language
        a = ai.answer("is invoice.pdf.exe dangerous?")
        assert "disguise" in a.lower() and "yes" in a.lower(), "assess bad: %s" % a
        # 3. recommendations are honest when nothing installed
        r = ai.answer("what should i do")
        assert "installer" in r.lower() or "scan" in r.lower(), "recommend bad: %s" % r
        # 4. status is plain language (honest PARTIAL on a bare temp home)
        s = ai.answer("check my protection")
        assert "protection" in s.lower() and "partial" in s.lower(), "status bad: %s" % s
        # 5. quarantine is PROPOSED with confirmation, never executed blindly
        d2 = os.path.join(home, "dl")
        os.makedirs(d2)
        sus0 = os.path.join(d2, "suspicious.pdf.exe")
        open(sus0, "w").write("x")
        q = ai.answer("quarantine %s" % sus0)
        assert ai.pending and ai.pending.get("action") == "quarantine_path", \
            "quarantine was not proposed: %s" % q
        assert "yes/no" in q.lower() or "confirm" in q.lower(), "no confirmation ask: %s" % q
        # 6. declining is respected, file untouched
        d = ai.answer("no")
        assert ai.pending is None and "won't" in d.lower(), "decline bad: %s" % d
        assert os.path.exists(sus0), "file was touched after decline!"
        # 7. safe scan runs on its own
        open(os.path.join(d2, "clean.txt"), "w").write("hello")
        sc = ai.answer("scan %s" % d2)
        assert "suspicious" in sc.lower() or "found" in sc.lower(), "scan bad: %s" % sc
        # 8. supervised quarantine of a REAL file, then rewind restores it
        sus = os.path.join(d2, "evil.pdf.exe")
        open(sus, "w").write("x")
        p = ai.answer("quarantine %s" % sus)
        assert ai.pending and ai.pending.get("action") == "quarantine_path", \
            "no quarantine proposal: %s" % p
        assert "yes/no" in p.lower() or "confirm" in p.lower(), "no confirm ask: %s" % p
        y = ai.answer("yes")
        assert not os.path.exists(sus), "file not quarantined: %s" % y
        assert "undo" in y.lower(), "no undo mention: %s" % y
        u = ai.answer("undo")
        assert os.path.exists(sus), "rewind did not restore the file: %s" % u
        import shield_journal as journal
        assert not journal.entries(home), "journal not empty after rewind"
        # 9. off switch / on switch via chat
        import glob as _glob
        _binp = os.path.join(home, "bin")
        os.makedirs(_binp, exist_ok=True)
        for _f in _glob.glob(os.path.join(HERE, "*.py")) + \
                [os.path.join(HERE, "signatures.json")]:
            if os.path.exists(_f):
                shutil.copy2(_f, _binp)
        off = ai.answer("turn off protection")
        assert "off" in off.lower(), "off bad: %s" % off
        on = ai.answer("turn on")
        assert "on" in on.lower() and "problem" not in on.lower(), "on bad: %s" % on
        print("AI-BASIC SELF-TEST PASS — 9/9 conversations natural and supervised")
        return 0
    except AssertionError as e:
        print("AI-BASIC SELF-TEST FAIL: %s" % e)
        return 1
    finally:
        try:
            import install as inst
            inst.protection_off(home, quiet=True)
        except Exception:
            pass
        shutil.rmtree(home, ignore_errors=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    from shield_ai import main as ai_main
    ai_main(sys.argv[1:], edition="basic")
