#!/usr/bin/env python3
"""Build the downloadable Shield bundles (real zips of the real tools).

Each bundle is one download: unzip, run install.py, protection is RUNNING.
Called by code/build_pages.py so bundles stay fresh; safe to run standalone.
"""
import os
import zipfile

FIXED_DATE = (2026, 10, 5, 0, 0, 0)  # deterministic zips: unchanged tools = byte-identical bundles

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(REPO, "tools")
OUT = os.path.join(REPO, "downloads")

FILES = ("install.py", "shield_status.py", "shield_monitor.py", "shield_ai.py",
         "shield_ai_basic.py", "shield_ai_defense.py", "shield_journal.py",
         "shield_basic.py", "shield_defense.py", "shield_scan.py",
         "shield_update.py", "signatures.json")

# Downloadable parts: each module separately, so a user can fetch only what
# they need. install.py --assemble <folder> validates the parts, compiles
# them, and builds the working tool from them.
PARTS = {
    "signature-shield-part-engine.zip": (
        "The engine — scanner core, quarantine with restore, the fail-safe "
        "action journal, and the status checker.",
        ("shield_basic.py", "shield_journal.py", "shield_status.py")),
    "signature-shield-part-signatures.zip": (
        "The signature database — threat fingerprints. Swap in a fresh one "
        "any time; the updater does this for you automatically.",
        ("signatures.json",)),
    "signature-shield-part-ai.zip": (
        "Shield AI — the conversational antivirus AI (Basic + Defense-Grade "
        "editions) that runs scans, explains findings, and regulates updates.",
        ("shield_ai.py", "shield_ai_basic.py", "shield_ai_defense.py")),
    "signature-shield-part-scans.zip": (
        "The scan modules — all six Signature scan types (quick, full, custom, "
        "USB, startup, memory) plus defense heuristics and the monitor.",
        ("shield_scan.py", "shield_defense.py", "shield_monitor.py")),
    "signature-shield-part-installer.zip": (
        "The installer & updater — assembles the parts into the working tool "
        "on your PC and keeps the signature database current.",
        ("install.py", "shield_update.py")),
}

PART_README = """Signature Shield — {label}
{desc}

PART {n} OF 5. This is one module of the whole Shield; the parts assemble into
the working tool on YOUR pc — nothing runs anywhere else.

FREE FOREVER: no accounts, no payments, no upsells, no trial traps.

ASSEMBLE (download the parts -> the installer compiles them -> protection RUNNING):
  1. Download all 5 part zips into ONE folder (or just the ones you need to
     refresh — the installer tells you if a part is missing).
  2. Unzip the installer part anywhere, then run:
       python3 install.py --assemble <the-folder-with-the-parts> [--edition ai-defense]
     The installer validates every part, compiles the modules, and installs
     the working tool. It shows every step and asks before touching your
     system scheduler. Nothing changes silently.
  3. Look for: PROTECTION: RUNNING

Or skip the parts and grab one full bundle instead (same tool, one download).
To remove cleanly later: python3 install.py --uninstall

Your system stays yours.
"""

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


def _write_zip(path, files, readme_text):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for fn in files:
            src = os.path.join(TOOLS, fn)
            if os.path.exists(src):
                zi = zipfile.ZipInfo(fn, date_time=FIXED_DATE)
                zi.external_attr = 0o644 << 16
                with open(src, "rb") as f:
                    z.writestr(zi, f.read())
        zi = zipfile.ZipInfo("README.txt", date_time=FIXED_DATE)
        zi.external_attr = 0o644 << 16
        z.writestr(zi, readme_text)
    print("wrote", path, os.path.getsize(path), "bytes")


def main():
    os.makedirs(OUT, exist_ok=True)
    for bundle, (desc, edition) in BUNDLES.items():
        ai_file = {"ai-defense": "shield_ai_defense.py",
                   "ai-basic": "shield_ai_basic.py"}.get(edition)
        _write_zip(os.path.join(OUT, bundle), FILES, README.format(
            name=bundle.replace(".zip", "").replace("-", " ").title(),
            desc=desc, edition=edition,
            ai_line=AI_LINE.format(ai=ai_file) if ai_file else ""))
    for i, (part, (desc, files)) in enumerate(PARTS.items(), 1):
        _write_zip(os.path.join(OUT, part), files, PART_README.format(
            label=part.replace(".zip", "").replace("-", " ").title(),
            desc=desc, n=i))


if __name__ == "__main__":
    main()
