
# ============================ PAGE BODIES ============================

def index_body(n):
    return """
<div class="hero">
<h2>Every PC deserves every cure.</h2>
<p>The Signature Antivirus exists for one mission: <b>all solutions to all PC viruses</b> —
every cure, every immunity — free for every computer. Pick your protection, download the
real tools, run them on your own machine. No accounts. No cloud. No subscriptions. Your PC stays yours.</p>
</div>
<div class="osbanner" id="osBanner">Detecting your system&hellip;</div>
<div class="stats" role="status">
<div class="stat"><b id="stAddons">""" + str(n) + """</b><span>virus solutions archived</span></div>
<div class="stat"><b>1,000,000</b><span>march goal</span></div>
<div class="stat"><b>9</b><span>protection downloads</span></div>
<div class="stat"><b>100% free</b><span>free forever, no accounts</span></div>
</div>
<div class="mission"><b>Our mission statement.</b> Viruses do not care what system you run, and neither do we.
The Signature Antivirus gives every PC the full set of cures and immunities: a classic-style shield for everyday
threats, a defense-grade toolkit for the serious ones, and a solution add-on for every virus we know —
marching to one million. The tools detect your system automatically — a Mac does not need the same protection
as a Windows PC, and our profiles are honest about the difference. Everything is a download you run yourself.
Nothing phones home.</div>
<h2>How it works</h2>
<div class="cards">
<div class="card"><h3>1 &middot; Pick</h3><p>Choose <b>Signature Shield Basic</b> for everyday protection,
or <b>Defense-Grade</b> for the full arsenal. The site detects your system and pre-selects the right profile.</p></div>
<div class="card"><h3>2 &middot; Download</h3><p>Real Python tools — the scanner, the quarantine, the firewall-rule
generator, the USB guard, the ransomware tripwires. They run on <b>your</b> PC, not in our cloud.</p></div>
<div class="card"><h3>3 &middot; Run</h3><p><code>python3 install.py</code> — that is the whole
signup flow. The installer sets everything up, starts the resident monitor, and ends with
<b>PROTECTION: RUNNING</b>. One universal download detects your OS and applies the matching protection automatically.</p></div>
</div>
<div class="cards">
<div class="card"><h3>🛡️ The Antivirus</h3><p>Two downloads: <b>Signature Shield Basic</b> (the classic suite —
real-time-style scanning, quarantine, scheduled scans) and <b>Signature Shield Defense-Grade</b>
(behavioral heuristics, firewall rules, USB guard, ransomware honeypots, boot check, network monitor).</p>
<a class="btn" href="antivirus.html">Get protected</a></div>
<div class="card"><h3>🧩 The 1 Million Add-Ons</h3><p>A specific solution for every virus — documented historic
families plus heuristic defense profiles, marching to one million. Search it, or press <b>Apply all</b> and
harden your whole system at once.</p>
<a class="btn" href="addons.html">Browse the archive</a></div>
</div>
<div class="card flagship" id="uniRec"><h3>&#x1F6E1;&#xFE0F; The universal recommendation</h3>
<p class="flagtag">ONE CLICK &middot; BEST PROTECTION</p>
<p id="recOs">Detecting your system&hellip;</p>
<p><b>Signature Shield AI Defense-Grade</b> — the flagship. Shield, the antivirus AI, is the
engine: it runs every Signature scan type, explains findings in plain language, resolves with
your confirmation, and <b>regulates its own updates</b> — checking for new signature data on
schedule and applying it, always with an undo.</p>
<p class="note" id="sigStatus">Checking the signature database&hellip;</p>
<a class="btn" href="downloads/signature-shield-ai.zip" download>&#x2B07; Download the recommended Shield</a>
<p class="note">Built on well-known antivirus techniques &mdash; signature matching, heuristic
analysis, quarantine, behavioral monitoring &mdash; as an original Signature implementation.
No vendor code, no trademarks, no third-party engines.</p>
<p class="note">Want it your way? <a href="antivirus.html">Choose your edition</a> &middot;
<a href="scan.html">Pick your scan</a> &middot; <a href="antivirus.html#parts">Download in parts</a></p>
</div>
<p class="note"><b>Honest scope.</b> These are real, working tools with real capabilities, described exactly as
they behave. They do not replace your operating system's built-in protections — on macOS they coexist with
Gatekeeper and XProtect; on Windows they complement Windows Security. The starter signature database ships the
industry-standard EICAR test marker so you can verify detection yourself on day one.</p>
<script>""" + OS_JS + """
(function(){var os=detectOS(),p=PROFILES[os]||PROFILES['Unknown'];
document.getElementById('recOs').innerHTML=p.dl?'<b>For your '+os+' system:</b> one download — the installer detects your OS and applies the matching protection profile automatically.':'<b>You are on '+os+':</b> the tools run on PCs (Windows, macOS, Linux) — grab the download for your computer.';
fetch('tools/signatures.json').then(function(r){return r.json();}).then(function(j){
 var m=j.meta||{};
 document.getElementById('sigStatus').innerHTML='<b>Protection current as of '+(m.updated||'?')+'</b> &middot; signature database v'+(m.version||'?')+' &middot; updated as new data arrives.';}).catch(function(){
 document.getElementById('sigStatus').textContent='Signature database status unavailable offline — the download carries the latest.';});
document.getElementById('osBanner').innerHTML='<b>Detected system: '+os+'.</b> '+p.note+
' <a href="antivirus.html" style="color:#7ec8ff">Your protection profile is ready &rarr;</a>';})();</script>
"""

