<p align="center">
  <img src="/images/banner01.png" alt="X-iNet Multi-Format Filter Pipeline" width="100%">
</p>

# X-iNet Multi-Format Filter Pipeline

**Die X-iNet Multi-Format Filter Pipeline ist wie ein unsichtbarer Schutz-Schild fuer dein Internet zu Hause. Sie sammelt automatisch Listen mit schlechten Webseiten und sorgt dafuer, dass dein Router diese blockiert, damit alle in der Familie sicher im Netz surfen koennen.**

## 🚀 Der Live-Konfigurator (GUI)
Hier koennen Sie den Filter einstellen, Ausnahmen hinzufuegen und die Blackliste fuer den Router kopieren/runterladen:
👉 **[https://albertuszerk.github.io/inetfilterlist/web/](https://albertuszerk.github.io/inetfilterlist/web/)**

---

## 1. Wer wir sind
Dieses Projekt ist eine Zusammenarbeit zwischen einem Entwickler und einer intelligenten Maschine.
* **Autor:** Albertus Zerk
* **KI-Partner:** Gemini (Google AI)

---

## 2. Warum wir das tun (fuer Vaeter, Muetter, Kinder und Jugendliche)
Das Internet ist toll, aber es gibt dort viele Dinge, die Kinder nicht sehen sollten – wie Gewalt oder schlechte Filme. Wir haben dieses System gebaut, um Eltern die Kontrolle zurueckzugeben. Es hilft uns, Leitplanken zu setzen, damit unsere Kinder die guten Seiten des Internets nutzen koennen, waehrend die schlechten draussen bleiben.

---

## 3. Die wichtigsten Vorteile
* **Kluge Auswahl:** Das System weiss, welche Webseiten wichtig sind und welche nur den Router bremsen wuerden.
* **Flint 2 Power:** Alles ist extra fuer den **GL.iNet GL-MT6000 (Flint 2)** Router optimiert.
* **Immer bereit:** Auch wenn mal ein Server ausfaellt, arbeitet der Schutz einfach weiter.
* **Deine Regeln:** Mit der "Whitelist" kannst du Webseiten, die du magst (wie Facebook), sofort wieder erlauben.
* **Schoene Zahlen:** Alle Mengenangaben nutzen das klare Format mit dem Hochkomma (z. B. **1'000**).

---

## 4. Bilder-Galerie
Hier siehst du, wie das System aussieht und wie es funktioniert:

| | | |
| :--- | :--- | :--- |
| ![Bild 1: Quellen](/images/screen07.png) | ![Bild 2: Daten Export](/images/screen11.png) | ![Bild 3: Daten Limiter und Screen](/images/screen09.png) |
| ![Bild 4: X-iNet Multi-Format Filter Pipeline](/images/screen12.png) | ![Bild 5: Datenquellen und Priorisierung](/images/screen06.png) | ![Bild 6: Unterstuetzte Router](/images/screen02.png) |

---

## 5. So funktioniert der Trick (Der Boost)
Damit die wichtigsten Filter-Seiten immer ganz oben in der Liste stehen, geben wir ihnen einen riesigen Punkte-Vorsprung von **950'000** Plaetzen. So fliegen die schlechten Seiten garantiert nicht aus der Liste raus.

$$Rang_{neu} = \max(1, Rang_{alt} - 950'000)$$

---

## 6. Wo der Filter nicht helfen kann: Tor-Netzwerk
Kein Filter ist perfekt. Es gibt ein Programm namens **Tor**, das den Internetverkehr versteckt. Da Tor einen eigenen geheimen Tunnel baut, kann unser Filter nicht hineinsehen und dort auch nichts blockieren. Eltern sollten wissen, dass Kinder mit dem Tor-Browser diesen Filter umgehen koennten.

---

## 7. Starten mit GitHub Codespaces und Weiterentwicklung
Du kannst das ganze System direkt in GitHub starten, ohne etwas auf deinem Computer zu installieren:
1. Klicke auf `Code` -> `Codespaces` -> `Create codespace`.
2. Tippe im schwarzen Fenster unten: `python main.py`.
3. Alle fertigen Dateien liegen danach im Ordner `/output`.

---

## 8. Den Router verbinden (Flint 2)
Du kannst deinen **GL.iNet Flint 2** Router direkt mit diesem System verbinden.
* **Direkt-Link:** `https://raw.githubusercontent.com/albertuszerk/inetfilterlist/main/output/xinet_flint2.hosts`
* **Info:** Der Flint 2 kann locker **150'000** Webseiten auf einmal blockieren.

---

## 9. Die Intelligenz hinter der Filter-Pipeline
Wir untersuchen ueber **5'800'000** Webseiten (Stand 2026) und suchen die wichtigsten fuer dich heraus.

---

## 10. Wie werden die "wichtigsten" Webseiten berechnet?
Die technische Basis fuer diese Auswahl bildet das **Tranco-Ranking**. Dies ist ein hochpräzises Ranking, das die Beliebtheit von Domains ueber einen Zeitraum von 30 Tagen mittelt. Dabei werden Daten aus verschiedenen Quellen (wie z.B. Cisco Umbrella, Majestic und Alexa) kombiniert, um ein stabiles und manipulationssicheres Abbild des weltweiten Datenverkehrs zu erhalten.

**Die Logik dahinter:**
* **Aggregiertes Ranking:** Anstatt nur einer Quelle zu vertrauen, nutzt die Pipeline einen gewichteten Durchschnitt, um kurzfristige Verzerrungen zu vermeiden.
* **Der Limiter-Effekt:** Ueber den **Ranking-Limit-Slider** im Dashboard legst du stufenlos fest, bis zu welcher Position (z.B. Top 80'000) Webseiten als "vertrauenswuerdig" eingestuft oder von Filtern ausgenommen werden.
* **Ressourcen-Optimierung:** Da die Hardware deines Routers Höchstleistungen erbringen muss, sorgt dieses Ranking dafuer, dass die Filter-Pipeline nur dort ansetzt, wo es wirklich nötig ist.

### Effizienz vs. Listenlänge: Warum weniger oft mehr ist
Ein häufiges Missverständnis bei DNS-Filtern ist, dass eine längere Liste automatisch besseren Schutz bietet. Die **X-iNet Filter Pipeline** nutzt intelligente Priorisierung:

* **Fokus-Effekt:** Durch das Ranking werden Bedrohungen auf den meistbesuchten Webseiten priorisiert.
* **Performance-Boost:** Eine Liste mit nur **1'000 hochrelevanten Einträgen** deckt die "Autobahnen" des Internets ab, auf denen sich 99% des Familien-Traffics bewegen.
* **Effizienz-Vergleich:** Theoretisch kann es diese optimierte Kurzliste mit ungefilterten Listen von 150'000 Einträgen aufnehmen, ohne die CPU deines Routers unnoetig zu belasten.
* **Zielgerichteter Schutz:** Du sparst Speicherplatz fuer "verlassene Waldwege" des Webs und behältst die volle Geschwindigkeit deines Netzwerks bei.

| Kategorie | Kapazitaet | Was es macht |
| :--- | :--- | :--- |
| **Flint 2 (Plain)** | [max. 150'000] | Schnellster Schutz fuer deinen Router. |
| **Universal HOSTS** | [max. 1'000'000+] | Passt fast ueberall. |
| **AdGuard Home** | [max. 200'000] | Blockiert Werbung sehr gut. |

---

## 11. Integration & Direkt-Link fuer Router
Um diese Intelligenz ohne komplizierte Umwege nutzbar zu machen, generiert das System einen **Direkt-Link**. Dieser Link ist so aufbereitet, dass dein Router ihn unmittelbar verstehen und die gefilterten Daten verarbeiten kann. Damit entfällt das manuelle Sortieren von Listen – die Pipeline liefert das fertige Ergebnis direkt an dein Ziel-System.

---
*Stand: 22. Januar 2026 – Gemeinsam fuer ein sicheres Internet.*
