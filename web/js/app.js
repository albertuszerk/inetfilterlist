// app.js - Die intelligente Steuerzentrale

let globalDomainData = []; // Hier speichern wir die Rohdaten nach dem Laden

async function initApp() {
    await loadStatus();
    await loadRawData();
}

// 1. Status und Ampeln laden
async function loadStatus() {
    try {
        const response = await fetch('../output/status.json');
        const data = await response.json();

        document.getElementById('brutto-count').innerText = data.metadata.total_processed_brutto.toLocaleString('de-DE');
        document.getElementById('netto-count').innerText = data.metadata.total_unique_netto.toLocaleString('de-DE');
        document.getElementById('last-update').innerText = data.metadata.timestamp;

        const statusList = document.getElementById('source-status-list');
        statusList.innerHTML = '';
        data.sources.forEach(source => {
            const div = document.createElement('div');
            div.style.padding = "5px 0";
            div.innerHTML = `<span class="status-indicator status-${source.status}"></span> 
                             <strong>${source.name}</strong>: ${source.count.toLocaleString('de-DE')} Eintraege`;
            statusList.appendChild(div);
        });
    } catch (e) { console.error("Status-Fehler", e); }
}

// 2. Die Rohdaten fuer die Filter-Engine laden
async function loadRawData() {
    try {
        const response = await fetch('../output/xinet_data.json');
        globalDomainData = await response.json();
        console.log("Daten-Engine bereit. " + globalDomainData.length + " Domains geladen.");
    } catch (e) { console.error("Daten-Fehler", e); }
}

// 3. Die eigentliche "Innovations-Maschine": Datei generieren
function generateFilterFile() {
    const whitelist = document.getElementById('whitelist-input').value
                        .split('\n')
                        .map(d => d.trim().toLowerCase())
                        .filter(d => d.length > 0);

    // In diesem Prototyp filtern wir einfach gegen die Whitelist
    // Spaeter koennen wir hier noch die Kategorien-Logik verfeinern
    let filteredList = globalDomainData.filter(domain => !whitelist.includes(domain));

    // Format waehlen (Wir nutzen hier als Beispiel das Flint 2 / AdGuard Format)
    let outputContent = "! Title: Individueller X-iNet Filter\n! Erstellt am: " + new Date().toLocaleString() + "\n";
    filteredList.forEach(domain => {
        outputContent += `||${domain}^\n`;
    });

    // Download ausloesen
    const blob = new Blob([outputContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'mein_xinet_filter.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

document.getElementById('generate-btn').addEventListener('click', generateFilterFile);
window.addEventListener('DOMContentLoaded', initApp);