INDEX_WELCOME = ("<li><b>Pick your protection.</b> Basic for everyday threats, Defense-Grade for the full arsenal — "
 "the site detects your system and pre-selects the right profile.</li>"
 "<li><b>Download, don't subscribe.</b> Real Python tools you run on your own PC. No accounts, no cloud.</li>"
 "<li><b>Browse the cures.</b> The add-on archive holds a specific solution for every virus — search it or Apply all.</li>")


def antivirus_body():
    return """
<div class="hero"><h2>Download your protection</h2>
<p>No accounts. No cloud. No subscriptions. Choose a shield, download it, run it on your PC.
One universal download detects your system automatically and applies the matching profile.</p>
<p class="freeforever"><b>Free forever.</b> No accounts, no payments, no upsells, no trial traps —
every tool is yours. If anything ever goes wrong, uninstalling removes everything cleanly.
Built on well-known antivirus techniques &mdash; signature matching, heuristic analysis,
quarantine, behavioral monitoring &mdash; as an original Signature implementation: no vendor
code, no trademarks, no third-party engines.</p></div>
<div class="osbanner" id="osBanner2">Detecting your system&hellip;</div>
<h2>Get running in 3 steps</h2>
<div class="cards">
<div class="card"><h3>1 &middot; Download</h3><p>Pick your Shield below — one zip with everything
inside: the installer, the AI engine, the scanners, the status checker.</p></div>
<div class="card"><h3>2 &middot; Run the installer</h3><p>Unzip, then <code>python3 install.py</code>.
It shows every step, asks before touching your system scheduler, and plants the
ransomware tripwires. Nothing changes silently.</p></div>
<div class="card"><h3>3 &middot; Protection running</h3><p>The installer ends with
<b>PROTECTION: RUNNING</b>. Check any time with <code>python3 shield_status.py</code>,
and meet Shield — your antivirus AI — with <code>python3 shield_ai_defense.py chat</code>.</p></div>
</div>
<h2>Choose your Shield</h2>
<div class="cards">
<div class="card flagship"><h3>&#x1F916; Signature Shield AI Defense-Grade</h3>
<p class="flagtag">FLAGSHIP &middot; RECOMMENDED</p>
<p><b>The AI is the engine.</b> Shield watches your system, detects threats, explains them in
plain language, and regulates with your supervision — it asks before anything destructive,
and every action carries an undo.</p>
<a class="btn" href="downloads/signature-shield-ai.zip" download>&#x2B07; Download the AI Shield</a></div>
<div class="card"><h3>&#x1F916; Signature Shield AI (Basic)</h3>
<p>The AI engine with classic-style scanning — signature database, quarantine, scheduled
scans, all explained conversationally and all reversible.</p>
<a class="btn" href="downloads/signature-shield-ai-basic.zip" download>&#x2B07; Download AI Basic</a></div>
<div class="card"><h3>&#x1F6E1;&#xFE0F; Signature Shield Basic</h3>
<p><b>The classic suite, Signature-style.</b> SHA-256 signature scanning, quarantine with
one-command restore, scheduled scans, double-extension detection. No AI — just the tools.</p>
<a class="btn sec" href="downloads/signature-shield-basic.zip" download>&#x2B07; Download Basic</a></div>
<div class="card"><h3>&#x1F6E1;&#xFE0F;&#x2694;&#xFE0F; Signature Shield Defense-Grade</h3>
<p><b>The advanced arsenal, classic.</b> Behavioral heuristics, firewall-rules generator,
USB guard, ransomware tripwires, boot auditor, network monitor. No AI — just the tools.</p>
<a class="btn sec" href="downloads/signature-shield-defense.zip" download>&#x2B07; Download Defense-Grade</a></div>
</div>
<p class="note">Every bundle ships <code>--self-test</code> on every tool, the EICAR test marker
in the threat database, the fail-safe undo journal, the <b>off switch</b>
(<code>install.py --off</code> / <code>--on</code>), and the clean <b>uninstaller</b>
(<code>install.py --uninstall</code>) that proves zero residue.</p>
<h2 id="parts">Download in parts</h2>
<p>Prefer it modular? Each part downloads separately — the installer assembles ("compiles")
the parts into the working tool on <b>your</b> PC. Nothing runs anywhere else.</p>
<div class="cards">
<div class="card"><h3>1 &middot; Engine</h3><p>The scanner core, quarantine with one-command
restore, the fail-safe action journal, the status checker.</p>
<a class="btn sec" href="downloads/signature-shield-part-engine.zip" download>&#x2B07; Part 1: Engine</a></div>
<div class="card"><h3>2 &middot; Signatures</h3><p>The threat fingerprint database. Refresh this
part any time — or let Shield update it for you automatically.</p>
<a class="btn sec" href="downloads/signature-shield-part-signatures.zip" download>&#x2B07; Part 2: Signatures</a></div>
<div class="card"><h3>3 &middot; Shield AI</h3><p>The conversational antivirus AI (Basic +
Defense-Grade) — runs scans, explains findings, regulates updates.</p>
<a class="btn sec" href="downloads/signature-shield-part-ai.zip" download>&#x2B07; Part 3: AI</a></div>
<div class="card"><h3>4 &middot; Scan modules</h3><p>All six Signature scan types (quick, full,
custom, USB, startup, memory) plus defense heuristics and the monitor.</p>
<a class="btn sec" href="downloads/signature-shield-part-scans.zip" download>&#x2B07; Part 4: Scans</a></div>
<div class="card"><h3>5 &middot; Installer</h3><p>Assembles the parts into the working tool and
keeps the signature database current.</p>
<a class="btn sec" href="downloads/signature-shield-part-installer.zip" download>&#x2B07; Part 5: Installer</a></div>
</div>
<p><b>Assemble:</b> download all five parts into one folder, unzip the installer part, then run<br>
<code>python3 install.py --assemble &lt;the-folder-with-the-parts&gt;</code> — the installer
validates every part, compiles the modules, and finishes with <b>PROTECTION: RUNNING</b>.
Missing a part? It tells you exactly which one. The full bundles above remain the one-click option.</p>
<h2>Protection profiles — honest, per system</h2>
<table class="prof"><tr><th>Your system</th><th>What you get</th><th>Why</th></tr>
<tr><td><b>Windows</b></td><td>Full suite: signature + heuristic scan, netsh firewall rules, USB autorun guard,
ransomware honeypots, startup/registry boot check, network monitor</td>
<td>Windows faces the broadest malware landscape — it gets every layer.</td></tr>
<tr><td><b>macOS</b></td><td>Signature + heuristic scan, USB guard, honeypots, LaunchAgents/Daemons boot check,
network monitor, optional pf rules</td>
<td>macOS ships Gatekeeper and XProtect and faces a different, smaller threat landscape —
it does not need the same protection as Windows. Shield is a second opinion, not a replacement.</td></tr>
<tr><td><b>Linux</b></td><td>Signature + heuristic scan, USB guard, honeypots, systemd/cron boot check,
network monitor, ufw or nftables rules, permissions hardening</td>
<td>Linux threats ride permissions and services — the profile focuses there.</td></tr>
<tr><td><b>Not recognized</b></td><td>Portable signature + heuristic scan, generic hardening checklist</td>
<td>The scanner is pure Python and runs anywhere Python runs.</td></tr></table>
<h2>Try the scanner right here</h2>
<p class="note">Pick any file on your device — it is hashed <b>in your browser</b> (nothing uploads) and checked
against the EICAR test marker plus the double-extension disguise test.</p>
<div class="searchrow"><input type="file" id="tryFile" aria-label="Choose a file to check">
<button class="btn" id="tryBtn" type="button">Check this file</button></div>
<p id="tryOut" class="note" aria-live="polite"></p>
<script>""" + OS_JS + """
(function(){var os=detectOS(),p=PROFILES[os]||PROFILES['Unknown'];
var dl=p.dl?'Both downloads below run on '+os+' — the tools detect it again at runtime.':'You are on '+os+': the Python tools run on PCs (Windows, macOS, Linux) — the archive and checklists still apply.';
document.getElementById('osBanner2').innerHTML='<b>Detected system: '+os+'.</b> '+p.note+' '+dl;
var EICAR='275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f';
document.getElementById('tryBtn').onclick=function(){
 var f=document.getElementById('tryFile').files[0];if(!f){document.getElementById('tryOut').textContent='Choose a file first.';return;}
 var r=new FileReader();r.onload=function(){
  crypto.subtle.digest('SHA-256',r.result).then(function(h){
   var hex=Array.prototype.map.call(new Uint8Array(h),function(b){return ('0'+b.toString(16)).slice(-2)}).join('');
   var out=document.getElementById('tryOut'),msgs=[];
   if(hex===EICAR)msgs.push('MATCH: EICAR test marker detected — the scanner database works.');
   if(/\\.(pdf|doc|docx|jpg|png|txt|zip|mp3)\\.exe$/i.test(f.name))msgs.push('FLAG: double-extension disguise.');
   out.textContent=msgs.length?msgs.join(' '):'Clean: no signature match, no disguise pattern. (sha256 '+hex.slice(0,16)+'….)';
  });};
 r.readAsArrayBuffer(f);};})();</script>
"""

