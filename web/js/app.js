// app.js - X-iNet Filter Engine (Final Robust Version)
let rawData = [];
const BASE_RAW_URL = "https://raw.githubusercontent.com/albertuszerk/inetfilterlist/main/output/";

const FORMAT_FILES = {
    flint2: "xinet_flint2_adguard.txt",
    mikrotik: "xinet_mikrotik.rsc",
    fritzbox: "xinet_fritzbox.txt",
    hosts: "xinet_universal_hosts.txt",
    pihole: "xinet_pihole.txt",
    dnsmasq: "xinet_dnsmasq.conf",
    unbound: "xinet_unbound.conf"
};

async function init() {
    document.getElementById('whitelist-input').value = localStorage.getItem('xinet_whitelist') || '';
    
    document.getElementById('limit-slider').addEventListener('input', (e) => {
        document.getElementById('limit-value').innerText = e.target.value;
        updateUI();
    });
    document.getElementById('whitelist-input').addEventListener('input', updateUI);
    document.getElementById('format-select').addEventListener('change', updateUI);
    document.getElementById('generate-btn').addEventListener('click', downloadFile);

    await loadStatus();
    await loadData();
}

async function loadStatus() {
    try {
        const r = await fetch('../output/status.json');
        if (!r.ok) throw new Error("Status nicht gefunden");
        const d = await r.json();
        
        // Stats befuellen (beachtet beide moeglichen Key-Varianten)
        document.getElementById('brutto-count').innerText = (d.metadata.total_processed_brutto || d.metadata.brutto || 0).toLocaleString('de-DE');
        document.getElementById('netto-count').innerText = (d.metadata.total_unique_netto || d.metadata.netto || 0).toLocaleString('de-DE');
        
        const catContainer = document.getElementById('dynamic-categories');
        const statusList = document.getElementById('source-status-list');
        catContainer.innerHTML = ''; 
        statusList.innerHTML = '';

        const uniqueCats = [...new Set(d.sources.map(s => s.category.toUpperCase()))];
        uniqueCats.forEach(cat => {
            catContainer.innerHTML += `<label style="display:block; margin: 5px 0; cursor:pointer;">
                <input type="checkbox" class="cat-cb" value="${cat}" checked onchange="updateUI()"> ${cat}
            </label>`;
        });

        d.sources.forEach(s => {
            statusList.innerHTML += `<div><span class="status-indicator status-${s.status}"></span> ${s.name}: ${s.count.toLocaleString('de-DE')}</div>`;
        });
    } catch(e) { 
        console.error("Status-Ladefehler", e);
    }
}

async function loadData() {
    try {
        const r = await fetch('../output/xinet_data.json');
        if (!r.ok) throw new Error("Daten nicht gefunden");
        rawData = await r.json();
        updateUI();
    } catch(e) { 
        console.error("Daten-Ladefehler", e);
        document.getElementById('preview-area').innerText = "Warte auf Synchronisation der xinet_data.json...";
    }
}

function updateUI() {
    if (rawData.length === 0) return;

    const limit = parseInt(document.getElementById('limit-slider').value);
    // Wir holen die ausgewaehlten Kategorien in GROSSBUCHSTABEN
    const activeCats = Array.from(document.querySelectorAll('.cat-cb:checked')).map(cb => cb.value.toUpperCase());
    
    const whitelistText = document.getElementById('whitelist-input').value;
    localStorage.setItem('xinet_whitelist', whitelistText);
    const whitelist = whitelistText.split('\n').map(s => s.trim().toLowerCase()).filter(s => s !== "");

    // Filterung: Beachtet Gross-/Kleinschreibung beim Vergleich
    const filtered = rawData.filter(item => 
        activeCats.includes(item.c.toUpperCase()) && !whitelist.includes(item.d.toLowerCase())
    ).slice(0, limit);
    
    document.getElementById('live-counter').innerText = filtered.length.toLocaleString('de-DE');

    const format = document.getElementById('format-select').value;
    document.getElementById('direct-link-display').innerText = BASE_RAW_URL + (FORMAT_FILES[format] || "");

    renderPreview(filtered, format);
}

function renderPreview(data, format) {
    const max = 15;
    let text = `--- Vorschau (${format.toUpperCase()}) ---\n`;
    if (data.length === 0) {
        text += "(Keine Domains fuer diese Auswahl gefunden - pruefe die Checkboxen)";
    } else {
        data.slice(0, max).forEach(i => {
            if (format === 'flint2') text += `||${i.d}^\n`;
            else if (format === 'mikrotik') text += `add address=127.0.0.1 name="${i.d}"\n`;
            else if (format === 'hosts') text += `0.0.0.0 ${i.d}\n`;
            else if (format === 'dnsmasq') text += `address=/${i.d}/\n`;
            else if (format === 'unbound') text += `local-zone: "${i.d}" always_nxdomain\n`;
            else text += `${i.d}\n`;
        });
        if (data.length > max) text += "...";
    }
    document.getElementById('preview-area').innerText = text;
}

function downloadFile() {
    const format = document.getElementById('format-select').value;
    const activeCats = Array.from(document.querySelectorAll('.cat-cb:checked')).map(cb => cb.value.toUpperCase());
    const whitelist = document.getElementById('whitelist-input').value.split('\n').map(s => s.trim().toLowerCase()).filter(s => s !== "");
    const limit = parseInt(document.getElementById('limit-slider').value);

    const data = rawData.filter(item => 
        activeCats.includes(item.c.toUpperCase()) && !whitelist.includes(item.d.toLowerCase())
    ).slice(0, limit);
    
    let content = "";
    if (format === 'mikrotik') content = "/ip dns static\n";
    data.forEach(i => {
        if (format === 'flint2') content += `||${i.d}^\n`;
        else if (format === 'mikrotik') content += `add address=127.0.0.1 name="${i.d}"\n`;
        else if (format === 'hosts') content += `0.0.0.0 ${i.d}\n`;
        else if (format === 'dnsmasq') content += `address=/${i.d}/\n`;
        else if (format === 'unbound') content += `local-zone: "${i.d}" always_nxdomain\n`;
        else content += `${i.d}\n`;
    });

    const blob = new Blob([content], {type: 'text/plain'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = FORMAT_FILES[format] || "xinet_filter.txt";
    a.click();
    URL.revokeObjectURL(url);
}

window.addEventListener('DOMContentLoaded', init);