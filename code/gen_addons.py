#!/usr/bin/env python3
"""Deterministic JAH-AV add-on record generator (marching to 1,000,000).

Seed records (origin=documented) describe real historic malware families —
public facts only. Generated records (origin=generated) are Signature-authored
heuristic defense profiles for malware CATEGORIES, clearly labeled as such;
they never pretend to be documented real-world malware.

Usage: python3 gen_addons.py --n 500 [--seed-only]
"""
import gzip
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data", "addons")
VOLDIR = os.path.join(DATA, "volumes")
STATE = os.path.join(DATA, "state.json")
INDEX = os.path.join(DATA, "index.json")
CHUNK = 500

DOCUMENTED = [
    # (name, year, type, level, vector, solution)
    ("Elk Cloner", 1982, "boot virus", "low",
     "Infected Apple II floppy boot sectors.",
     "Boot from a clean disk, then scan and rewrite the boot sector with Shield Basic."),
    ("Brain", 1986, "boot virus", "low",
     "Infected PC floppy boot sectors.",
     "Boot from clean media, scan with Shield Basic, restore the boot sector from a known-clean copy."),
    ("Melissa", 1999, "macro worm", "high",
     "Email attachment exploiting Word macros; mass-mailed itself.",
     "Delete the attachment unopened, disable macros, scan with Shield, update Office."),
    ("ILOVEYOU", 2000, "worm", "critical",
     "VBS email attachment disguised as a love letter; overwrote media files.",
     "Delete the attachment, restore overwritten files from backup, scan with Shield Basic (flags .vbs heuristics)."),
    ("Anna Kournikova", 2001, "worm", "medium",
     "Email VBS attachment posing as a photo.",
     "Delete unopened, scan with Shield, enable email attachment filtering."),
    ("Code Red", 2001, "worm", "critical",
     "Exploited IIS servers; defaced websites, launched DDoS.",
     "Patch the web server, isolate the host, scan with Shield, restore defaced content from backup."),
    ("Nimda", 2001, "worm", "critical",
     "Spread via email, shares, and IIS in one package.",
     "Isolate the machine, patch IIS and browsers, full Shield scan, change exposed credentials."),
    ("SQL Slammer", 2003, "worm", "critical",
     "UDP buffer overflow in SQL Server; slowed the whole internet.",
     "Patch SQL Server, block UDP 1434 at the firewall (Shield Defense firewall rules), reboot clean."),
    ("Blaster", 2003, "worm", "high",
     "Exploited Windows RPC DCOM; forced reboots.",
     "Patch the RPC vulnerability, block TCP 135 at the firewall, scan with Shield in Safe Mode."),
    ("Sobig", 2003, "worm", "high",
     "Email worm with its own SMTP engine.",
     "Delete attachments, block the sender domain, scan with Shield, update antivirus signatures."),
    ("Sasser", 2004, "worm", "high",
     "Exploited LSASS; no email needed.",
     "Patch LSASS, block TCP 445/5554 (Shield Defense firewall rules), Safe-Mode scan with Shield."),
    ("MyDoom", 2004, "worm", "critical",
     "Fastest-spreading email worm of its era; opened backdoors.",
     "Delete attachments, scan with Shield, check bootcheck for backdoor persistence, change passwords."),
    ("Bagle", 2004, "worm", "high",
     "Email worm that disabled security software.",
     "Boot to Safe Mode, run Shield Basic from clean media, re-enable protections, change credentials."),
    ("Zeus", 2007, "banking trojan", "critical",
     "Stole banking credentials via form grabbing.",
     "Isolate, Safe-Mode Shield scan, assume credentials compromised — change all banking passwords from a clean device, enable 2FA."),
    ("Storm Worm", 2007, "trojan", "high",
     "Email trojan that built a peer-to-peer botnet.",
     "Delete the lure email, Safe-Mode scan, bootcheck for persistence, change email passwords."),
    ("QakBot", 2007, "banking trojan", "high",
     "Modular banking trojan spread by email and shares.",
     "Isolate, full Shield scan, credential reset from a clean machine, review network shares."),
    ("Conficker", 2008, "worm", "critical",
     "Exploited Windows Server service; disabled updates.",
     "Patch MS08-067, block TCP 445, Safe-Mode scan with Shield, re-enable Windows Update."),
    ("Stuxnet", 2010, "worm / sabotage", "critical",
     "USB-spread worm targeting industrial control systems.",
     "Remove infected USB media, scan air-gapped systems with Shield USB guard, rebuild controllers from known-clean images."),
    ("Duqu", 2011, "spyware", "high",
     "Espionage toolkit related to Stuxnet.",
     "Isolate, memory + disk scan with Shield, rebuild from clean images, rotate all credentials."),
    ("Flame", 2012, "spyware", "high",
     "Modular espionage malware.",
     "Isolate, full Shield heuristic scan, rebuild affected systems, audit exfiltrated data scope."),
    ("Shamoon", 2012, "wiper", "critical",
     "Wiped disks across corporate networks.",
     "Isolate immediately, restore from offline backups (wiped data is unrecoverable), rebuild, segment the network."),
    ("CryptoLocker", 2013, "ransomware", "critical",
     "Email-attachment ransomware; encrypted user files.",
     "Disconnect from network, do NOT pay from the infected machine, restore from clean backups, Safe-Mode Shield scan, patch and harden."),
    ("Emotet", 2014, "trojan / botnet", "critical",
     "Email-delivered modular malware platform.",
     "Delete the lure, isolate, Safe-Mode Shield scan, bootcheck for scheduled-task persistence, reset credentials."),
    ("Dridex", 2014, "banking trojan", "high",
     "Macro-email banking credential stealer.",
     "Disable macros, delete the document, Shield scan, change banking passwords from a clean device."),
    ("Petya", 2016, "ransomware", "critical",
     "Encrypted the master boot record.",
     "Do not reboot (reboot triggers encryption), image the disk, restore MBR from clean media or restore from backup."),
    ("Locky", 2016, "ransomware", "critical",
     "Macro-document ransomware.",
     "Disconnect, restore from clean backups, Safe-Mode Shield scan, disable macros network-wide."),
    ("TrickBot", 2016, "trojan", "high",
     "Modular banking trojan, Emotet's successor payload.",
     "Isolate, Safe-Mode Shield scan, bootcheck, credential reset from clean hardware."),
    ("Mirai", 2016, "IoT botnet", "high",
     "Enslaved cameras/routers with default passwords.",
     "Change ALL default passwords on IoT devices, update firmware, isolate IoT on a separate network segment."),
    ("WannaCry", 2017, "ransomware worm", "critical",
     "Exploited SMB (MS17-010); encrypted files across networks.",
     "Isolate, patch MS17-010 everywhere, block SMB at the firewall (Shield Defense rules), restore from clean backups, Safe-Mode Shield scan."),
    ("NotPetya", 2017, "wiper", "critical",
     "Posed as ransomware; actually destroyed data irreversibly.",
     "Isolate immediately — do not pay (decryption was never possible), restore from offline backups, rebuild systems."),
    ("Bad Rabbit", 2017, "ransomware", "high",
     "Drive-by fake Flash update ransomware.",
     "Disconnect, restore from clean backups, Safe-Mode Shield scan, block the distribution sites at DNS/firewall."),
    ("Ryuk", 2018, "ransomware", "critical",
     "Targeted big-game ransomware, often via TrickBot/Emotet.",
     "Isolate, engage backups (offline copies), rebuild, full Shield Defense apply-all hardening afterward."),
]

