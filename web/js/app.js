// app.js - Kern-Logik ohne Vorschau-Ballast
let rawData = [];
const BASE_RAW_URL = "https://raw.githubusercontent.com/albertuszerk/inetfilterlist/main/output/";

const FORMAT_FILES = {
    hosts: "xinet_universal_hosts.txt",
    flint2: "xinet_flint2_adguard.txt",
    mikrotik: "xinet_mikrotik.rsc",
    fritzbox: "xinet_fritzbox.txt",
    pihole: "xinet_pihole.txt",
    dnsmasq: "xinet_dnsmasq.conf",
    unbound: "xinet_unbound.conf",
    rpz: "xinet_rpz.zone"
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
        const response = await fetch('../output/status.json?v=' + Date.now());
        const data = await response.json();
        
        const b = data.metadata.brutto || data.metadata.total_processed_brutto || 0;
        const n = data.metadata.netto || data.metadata.total_unique_netto || 0;
        
        document.getElementById('brutto-count').innerText = b.toLocaleString('de-DE');
        document.getElementById('netto-count').innerText = n.toLocaleString('de-DE');
        
        const catContainer = document.getElementById('dynamic-categories');
        const statusList = document.getElementById('source-status-list');
        catContainer.innerHTML = ''; statusList.innerHTML = '';

        const uniqueCats = [...new Set(data.sources.map(s => s.category.toLowerCase()))];
        uniqueCats.forEach(cat => {
            catContainer.innerHTML += `
                <label style="display:block; margin: 5px 0; cursor:pointer;">
                    <input type="checkbox" class="cat-cb" value="${cat}" checked onchange="updateUI()"> ${cat.toUpperCase()}
                </label>`;
        });

        data.sources.forEach(s => {
            statusList.innerHTML += `<div><span class="status-indicator status-${s.status}"></span> ${s.name}: ${s.count.toLocaleString('de-DE')}</div>`;
        });
    } catch(e) { console.error("Status-Ladefehler", e); }
}

async function loadData() {
    try {
        const response = await fetch('../output/xinet_data.json?v=' + Date.now());
        rawData = await response.json();
        console.log("Daten-Check: " + rawData.length + " Eintraege geladen.");
        updateUI();
    } catch(e) { console.error("Daten-Ladefehler", e); }
}

function updateUI() {
    const format = document.getElementById('format-select').value;
    document.getElementById('direct-link-display').innerText = BASE_RAW_URL + (FORMAT_FILES[format] || "");
}

function downloadFile() {
    if (!rawData || rawData.length === 0) { alert("Daten werden noch geladen..."); return; }
    
    const limit = parseInt(document.getElementById('limit-slider').value);
    const activeCats = Array.from(document.querySelectorAll('.cat-cb:checked')).map(cb => cb.value.toLowerCase());
    const whitelist = document.getElementById('whitelist-input').value.split('\n').map(s => s.trim().toLowerCase()).filter(s => s !== "");
    const format = document.getElementById('format-select').value;

    const filtered = rawData.filter(item => {
        const category = (item.c || item.category || "").toLowerCase();
        const domain = (item.d || item.domain || "").toLowerCase();
        return activeCats.includes(category) && !whitelist.includes(domain);
    }).slice(0, limit);
    
    let content = "";
    if (format === 'mikrotik') content = "/ip dns static\n";
    else if (format === 'flint2') content = "! X-iNet Filter\n";

    filtered.forEach(i => {
        const d = i.d || i.domain;
        if (format === 'flint2') content += `||${d}^\n`;
        else if (format === 'mikrotik') content += `add address=127.0.0.1 name="${d}"\n`;
        else if (format === 'hosts') content += `0.0.0.0 ${d}\n`;
        else if (format === 'dnsmasq') content += `address=/${d}/\n`;
        else if (format === 'unbound') content += `local-zone: "${d}" always_nxdomain\n`;
        else content += `${d}\n`;
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