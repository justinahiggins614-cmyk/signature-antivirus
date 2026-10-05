
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
<div class="stat"><b>2</b><span>protection downloads</span></div>
<div class="stat"><b>100% free</b><span>no accounts, ever</span></div>
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
<div class="card"><h3>3 &middot; Run</h3><p><code>python3 shield_basic.py scan ~/Downloads</code> — that is the whole
signup flow. One universal download detects your OS and applies the matching protection automatically.</p></div>
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
<p class="note"><b>Honest scope.</b> These are real, working tools with real capabilities, described exactly as
they behave. They do not replace your operating system's built-in protections — on macOS they coexist with
Gatekeeper and XProtect; on Windows they complement Windows Security. The starter signature database ships the
industry-standard EICAR test marker so you can verify detection yourself on day one.</p>
<script>""" + OS_JS + """
(function(){var os=detectOS(),p=PROFILES[os]||PROFILES['Unknown'];
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
One universal download detects your system automatically and applies the matching profile.</p></div>
<div class="osbanner" id="osBanner2">Detecting your system&hellip;</div>
<div class="cards">
<div class="card"><h3>🛡️ Signature Shield Basic</h3>
<p><b>The classic suite, Signature-style.</b> SHA-256 signature scanning against the Signature threat database,
quarantine with one-command restore, scheduled scans, and known-bad filename detection
(double extensions like <code>invoice.pdf.exe</code>).</p>
<p class="note">Ships with the industry-standard EICAR test marker in its database, so you can prove
detection works the day you install it.</p>
<a class="btn" href="tools/shield_basic.py" download>⬇ Download shield_basic.py</a>
<a class="btn sec" href="tools/signatures.json" download>⬇ Threat database</a>
<pre class="cmd">python3 shield_basic.py --self-test   # prove it works
python3 shield_basic.py scan ~/Downloads --quarantine</pre></div>
<div class="card"><h3>🛡️⚔️ Signature Shield Defense-Grade</h3>
<p><b>The advanced arsenal.</b> Behavioral-heuristic scanner, firewall-rules <i>generator</i> for your exact OS,
USB autorun guard, ransomware honeypot tripwires, boot/auto-start auditor, and network monitor —
with <code>apply-all</code> running the whole profile in one command.</p>
<p class="note">The generator writes the rules; <b>you</b> review and apply them. Nothing is changed silently.</p>
<a class="btn" href="tools/shield_defense.py" download>⬇ Download shield_defense.py</a>
<pre class="cmd">python3 shield_defense.py --self-test
python3 shield_defense.py apply-all   # full profile for your OS</pre></div>
</div>
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
 "<li><b>Download, don't subscribe.</b> Two real Python tools. They detect your OS at runtime, automatically.</li>"
 "<li><b>Prove it works.</b> Every tool ships <code>--self-test</code>; the database ships the EICAR test marker.</li>")

def addons_body(n):
    return """
<div class="hero"><h2>The 1 Million Add-On Archive</h2>
<p>A specific solution for <b>every virus</b> &mdash; documented historic families plus heuristic defense profiles,
marching to one million. Search for a threat, open its cure, or press <b>Apply all</b>.</p></div>
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