AV_WELCOME = ("<li><b>Your system is detected.</b> Windows, macOS, or Linux — the right profile is pre-selected.</li>"
 "<li><b>Meet Shield, the AI.</b> The flagship editions put the antivirus AI in charge — it watches, explains, asks before acting, and undoes anything on your word.</li>"
 "<li><b>Download, don't subscribe.</b> Real tools you run on your own PC. Free forever — no accounts, no payments.</li>"
 "<li><b>Prove it works.</b> Every tool ships <code>--self-test</code>; the database ships the EICAR test marker; uninstalling proves zero residue.</li>")

def addons_body(n):
    return """
<div class="hero"><h2>The 1 Million Add-On Archive</h2>
<p>A specific solution for <b>every virus</b> &mdash; documented historic families plus heuristic defense profiles,
marching to one million. Search for a threat, open its cure, or press <b>Apply all</b>.</p>
<p class="freeforever"><b>Free forever.</b> Every solution, every tool — no accounts, no payments, no upsells.</p></div>
<div class="stats" role="status">
<div class="stat"><b id="azCount">""" + str(n) + """</b><span>solutions archived</span></div>
<div class="stat"><b>1,000,000</b><span>march goal</span></div>
<div class="stat"><b id="docCount">&ndash;</b><span>documented families</span></div>
</div>
<div class="osbanner" id="applyAll"><b>&#x1F6E1;&#xFE0F; Apply all &mdash; full protection for your system.</b><br>
<span id="aaText">Detecting your system&hellip;</span><br>
<a class="btn warn" href="tools/shield_defense.py" download style="margin-top:8px">&#x2B07; Download the Apply-All toolkit</a>
<a class="btn sec" href="tools/shield_basic.py" download style="margin-top:8px">&#x2B07; Basic shield</a>
<p class="note" id="aaList" style="margin-top:8px"></p>
<p class="note">Honest mechanics: the button downloads the real toolkit. On your PC,
<code>python3 shield_defense.py apply-all</code> plants the ransomware tripwires, generates your firewall
rules, audits auto-start entries, and prints the hardening checklist &mdash; the full set for your detected system.</p></div>
<h2>&#x2B50; AI's Best of the Best</h2>
<div class="card" id="bestCard"><h3>WannaCry <span class="badge b-crit">critical</span>
<span class="badge b-doc">documented</span></h3>
<p class="note">JAH-AV-000029 &middot; ransomware worm &middot; 2017 &middot; public record</p>
<p><b>The pick:</b> the most instructive cure in the archive &mdash; network worm + ransomware in one package,
defeated by patching, firewalling, and clean backups. If you apply one solution by hand, make it this pattern.</p>
<p class="sol">Isolate, patch MS17-010 everywhere, block SMB at the firewall (Shield Defense rules),
restore from clean backups, Safe-Mode Shield scan.</p>
<button class="btn sec" data-dl="JAH-AV-000029">&#x2B07; Download the removal steps</button></div>
<div class="searchrow"><input id="azSearch" type="search" placeholder="&#x1F50E; Search the archive &mdash; virus name, type, or ID&hellip;" aria-label="Search add-ons"></div>
<div class="searchrow"><input id="aiAsk" type="search" placeholder="&#x1F916; Ask the AI &mdash; e.g. &ldquo;ransomware cure&rdquo;" aria-label="Ask the AI">
<button class="btn" id="aiGo" type="button">Ask</button></div>
<p id="aiOut" class="note" aria-live="polite"></p>
<div class="az" id="azList"><p class="note">Loading the archive&hellip;</p></div>
<p class="note"><b>Two kinds of records.</b> <span class="badge b-doc">documented</span> = real historic malware
families (public record). <span class="badge b-gen">generated</span> = Signature-authored heuristic defense
profiles for malware categories &mdash; honest training patterns, never presented as real-world strains.</p>
<script>""" + OS_JS + """
(function(){
var os=detectOS(),p=PROFILES[os]||PROFILES['Unknown'];
document.getElementById('aaText').innerHTML='<b>Detected system: '+os+'.</b> '+p.note;
document.getElementById('aaList').innerHTML='<b>Your Apply-all set:</b> '+p.applies.join(' &middot; ');
var IDX=null,DET={};
function lvlB(l){l=(l||'').toLowerCase();return l==='critical'?'b-crit':(l==='high'?'b-high':(l==='medium'?'b-med':'b-low'));}
function orgB(o){return o==='documented'?'<span class="badge b-doc">documented</span>':'<span class="badge b-gen">generated</span>';}
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;');}
function recHTML(r){
 var d=DET[r[0]];
 return '<div class="rec" id="r-'+r[0]+'"><h4>'+esc(r[1])+' <span class="badge '+lvlB(r[3])+'">'+esc(r[3])+'</span>'+orgB(r[4])+'</h4>'
 +'<p class="note">'+r[0]+' &middot; '+esc(r[2])+'</p>'
 +(d?'<p class="sol"><b>Vector:</b> '+esc(d.vector)+'</p><p class="sol"><b>Solution:</b> '+esc(d.solution)+'</p><p class="note">'+esc(d.note)+'</p>'
     +'<button class="btn sec" data-dl="'+r[0]+'">&#x2B07; Download the removal steps</button>':'<p class="note">Loading solution&hellip;</p>')
 +'</div>';
}
function needDetails(rows,chunk,done){
 if(rows.every(function(r){return DET[r[0]];})){done();return;}
 fetch('data/addons/details/details-c'+String(chunk).padStart(5,'0')+'.json').then(function(r){return r.json();})
 .then(function(j){Object.keys(j).forEach(function(k){DET[k]=j[k];});done();})
 .catch(function(){done();});
}
function render(filter){
 var box=document.getElementById('azList');box.innerHTML='';
 var rows=IDX.rows.filter(function(r){
  if(!filter)return true;filter=filter.toLowerCase();
  return r[0].toLowerCase().indexOf(filter)>=0||r[1].toLowerCase().indexOf(filter)>=0||r[2].toLowerCase().indexOf(filter)>=0;});
 var byL={};rows.forEach(function(r){var L=(r[1][0]||'#').toUpperCase();(byL[L]=byL[L]||[]).push(r);});
 Object.keys(byL).sort().forEach(function(L){
  var det=document.createElement('details');det.innerHTML='<summary>'+L+' ('+byL[L].length+')</summary>';
  var inner=document.createElement('div');det.appendChild(inner);box.appendChild(det);
  det.addEventListener('toggle',function(){
   if(!det.open||det.dataset.done)return;det.dataset.done='1';
   var chunks={};byL[L].forEach(function(r){(chunks[r[5]]=chunks[r[5]]||[]).push(r);});
   var keys=Object.keys(chunks),i=0;
   (function next(){if(i>=keys.length){paint();return;}
    needDetails(chunks[keys[i]],keys[i],function(){i++;next();});})();
   function paint(){inner.innerHTML=byL[L].map(function(r){return recHTML(r);}).join('');wireDl(inner);}
  });
 });
 if(!Object.keys(byL).length)box.innerHTML='<p class="note">No matches.</p>';
 var m=/[?&]addon=(JAH-AV-\\d{6})/.exec(location.search);
 if(m){var hit=null;IDX.rows.forEach(function(r){if(r[0]===m[1])hit=r;});
  if(hit){needDetails([hit],hit[5],function(){box.innerHTML=recHTML(hit);wireDl(box);});}}
}
function wireDl(root){
 root.querySelectorAll('[data-dl]').forEach(function(b){b.onclick=function(){
  var id=b.getAttribute('data-dl'),d=DET[id];if(!d)return;
  var txt='SIGNATURE ANTIVIRUS - REMOVAL STEPS\\n'+id+' - '+d.name+' ('+d.type+', '+d.level+')\\n'
   +'Origin: '+d.origin+'\\n\\nVECTOR\\n'+d.vector+'\\n\\nSOLUTION\\n'+d.solution+'\\n\\nNOTE\\n'+d.note+'\\n';
  var a=document.createElement('a');a.href=URL.createObjectURL(new Blob([txt],{type:'text/plain'}));
  a.download=id+'-removal-steps.txt';document.body.appendChild(a);a.click();
  setTimeout(function(){URL.revokeObjectURL(a.href);a.remove();},500);};});
}
document.getElementById('aiGo').onclick=function(){
 var q=document.getElementById('aiAsk').value.trim().toLowerCase(),out=document.getElementById('aiOut');
 if(!q){out.textContent='Ask about a virus type — e.g. "ransomware cure".';return;}
 if(!IDX){out.textContent='The archive is still loading — one moment.';return;}
 var hits=IDX.rows.filter(function(r){return r[1].toLowerCase().indexOf(q)>=0||r[2].toLowerCase().indexOf(q)>=0||r[3].toLowerCase().indexOf(q)>=0;}).slice(0,5);
 out.innerHTML=hits.length?('I found '+hits.length+' matching solution'+(hits.length>1?'s':'')+': '+
  hits.map(function(r){return '<b>'+esc(r[1])+'</b> ('+r[0]+')';}).join(', ')+
  '. Open a letter group above to read the full cure.'):'I could not find that in the archive. Try a type like "ransomware", "worm", or "trojan" — every type has a solution profile.';
};
fetch('data/addons/index.json').then(function(r){return r.json();}).then(function(j){
 IDX=j;document.getElementById('docCount').textContent=j.rows.filter(function(r){return r[4]==='documented';}).length;
 document.getElementById('azSearch').addEventListener('input',function(e){render(e.target.value);});
 render('');
 needDetails([['JAH-AV-000029','WannaCry','','','documented',1]],1,function(){wireDl(document.getElementById('bestCard'));});
}).catch(function(){document.getElementById('azList').innerHTML='<p class="note">Archive failed to load.</p>';});
})();</script>
"""

