// app.js - X-iNet Filter Engine (Stabilisierte Version)
let rawData = [];

// Diese Funktion ermittelt den korrekten Pfad zu den Daten, 
// egal ob lokal oder auf GitHub Pages
function getBasePath() {
    const isGitHubPages = window.location.hostname.includes('github.io');
    return isGitHubPages ? '/inetfilterlist/output/' : '../../output/';
}

async function init() {
    document.getElementById('whitelist-input').value = localStorage.getItem('xinet_whitelist') || '';
    
    // Event-Listener fuer Slider und Auswahl
    document.getElementById('limit-slider').addEventListener('input', (e) => {
        document.getElementById('limit-value').innerText = e.target.value;
        updateUI();
    });
    document.getElementById('whitelist-input').addEventListener('input', updateUI);
    document.getElementById('format-select').addEventListener('change', updateUI);
    document.getElementById('generate-btn').addEventListener('click', downloadFile);

    // Erst Status, dann Daten laden
    await loadStatus();
    await loadData();
}

async function loadStatus() {
    try {
        const r = await fetch(getBasePath() + 'status.json');
        if (!r.ok) throw new Error("Status-Datei nicht erreichbar");
        const d = await r.json();
        
        // Statistiken setzen
        document.getElementById('brutto-count').innerText = (d.metadata.brutto || 0).toLocaleString('de-DE');
        document.getElementById('netto-count').innerText = (d.metadata.netto || 0).toLocaleString('de-DE');
        document.getElementById('last-update').innerText = d.metadata.timestamp || '--:--';
        
        // Kategorien dynamisch aufbauen
        const catContainer = document.getElementById('dynamic-categories');
        const statusList = document.getElementById('source-status-list');
        catContainer.innerHTML = ''; 
        statusList.innerHTML = '';

        const uniqueCats = [...new Set(d.sources.map(s => s.category))];
        uniqueCats.forEach(cat => {
            catContainer.innerHTML += `
                <label style="display:block; margin-bottom:5px; cursor:pointer;">
                    <input type="checkbox" class="cat-cb" value="${cat}" checked onchange="updateUI()"> ${cat.toUpperCase()}
                </label>`;
        });

        d.sources.forEach(s => {
            statusList.innerHTML += `<div><span class="status-indicator status-${s.status}"></span> ${s.name}: ${s.count.toLocaleString('de-DE')}</div>`;
        });
    } catch(e) { 
        console.error("Status-Fehler:", e);
        document.getElementById('source-status-list').innerHTML = '<p style="color:red;">Fehler: status.json konnte nicht geladen werden.</p>';
    }
}

async function loadData() {
    try {
        const r = await fetch(getBasePath() + 'xinet_data.json');
        if (!r.ok) throw new Error("Daten-Datei nicht erreichbar");
        rawData = await r.json();
        updateUI();
    } catch(e) { 
        console.error("Daten-Fehler:", e);
        document.getElementById('preview-area').innerText = "Fehler: xinet_data.json konnte nicht geladen werden.";
    }
}

function updateUI() {
    if (rawData.length === 0) return;

    const limit = parseInt(document.getElementById('limit-slider').value);
    const activeCats = Array.from(document.querySelectorAll('.cat-cb:checked')).map(cb => cb.value);
    const whitelistText = document.getElementById('whitelist-input').value;
    localStorage.setItem('xinet_whitelist', whitelistText);
    const whitelist = whitelistText.split('\n').map(s => s.trim().toLowerCase()).filter(s => s !== "");

    // Filterung
    const filtered = rawData.filter(item => activeCats.includes(item.c) && !whitelist.includes(item.d)).slice(0, limit);
    document.getElementById('live-counter').innerText = filtered.length.toLocaleString('de-DE');

    // Direkt-Link Anzeige
    const format = document.getElementById('format-select').value;
    const RAW_BASE = "https://raw.githubusercontent.com/albertuszerk/inetfilterlist/main/output/";
    const files = {
        flint2: "xinet_flint2_adguard.txt",
        mikrotik: "xinet_mikrotik.rsc",
        fritzbox: "xinet_fritzbox.txt",
        hosts: "xinet_universal_hosts.txt",
        pihole: "xinet_pihole.txt",
        dnsmasq: "xinet_dnsmasq.conf",
        unbound: "xinet_unbound.conf"
    };
    document.getElementById('direct-link-display').innerText = RAW_BASE + (files[format] || "");

    // Vorschau (Preview)
    renderPreview(filtered, format);
}

function renderPreview(data, format) {
    const max = 15;
    let text = `--- Vorschau (${format.toUpperCase()}) ---\n`;
    data.slice(0, max).forEach(i => {
        if (format === 'flint2') text += `||${i.d}^\n`;
        else if (format === 'mikrotik') text += `add address=127.0.0.1 name="${i.d}"\n`;
        else if (format === 'hosts') text += `0.0.0.0 ${i.d}\n`;
        else text += `${i.d}\n`;
    });
    if (data.length > max) text += "...";
    document.getElementById('preview-area').innerText = text;
}

function downloadFile() {
    const format = document.getElementById('format-select').value;
    const activeCats = Array.from(document.querySelectorAll('.cat-cb:checked')).map(cb => cb.value);
    const whitelist = document.getElementById('whitelist-input').value.split('\n').map(s => s.trim().toLowerCase()).filter(s => s !== "");
    const limit = parseInt(document.getElementById('limit-slider').value);

    const data = rawData.filter(item => activeCats.includes(item.c) && !whitelist.includes(item.d)).slice(0, limit);
    
    let content = "";
    if (format === 'mikrotik') content = "/ip dns static\n";
    
    data.forEach(i => {
        if (format === 'flint2') content += `||${i.d}^\n`;
        else if (format === 'mikrotik') content += `add address=127.0.0.1 name="${i.d}"\n`;
        else if (format === 'hosts') content += `0.0.0.0 ${i.d}\n`;
        else content += `${i.d}\n`;
    });

    const blob = new Blob([content], {type: 'text/plain'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = "xinet_export.txt";
    a.click();
    URL.revokeObjectURL(url);
}

window.addEventListener('DOMContentLoaded', init);