// app.js - Die innovative Filter-Engine

let rawData = [];

async function init() {
    await loadStatus();
    await loadData();
    // Whitelist-Gedaechtnis aus dem Browser-Speicher
    document.getElementById('whitelist-input').value = localStorage.getItem('xinet_whitelist') || '';
}

async function loadStatus() {
    try {
        const r = await fetch('../../output/status.json');
        const d = await r.json();
        document.getElementById('brutto-count').innerText = d.metadata.brutto.toLocaleString('de-DE');
        document.getElementById('netto-count').innerText = d.metadata.netto.toLocaleString('de-DE');
        document.getElementById('last-update').innerText = d.metadata.timestamp;
        
        const list = document.getElementById('source-status-list');
        list.innerHTML = '';
        d.sources.forEach(s => {
            list.innerHTML += `<div><span class="status-indicator status-${s.status}"></span> ${s.name}: ${s.count.toLocaleString('de-DE')}</div>`;
        });
    } catch(e) { console.error("Status-Ladefehler"); }
}

async function loadData() {
    try {
        const r = await fetch('../../output/xinet_data.json');
        rawData = await r.json();
        console.log("Engine bereit: " + rawData.length + " Domains.");
    } catch(e) { console.error("Daten-Ladefehler"); }
}

function generate() {
    const activeCats = [];
    if(document.getElementById('cat-sex').checked) activeCats.push('sex');
    if(document.getElementById('cat-violence').checked) activeCats.push('violence');
    if(document.getElementById('cat-vpn').checked) activeCats.push('vpn_proxy');
    if(document.getElementById('cat-gambling').checked) activeCats.push('gambling');

    const whitelistStr = document.getElementById('whitelist-input').value;
    localStorage.setItem('xinet_whitelist', whitelistStr);
    const whitelist = whitelistStr.split('\n').map(s => s.trim().toLowerCase()).filter(s => s !== "");

    // 1. Filtern
    const filtered = rawData.filter(item => activeCats.includes(item.c) && !whitelist.includes(item.d));

    // 2. Formatieren basierend auf Dropdown
    const format = document.getElementById('format-select').value;
    let content = "";
    let fileName = "xinet_filter.txt";

    if (format === 'flint2') {
        content = "! X-iNet Filter fuer Flint 2\n";
        filtered.forEach(i => content += `||${i.d}^\n`);
    } else if (format === 'mikrotik') {
        content = "/ip dns static\n";
        filtered.forEach(i => content += `add address=127.0.0.1 name="${i.d}"\n`);
        fileName = "xinet_mikrotik.rsc";
    } else if (format === 'hosts') {
        content = "# Universal HOSTS\n";
        filtered.forEach(i => content += `0.0.0.0 ${i.d}\n`);
    } else {
        // Standard: Reine Liste (Fritzbox / Pi-hole)
        filtered.forEach(i => content += `${i.d}\n`);
    }

    // 3. Download ausloesen
    const blob = new Blob([content], {type: 'text/plain'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    a.click();
}

document.getElementById('generate-btn').addEventListener('click', generate);
window.addEventListener('DOMContentLoaded', init);