AZ_WELCOME = ("<li><b>Search the cures.</b> Every virus gets its own solution add-on &mdash; documented families and heuristic profiles.</li>"
 "<li><b>Apply all.</b> One button prepares the full protection set for your detected system.</li>"
 "<li><b>Ask the AI.</b> Describe the threat in plain words; it finds the matching solutions.</li>")


def scan_body():
    return """
<div class="hero"><h2>🔎 Free Scan</h2>
<p>Every Signature scan type, free. Drop files here to check them right now, or download the
tools and scan your whole PC — quick, full, custom, USB, startup, or memory.</p>
<p class="freeforever"><b>Free forever.</b> No accounts, no payments, no upsells, no trial traps.
The on-site scan never uploads your files — everything is checked inside your own browser.</p></div>
<div class="osbanner" id="scanOs">Detecting your system&hellip;</div>

<h2>Part 1 — Pick your scan</h2>
<p class="note">Six Signature scan types. The <b>on-site</b> scan checks files you drop below.
The <b>download</b> scans your actual PC — a website cannot do that part, and any site that
claims otherwise is lying to you.</p>
<div class="cards">
<div class="card"><h3>⚡ Signature Quick Scan</h3><p>Downloads, Desktop, Documents, temp folders —
the places infections land first. The everyday check. <b>On-site:</b> drop the files ·
<b>Download:</b> <code>scan --type quick</code></p></div>
<div class="card"><h3>🔍 Signature Full Scan</h3><p>Your entire home folder, file by file.
Thorough; takes a while. <b>Download only:</b> <code>scan --type full</code></p></div>
<div class="card"><h3>🎯 Signature Custom Scan</h3><p>Only the folders or files you name.
<b>On-site:</b> drop exactly those files · <b>Download:</b> <code>scan --type custom --path ~/Downloads</code></p></div>
<div class="card"><h3>🔌 Signature USB Scan</h3><p>Every plugged-in stick, external drive and card —
autorun droppers live here. <b>Download only:</b> <code>scan --type usb</code></p></div>
<div class="card"><h3>🚀 Signature Startup Scan</h3><p>Every program set to auto-start with your system,
checked one by one — the persistence trick malware loves.
<b>Download only:</b> <code>scan --type startup</code></p></div>
<div class="card"><h3>🧠 Signature Memory Scan</h3><p>The program file behind each running process,
checked against the threat database. <b>Download only:</b> <code>scan --type memory</code></p></div>
</div>

<h2>Scan right here — drop your files</h2>
<div class="card" id="dropCard">
<div id="drop" style="border:2px dashed var(--grn);border-radius:12px;padding:34px 18px;text-align:center;cursor:pointer">
<b style="font-size:1.1rem">📁 Drop files here to scan them</b>
<p class="note">or <u>browse</u> — files are fingerprinted (SHA-256) and checked against the
threat database plus disguise heuristics, all inside your browser. Nothing is uploaded.</p>
<input id="filePick" type="file" multiple style="display:none">
</div>
<div id="scanOut" style="margin-top:12px"><p class="note">No files scanned yet.</p></div>
</div>
<p class="note"><b>Honest limits of this page.</b> It can only check files you hand it — it cannot see
the rest of your PC, your USB sticks, your startup entries, or your running programs. For those six
full scan types, download the tools below. That is not a sales pitch; it is how browsers work.</p>

<h2>Clean up</h2>
<div class="cards">
<div class="card"><h3>🧹 On this page</h3><p>Your browser cannot delete or quarantine PC files —
so cleanup here means <b>exact manual steps</b>. Press the button and the AI resolver below
walks you through each finding, step by step.</p>
<button class="btn warn" id="toResolver" type="button">Clean up with the AI resolver ↓</button></div>
<div class="card"><h3>🧹 With the download</h3><p>The real thing: threats quarantined for real,
with your confirmation, journaled so every action can be rewound.</p>
<pre class="cmd">python3 shield_basic.py scan --type full --clean</pre>
<p class="note">Add <code>--yes</code> to skip per-file confirmation. Restore any time:
<code>python3 shield_basic.py restore &lt;id&gt;</code> — or tell Shield “undo”.</p></div>
</div>

<h2>Download the full scanner</h2>
<div class="card"><h3>⬇ Get every scan type for your PC</h3>
<p>One zip per Shield — each runs all six scan types and detects your OS automatically.</p>
<p><a class="btn" href="downloads/signature-shield-ai.zip" download>⬇ AI Defense-Grade (flagship)</a>
<a class="btn sec" href="downloads/signature-shield-basic.zip" download>⬇ Basic</a>
<a class="btn sec" href="downloads/signature-shield-defense.zip" download>⬇ Defense-Grade</a></p>
<p class="note"><b>Every scan type, one command each:</b></p>
<pre class="cmd" id="cmdList">python3 shield_basic.py scan --type quick      # everyday check
python3 shield_basic.py scan --type full       # whole home folder
python3 shield_basic.py scan --type custom --path ~/Downloads   # your pick
python3 shield_basic.py scan --type usb        # sticks, drives, cards
python3 shield_basic.py scan --type startup    # auto-start programs
python3 shield_basic.py scan --type memory     # running programs
python3 shield_basic.py scan --type full --clean   # scan + quarantine (asks first)</pre>
<button class="btn sec" id="copyCmds" type="button">📋 Copy the commands</button>
<p class="note">Defense-Grade adds the behavioral-heuristic overlay on top:
<code>python3 shield_defense.py scan --type full</code></p></div>

<h2 id="aiResolver">Part 2 <span class="note">(optional)</span> — 🤖 AI Scan &amp; Resolver</h2>
<div class="card">
<p>Shield explains your scan in plain language and resolves it with you — on this page over your
dropped-file results, or on your PC inside the download
(<code>python3 shield_ai_defense.py chat</code> → say “full scan”).</p>
<div class="searchrow"><input id="aiScanAsk" type="search"
placeholder="Ask Shield — e.g. “what did you find?” or “my pc is slow”" aria-label="Ask Shield">
<button class="btn" id="aiScanGo" type="button">Ask</button></div>
<div id="aiScanOut" aria-live="polite"><p class="note">Drop files above first, or just describe
what is wrong — slow PC, popups, locked files, strange homepage…</p></div>
</div>
<script>""" + OS_JS + """
(function(){
var os=detectOS(),p=PROFILES[os]||PROFILES['Unknown'];
document.getElementById('scanOs').innerHTML='<b>Free scan — detected system: '+os+'.</b> '+p.note;
var DB=null,SCAN_FINDINGS=[];
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function hex(buf){return Array.prototype.map.call(new Uint8Array(buf),function(b){return ('0'+b.toString(16)).slice(-2);}).join('');}
function dbLoad(){
 if(DB)return Promise.resolve(DB);
 return fetch('tools/signatures.json').then(function(r){return r.json();}).then(function(j){DB=j;return j;});
}
var DOUBLE_EXT=[".pdf.exe",".doc.exe",".docx.exe",".xls.exe",".xlsx.exe",".jpg.exe",".jpeg.exe",".png.exe",".gif.exe",".txt.exe",".zip.exe",".rar.exe",".mp3.exe",".mp4.exe",".scr",".pif",".bat.exe",".cmd.exe",".lnk.exe"];
var RISKY_EXT=[".exe",".scr",".pif",".bat",".cmd",".ps1",".vbs",".msi",".com",".jar"];
function verdictFor(name,digest,db){
 var low=name.toLowerCase(),reasons=[],verdict='CLEAN',cls='b-low';
 var sigs=db.sha256||{},bad=(db.filenames||[]).map(function(n){return n.toLowerCase();});
 if(sigs[digest]){verdict='KNOWN THREAT';cls='b-crit';
  reasons.push('Fingerprint matches the threat database: '+sigs[digest]);}
 if(bad.indexOf(low)>=0){verdict='SUSPICIOUS';cls='b-high';
  reasons.push('Filename is on the known-threat name list.');}
 for(var i=0;i<DOUBLE_EXT.length;i++){
  if(low.slice(-DOUBLE_EXT[i].length)===DOUBLE_EXT[i]){verdict='SUSPICIOUS';cls='b-high';
   reasons.push('Double-extension disguise ('+DOUBLE_EXT[i]+') — pretends to be a document or image but is actually executable. One of the oldest malware tricks.');break;}}
 var ext=low.slice(low.lastIndexOf('.'));
 if(verdict==='CLEAN'&&RISKY_EXT.indexOf(ext)>=0){verdict='CAUTION';cls='b-med';
  reasons.push('It is an executable program, so it *can* change your system. Only run it if you know where it came from.');}
 return {verdict:verdict,cls:cls,reasons:reasons,digest:digest};
}
function renderResults(){
 var box=document.getElementById('scanOut');
 if(!SCAN_FINDINGS.length){box.innerHTML='<p class="note">No files scanned yet.</p>';return;}
 var h='<p><b>'+SCAN_FINDINGS.length+' file(s) checked</b> — inside your browser, nothing uploaded.</p>';
 SCAN_FINDINGS.forEach(function(f,i){
  h+='<div class="rec"><h4>'+esc(f.name)+' <span class="badge '+f.cls+'">'+f.verdict+'</span></h4>';
  h+='<p class="note">SHA-256: <code>'+f.digest.slice(0,24)+'…</code> · '+(f.size/1024).toFixed(1)+' KB</p>';
  if(f.reasons.length)h+='<p class="sol">'+f.reasons.map(function(r){return '• '+esc(r);}).join('<br>')+'</p>';
  else h+='<p class="sol">No threat fingerprints, no known-bad name, no disguise tricks. I cannot promise any file is 100% safe — but nothing about this one worries me.</p>';
  h+='</div>';});
 box.innerHTML=h;
}
function scanFiles(files){
 dbLoad().then(function(db){
  var jobs=[];
  for(var i=0;i<files.length;i++)(function(file){
   jobs.push(file.arrayBuffer().then(function(buf){
    return crypto.subtle.digest('SHA-256',buf).then(function(d){
     var v=verdictFor(file.name,hex(d),db);
     v.name=file.name;v.size=file.size;return v;});}));
  })(files[i]);
  document.getElementById('scanOut').innerHTML='<p class="note">🔎 Fingerprinting '+files.length+' file(s)…</p>';
  Promise.all(jobs).then(function(vs){SCAN_FINDINGS=SCAN_FINDINGS.concat(vs);renderResults();});
 }).catch(function(){document.getElementById('scanOut').innerHTML='<p class="note">Could not load the threat database — check your connection and try again.</p>';});
}
var drop=document.getElementById('drop'),pick=document.getElementById('filePick');
drop.addEventListener('click',function(){pick.click();});
pick.addEventListener('change',function(){if(pick.files.length)scanFiles(pick.files);pick.value='';});
['dragover','dragenter'].forEach(function(ev){drop.addEventListener(ev,function(e){e.preventDefault();drop.style.borderColor='#fff';});});
['dragleave','drop'].forEach(function(ev){drop.addEventListener(ev,function(e){e.preventDefault();drop.style.borderColor='';});});
drop.addEventListener('drop',function(e){var fs=e.dataTransfer.files;if(fs&&fs.length)scanFiles(fs);});
document.getElementById('toResolver').onclick=function(){
 document.getElementById('aiResolver').scrollIntoView({behavior:'smooth'});
 document.getElementById('aiScanAsk').focus({preventScroll:true});};
document.getElementById('copyCmds').onclick=function(){
 var t=document.getElementById('cmdList').textContent;
 if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t);}
 else{var ta=document.createElement('textarea');ta.value=t;document.body.appendChild(ta);ta.select();
  try{document.execCommand('copy');}catch(e){}ta.remove();}};
/* ---- AI Scan & Resolver (on-site): plain-language, grounded in YOUR results ---- */
function aiSay(html){document.getElementById('aiScanOut').innerHTML='<div class="rec"><p class="sol">'+html+'</p></div>';}
function plainWhy(f){
 if(f.verdict==='KNOWN THREAT')return 'its fingerprint is in the threat database — this is a confirmed bad file. Delete it and empty your trash.';
 if(f.verdict==='SUSPICIOUS')return f.reasons[0]+' Treat it as dangerous until proven otherwise.';
 if(f.verdict==='CAUTION')return 'it is a real program. If you did not mean to download it, delete it; if you trust the source, it is your call.';
 return 'it came back clean.';
}
function aiAnswer(q){
 q=(q||'').trim();var ql=q.toLowerCase();
 if(!ql){aiSay('Ask me about your scan results, or describe a symptom — “my pc is slow”, “popups everywhere”, “files are locked”.');return;}
 var bad=SCAN_FINDINGS.filter(function(f){return f.verdict!=='CLEAN';});
 if(/result|found|find|what.*(scan|check)|report|mean/.test(ql)){
  if(!SCAN_FINDINGS.length){aiSay('You have not scanned any files yet — drop some files in the box above and I will explain every result in plain language.');return;}
  if(!bad.length){aiSay('I checked '+SCAN_FINDINGS.length+' file(s) you dropped and every one came back clean — no threat fingerprints, no disguise tricks. The honest caveat: I can only judge the files you handed me, not your whole PC. For the full six scan types, download the tools.');return;}
  var h='Here is what I found in your '+SCAN_FINDINGS.length+' dropped file(s), in plain language:<br><br>';
  bad.forEach(function(f){h+='• <b>'+esc(f.name)+'</b> — flagged <b>'+f.verdict+'</b>: '+esc(plainWhy(f))+'<br>';});
  h+='<br><b>What to do:</b> 1) Do not open the flagged file(s). 2) Delete '+(bad.length>1?'them':'it')+' and empty your trash/recycle bin. 3) If it came by email or download, delete the original message too. 4) Want the deep version? Download the shield and run <code>scan --type full --clean</code> — it quarantines threats for real, with an undo for every action.';
  aiSay(h);return;}
 if(/clean|fix|remove|delete|quarantine|get rid/.test(ql)){
  if(bad.length){
   var h='Cleaning up <b>'+bad.length+'</b> flagged file(s) — exact steps, since this page cannot touch your PC itself:<br><br>';
   bad.forEach(function(f,i){h+=(i+1)+'. Delete <b>'+esc(f.name)+'</b> ('+f.verdict.toLowerCase()+': '+esc(f.reasons[0]||'flagged')+')<br>';});
   h+='<br>Then: empty your trash/recycle bin, restart your browser, and run the downloaded full scan to make sure nothing else is hiding: <code>python3 shield_basic.py scan --type full --clean</code>. Every cleanup there is journaled — say “undo” to reverse anything.';
   aiSay(h);return;}
  aiSay('Nothing to clean — your dropped files came back clean'+(SCAN_FINDINGS.length?'':' (and none have been scanned yet)')+'. If something still feels wrong, describe the symptom and I will walk you through it.');return;}
 var KB=[
  [/slow|lag|freez|crawl/, 'A slow PC has boring causes far more often than viruses: too many startup programs, a full disk, or an old spinning hard drive. <b>Do this:</b> 1) Restart (not sleep — restart). 2) Uninstall programs you do not recognize. 3) Check free disk space — under 10% free will choke any system. 4) Then download the shield and run <code>scan --type startup</code> to see everything auto-starting, and <code>scan --type memory</code> to check what is running right now.'],
  [/popup|pop-up|ads|advert/, 'Popups everywhere usually means adware — a browser hijacker or a shady extension, not a deep virus. <b>Do this:</b> 1) Remove browser extensions you did not install yourself. 2) Reset your browser homepage and search engine. 3) Clear site data. 4) Run <code>scan --type quick</code> on the download to catch the dropper.'],
  [/ransom|locked|encrypt|bitcoin|pay.*(file|decrypt)/, 'Locked/encrypted files with a ransom note is ransomware — act fast and <b>do not pay</b>: 1) Disconnect from the internet right now. 2) Do NOT delete the note — it identifies the strain. 3) Restore your files from a clean backup. 4) The archive has the WannaCry-class cure pattern; the Shield tripwires (honeypots) exist to catch the next one early. If there is no backup, say so and I will walk you through identification.'],
  [/homepage|redirect|search.*(chang|hijack)|toolbar/, 'A changed homepage or search redirect is a browser hijacker. <b>Do this:</b> 1) Remove unknown extensions. 2) Set your homepage/search back manually. 3) Check installed programs for anything installed the day it started and remove it. 4) Run <code>scan --type startup</code> — hijackers love auto-start entries.'],
  [/email|phish|scam.*(email|message)|suspicious.*(link|attach)/, 'Do not click it and do not open the attachment. <b>Do this:</b> 1) Delete the message. 2) If you already clicked, disconnect and run <code>scan --type full --clean</code>. 3) Change the password of any account you typed into that page, from a clean device. Forward the phish to your email provider\u2019s report address if it has one.'],
  [/boot|start.*(slow|fail)|blue screen|bsod|cras/, 'Boot trouble is usually drivers, disk errors, or a bad update — not always malware. <b>Do this:</b> 1) Boot into Safe Mode and see if it behaves. 2) Undo the most recent change (update, new program). 3) Run <code>scan --type startup</code> from Safe Mode to audit auto-start entries. If Safe Mode is also broken, say so — that changes the plan.']];
 for(var i=0;i<KB.length;i++){if(KB[i][0].test(ql)){aiSay(KB[i][1]);return;}}
 aiSay('I can explain your dropped-file results (“what did you find?”), walk you through cleanup (“clean it up”), or diagnose a symptom — try “my pc is slow”, “popups everywhere”, or “files are locked”. On your PC, Shield itself does all of this conversationally: <code>python3 shield_ai_defense.py chat</code>.');
}
document.getElementById('aiScanGo').onclick=function(){aiAnswer(document.getElementById('aiScanAsk').value);};
document.getElementById('aiScanAsk').addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();aiAnswer(e.target.value);}});
})();</script>
"""

SCAN_WELCOME = ("<li><b>Scan free.</b> Drop files to check them right now — fingerprints plus "
 "disguise heuristics, all inside your browser, nothing uploaded.</li>"
 "<li><b>Six scan types.</b> Quick, full, custom, USB, startup, memory — on-site for dropped "
 "files, or download the tools for the full PC versions.</li>"
 "<li><b>Clean up + AI resolver.</b> Exact manual steps here, real quarantine in the download, "
 "and Shield explains every finding in plain language.</li>")
