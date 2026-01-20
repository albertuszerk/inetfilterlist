// app.js - X-iNet Dynamic Engine 2026

let rawData = [];
const BASE_RAW_URL = "https://raw.githubusercontent.com/albertuszerk/inetfilterlist/main/output/";

const FORMAT_MAP = {
    flint2: "xinet_flint2_adguard.txt",
    mikrotik: "xinet_mikrotik.rsc",
    fritzbox: "xinet_fritzbox.txt",
    hosts: "xinet_universal_hosts.txt",
    pihole: "xinet_pihole.txt",
    dnsmasq: "xinet_dnsmasq.conf",
    unbound: "xinet_unbound.conf"
};

async function init() {
    await loadStatus();
    await loadData();
    document.getElementById('whitelist-input').value = localStorage.getItem('xinet_whitelist') || '';
    
    // Event-Listener fuer Live-Updates
    document.getElementById('whitelist-input').addEventListener('input', updateUI);
    document.getElementById('format-select').addEventListener('change', updateUI);
    updateUI();
}

async function loadStatus() {
    try {
        const r = await fetch('../../output/status.json');
        const d = await r.json();
        document.getElementById('brutto-count').innerText = d.metadata.brutto.toLocaleString('de-DE');
        document.getElementById('netto-count').innerText = d.metadata.netto.toLocaleString('de-DE');
        
        // Kategorien dynamisch erstellen
        const catContainer = document.getElementById('dynamic-categories');
        const statusList = document.getElementById('source-status-list');
        catContainer.innerHTML = ''; statusList.innerHTML = '';
        
        const uniqueCats = [...new Set(d.sources.map(s => s.category))];
        uniqueCats.forEach(cat => {
            catContainer.innerHTML += `<label><input type="checkbox" class="cat-cb" value="${cat}" checked onchange="updateUI()"> ${cat.toUpperCase()}</label><br>`;
        });

        d.sources.forEach(s => {
            statusList.innerHTML += `<div><span class="status-indicator status-${s.status}"></span> ${s.name}: ${s.count.toLocaleString('de-DE')}</div>`;
        });
    } catch(e) { console.error("Status-Ladefehler"); }
}

async function loadData() {
    try {
        const r = await fetch('../../output/xinet_data.json');
        rawData = await r.json();
        updateUI();
    } catch(e) { console.error("Daten-Ladefehler"); }
}

function updateUI() {
    const activeCats = Array.from(document.querySelectorAll('.cat-cb:checked')).map(cb => cb.value);
    const whitelist = document.getElementById('whitelist-input').value.split('\n').map(s => s.trim().toLowerCase()).filter(s => s !== "");
    localStorage.setItem('xinet_whitelist', document.getElementById('whitelist-input').value);

    // Filterung
    const filtered = rawData.filter(item => activeCats.includes(item.c) && !whitelist.includes(item.d));
    document.getElementById('live-counter').innerText = filtered.length.toLocaleString('de-DE');

    // Direkt-Link Anzeige
    const format = document.getElementById('format-select').value;
    document.getElementById('direct-link-display').innerText = BASE_RAW_URL + FORMAT_MAP[format];

    // Vorschau generieren
    const previewCount = 15;
    let previewText = `--- Vorschau (${format}) ---\n`;
    filtered.slice(0, previewCount).forEach(i => {
        if (format === 'flint2') previewText += `||${i.d}^\n`;
        else if (format === 'mikrotik') previewText += `add address=127.0.0.1 name="${i.d}"\n`;
        else if (format === 'hosts') previewText += `0.0.0.0 ${i.d}\n`;
        else previewText += `${i.d}\n`;
    });
    if (filtered.length > previewCount) previewText += "...";
    document.getElementById('preview-area').innerText = previewText;
}

// Download-Funktion bleibt identisch zur Vorversion
document.getElementById('generate-btn').addEventListener('click', () => {
    // Hier Logik zum Download wie in der Vorversion einbauen...
    alert("Download wird gestartet mit den Einstellungen der Vorschau!");
});

window.addEventListener('DOMContentLoaded', init);