CATEGORIES = [
    ("ransomware", "critical",
     "Isolate the machine from the network, identify the strain, restore from clean offline backups, "
     "Safe-Mode Shield scan, patch the entry vector, then run Shield Defense apply-all."),
    ("worm", "high",
     "Isolate, patch the exploited service, block its ports with Shield Defense firewall rules, "
     "Safe-Mode Shield scan across shares, change exposed credentials."),
    ("trojan", "high",
     "Delete the lure, Safe-Mode Shield scan, bootcheck for persistence entries, "
     "reset credentials from a clean device."),
    ("spyware", "medium",
     "Full Shield heuristic scan, remove the bundling program, check browser extensions, "
     "rotate passwords for accounts used on the machine."),
    ("adware", "low",
     "Uninstall the bundling application, Shield scan, reset browser settings, "
     "review startup entries with bootcheck."),
    ("rootkit", "critical",
     "Scan from clean boot media (rootkits hide from the running OS), rebuild if the kernel is compromised, "
     "restore from known-clean images."),
    ("keylogger", "high",
     "Shield heuristic scan (flags keylogging keywords), change ALL typed passwords from a clean device, "
     "enable 2FA everywhere."),
    ("botnet", "high",
     "Isolate, Safe-Mode Shield scan, bootcheck for scheduled tasks/services, "
     "block command-and-control indicators at the firewall."),
    ("wiper", "critical",
     "Isolate immediately, restore from offline backups, rebuild — wiped data is unrecoverable by design."),
    ("scareware", "low",
     "Do not pay or call the number. Force-close the browser, Shield scan, "
     "clear browser data, report the page."),
]

