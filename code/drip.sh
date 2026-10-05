#!/bin/bash
# Antivirus add-on drip — +500 JAH-AV records every 2h toward 1M (silent run).
set -e
cd /home/hatch/workspace/signature-antivirus
git pull -q origin main || true
python3 code/gen_addons.py --n 500
python3 code/build_pages.py > /dev/null
git add -A
if git diff --cached --quiet; then echo "DRIP: no changes"; exit 0; fi
TOTAL=$(python3 -c "import json;print(json.load(open('data/addons/index.json'))['count'])")
git -c user.name="JAH System" -c user.email="jah@antivirus.local" \
    commit -qm "Antivirus drip: +500 add-ons ($TOTAL total)"
git push -q origin main
echo "DRIP: +500 add-ons, $TOTAL total"
