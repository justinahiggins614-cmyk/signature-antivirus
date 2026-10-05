#!/usr/bin/env python3
"""Build the downloadable Shield bundles (real zips of the real tools).

Each bundle is one download: unzip, run install.py, protection is RUNNING.
Called by code/build_pages.py so bundles stay fresh; safe to run standalone.
"""
import os
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(REPO, "tools")
OUT = os.path.join(REPO, "downloads")

FILES = ("install.py", "shield_status.py", "shield_monitor.py", "shield_ai.py",
         "shield_ai_basic.py", "shield_ai_defense.py", "shield_journal.py",
         "shield_basic.py", "shield_defense.py", "signatures.json")

BUNDLES = {
    "signature-shield-ai.zip": (
        "Signature Shield AI Defense-Grade — the flagship. "
        "The AI actively regulates your system with your supervision.",
        "ai-defense"),
    "signature-shield-ai-basic.zip": (
        "Signature Shield AI (Basic) — the AI engine with classic-style scanning.",
        "ai-basic"),
    "signature-shield-basic.zip": (
        "Signature Shield Basic (classic) — signature scanning, quarantine, "
        "scheduled scans. No AI.",
        "basic"),
    "signature-shield-defense.zip": (
        "Signature Shield Defense-Grade (classic) — the full arsenal, no AI.",
        "defense"),
}

README = """Signature Shield — {name}
{desc}

FREE FOREVER: no accounts, no payments, no upsells, no trial traps.
To remove cleanly later: python3 install.py --uninstall

INSTALL (download -> run -> protection RUNNING):
  1. Unzip this file anywhere.
  2. python3 install.py --edition {edition}
     (The installer shows every step and asks before touching
      your system scheduler. Nothing changes silently.)
  3. Look for: PROTECTION: RUNNING

THEN:
  Check status anytime:            python3 shield_status.py
{ai_line}  Fail-safe rewind:  every AI action is journaled — say "undo" in chat.
  Off switch:  python3 install.py --off   /   --on to resume.
  Clean removal: python3 install.py --uninstall  (proves zero residue)

Your system stays yours.
"""

AI_LINE = "  Meet Shield, your antivirus AI:  python3 {ai} chat\n"


def main():
    os.makedirs(OUT, exist_ok=True)
    for bundle, (desc, edition) in BUNDLES.items():
        ai_file = {"ai-defense": "shield_ai_defense.py",
                   "ai-basic": "shield_ai_basic.py"}.get(edition)
        path = os.path.join(OUT, bundle)
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            for fn in FILES:
                src = os.path.join(TOOLS, fn)
                if os.path.exists(src):
                    z.write(src, fn)
            z.writestr("README.txt", README.format(
                name=bundle.replace(".zip", "").replace("-", " ").title(),
                desc=desc, edition=edition,
                ai_line=AI_LINE.format(ai=ai_file) if ai_file else ""))
        print("wrote", path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()