GEN_PREFIX = {"ransomware": "Cryptor", "worm": "Wormlet", "trojan": "Trojaner",
              "spyware": "Spyweave", "adware": "Adspew", "rootkit": "Rootshade",
              "keylogger": "Keysnare", "botnet": "Botswarm", "wiper": "Wipeout",
              "scareware": "Scarecrow"}


def load_state():
    if os.path.exists(STATE):
        with open(STATE) as f:
            return json.load(f)
    return {"next_index": 1}


def save_state(s):
    os.makedirs(DATA, exist_ok=True)
    with open(STATE, "w") as f:
        json.dump(s, f)


def chunk_path(n):
    return os.path.join(VOLDIR, "addons-c%05d.jsonl.gz" % n)


def append_records(records):
    os.makedirs(VOLDIR, exist_ok=True)
    st = load_state()
    idx = st["next_index"]
    for r in records:
        r["id"] = "JAH-AV-%06d" % idx
        idx += 1
    st["next_index"] = idx
    save_state(st)
    # append into current chunk (roll at CHUNK)
    existing = 0
    n = 1
    while os.path.exists(chunk_path(n)):
        with gzip.open(chunk_path(n), "rt", encoding="utf-8") as f:
            c = sum(1 for _ in f)
        if c < CHUNK:
            existing = c
            break
        n += 1
    else:
        n = 1 if not os.path.exists(chunk_path(1)) else n
    buf = list(records)
    while buf:
        room = CHUNK - existing
        take = buf[:room]
        with gzip.open(chunk_path(n), "at", encoding="utf-8") as f:
            for r in take:
                f.write(json.dumps(r) + "\n")
        buf = buf[room:]
        n += 1
        existing = 0
    return records


def make_documented():
    recs = []
    for name, year, typ, level, vector, solution in DOCUMENTED:
        recs.append({"name": name, "year": year, "type": typ, "level": level,
                     "vector": vector, "solution": solution,
                     "origin": "documented",
                     "note": "Documented historic malware family (public record)."})
    return recs


def make_generated(start, count):
    rng = random.Random(0x5EED + start)
    recs = []
    for i in range(count):
        cat, level, solution = CATEGORIES[(start + i) % len(CATEGORIES)]
        variant = (start + i) // len(CATEGORIES)
        recs.append({
            "name": "%s-variant-%04d" % (GEN_PREFIX[cat], variant),
            "year": None, "type": cat, "level": level,
            "vector": "Varies by strain — see the %s defense profile." % cat,
            "solution": solution, "origin": "generated",
            "note": ("Signature-generated heuristic defense profile for the %s category. "
                     "Not a claim about a specific real-world strain." % cat)})
    return recs


def rebuild_index():
    rows = []
    n = 1
    while os.path.exists(chunk_path(n)):
        with gzip.open(chunk_path(n), "rt", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                rows.append([r["id"], r["name"], r["type"], r["level"], r["origin"], n])
        n += 1
    rows.sort(key=lambda x: x[1].lower())
    with open(INDEX, "w", encoding="utf-8") as f:
        json.dump({"count": len(rows), "rows": rows}, f)
    # per-chunk detail files for the frontend
    detdir = os.path.join(DATA, "details")
    os.makedirs(detdir, exist_ok=True)
    n = 1
    while os.path.exists(chunk_path(n)):
        det = {}
        with gzip.open(chunk_path(n), "rt", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                det[r["id"]] = {"vector": r["vector"], "solution": r["solution"],
                                "note": r["note"], "year": r.get("year"),
                                "name": r["name"], "type": r["type"],
                                "level": r["level"], "origin": r["origin"]}
        with open(os.path.join(detdir, "details-c%05d.json" % n), "w",
                  encoding="utf-8") as f:
            json.dump(det, f)
        n += 1
    return len(rows)


def main(argv):
    n = 500
    if "--n" in argv:
        n = int(argv[argv.index("--n") + 1])
    st = load_state()
    if st["next_index"] == 1:
        recs = make_documented()
        st2 = load_state()
        if st2["next_index"] == 1:
            append_records(recs)
            print("seeded %d documented records" % len(recs))
    start = load_state()["next_index"]
    recs = make_generated(start, n)
    append_records(recs)
    total = rebuild_index()
    print("generated %d records, total %d" % (len(recs), total))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
