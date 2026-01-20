// app.js - Die interaktive Filter-Engine

let rawData = []; // Die Basis-Daten mit Kategorien

async function init() {
    await loadStatus();
    await loadData();
    // Whitelist aus dem Speicher laden
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
            list.innerHTML += `<div style="margin-bottom:5px;"><span class="status-indicator status-${s.status}"></span> ${s.name}: ${s.count.toLocaleString('de-DE')}</div>`;
        });
    } catch(e) { console.error("Status konnte nicht geladen werden."); }
}

async function loadData() {
    try {
        const r = await fetch('../../output/xinet_data.json');
        rawData = await r.json();
        console.log("Engine geladen: " + rawData.length + " Domains.");
    } catch(e) { console.error("Daten-Engine Fehler."); }
}

function generate() {
    const activeCats = [];
    if(document.getElementById('cat-sex').checked) activeCats.push('sex');
    if(document.getElementById('cat-violence').checked) activeCats.push('violence');
    if(document.getElementById('cat-vpn').checked) activeCats.push('vpn_proxy');
    if(document.getElementById('cat-gambling').checked) activeCats.push('gambling');

    const whitelist = document.getElementById('whitelist-input').value.split('\n').map(s => s.trim().toLowerCase()).filter(s => s !== "");
    localStorage.setItem('xinet_whitelist', document.getElementById('whitelist-input').value);

    // Filter-Prozess
    const filtered = rawData.filter(item => activeCats.includes(item.c) && !whitelist.includes(item.d));

    // Format-Wahl (Beispiel Flint 2)
    let content = "! X-iNet Individueller Filter\n! Erstellt: " + new Date().toLocaleString() + "\n";
    filtered.forEach(item => {
        content += `||${item.d}^\n`;
    });

    // Download
    const blob = new Blob([content], {type: 'text/plain'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'mein_xinet_filter.txt';
    a.click();
}

document.getElementById('generate-btn').addEventListener('click', generate);
window.addEventListener('DOMContentLoaded', init);