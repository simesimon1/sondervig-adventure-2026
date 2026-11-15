# Søndervig Adventure 2026

Browserbasiertes Familienabenteuer mit Three.js. Bestehendes Spiel: **v0.10** (`index.html`). OSM-Testkarte: **v0.11.2**. Die bisherige OSM-3D-Vorschau v0.13 wird in Phase 1 zu einer begehbaren **v0.14** weiterentwickelt.

## Figurenprototyp v0.15

Diese Entwicklungsbranch baut auf der v0.14 aus PR #1 auf. Neu sind eigene GLB-Modelle von Simon, Swantje und Ida nach den Charakterkarten, Skelettanimationen, ein separates Figurenatelier und eine erste Material-/Lichtüberarbeitung. [Umfang und Grenzen](docs/phase-2-characters.md) · [Modellherkunft](assets/characters/README.md).

`character-studio.html` bietet Ganzkörper-/Gesichtsansicht und Stand-/Gehanimation. Im Spiel über `?` → „Figurenatelier öffnen“. Die Modelle sind ein erster stilisierter Entwurf; der Detailgrad der Referenzkarten ist noch nicht erreicht. Private Vorlagen sind nicht enthalten. Simons Größe bleibt nach dem ursprünglichen Auftrag 1,88 m, trotz der abweichenden Angabe auf seiner Karte.

## Phase 1 starten

```sh
python3 -m http.server 8000
```

Dann <http://localhost:8000/osm-3d-preview.html> öffnen. Oder über die neue Schaltfläche im Startbildschirm des bisherigen Spiels einsteigen. Kein Build, keine Installation von npm-Paketen, kein API-Schlüssel erforderlich. `file://` funktioniert wegen ES-Modulen und JSON-Fetch nicht.

Auf GitHub Pages liegt der Abschnitt nach einem geprüften Merge unter `https://simesimon1.github.io/sondervig-adventure-2026/osm-3d-preview.html`. Eine Entwicklungsbranch wird **nicht** automatisch als Pages-Vorschau veröffentlicht. Vor dem Merge lokal oder über einen separaten statischen Testserver testen.

## Was in Phase 1 spielbar ist

- Ein begrenzter Bereich von 420 × 360 lokalen Metern um den bisherigen Startpunkt, mit 108 dargestellten OSM-Gebäuden. Der vollständige Snapshot mit **122 Wegen und 227 Gebäuden** bleibt erhalten.
- Gebäudegrundrisse mit daran ausgerichteten Satteldächern, Giebeln, Holzfassaden, Fenstern, Tür, Rahmen und Sockeln. Details werden in der Entfernung ausgeblendet.
- Kontinuierliches Dünengelände mit geglätteten Übergängen zu Hausfundamenten und Straßen; Strandhafer als instanzierte Geometrie.
- Simon (1,88 m), Swantje (1,87 m) und Ida (1,05 m) als eigene animierte GLB-Entwürfe. Keine vorgeblich vorhandenen Familienmodelle oder privaten Fotos.
- Gehen relativ zur Kamera, Kollisionen gegen Gebäudegrundrisse, geparktes Auto und Swantje. Bodenhöhe entspricht den tatsächlich gerenderten Geländedreiecken.
- Gespräche und sechs Muscheln als kleine Suchaufgabe; der Zähler gilt für die aktuelle Sitzung.
- Sparsame Grafik für Touchgeräte, optional höhere Qualität mit dynamischen Schatten. Three.js 0.160.1 wird für diesen Abschnitt lokal mitgeliefert.

Das Auto ist in diesem Abschnitt noch nicht fahrbar. Weitere Familienmitglieder, Ladenbesuche, Küstenlinie, Strand und Ausflugsmissionen werden hier noch nicht umgesetzt. Das bisherige Spiel mit seinen bestehenden Inhalten bleibt separat erreichbar.

## Steuerung

| Eingabe | Funktion |
| --- | --- |
| WASD / Pfeiltasten | relativ zur Kamerablickrichtung gehen |
| Virtuellen Joystick ziehen | gehen, gleichzeitig ist Kameradrehung möglich |
| Linke Maustaste ziehen / ein Finger auf der Welt | Kamera drehen und neigen |
| Mausrad / zwei Finger auseinander oder zusammen | zoomen |
| Zwei Finger gemeinsam verschieben | Ansicht verschieben |
| E / Aktion | sprechen, untersuchen, Muschel aufnehmen |
| Zur Figur | Kamera zur Figur zurücksetzen |
| Überblick | OSM-Umgebung von oben ansehen |
| Grafik | Automatisch → Sparsam → Hoch |
| ? | Hilfe und Hinweise zur Kartengenauigkeit |

## Daten und Genauigkeit

Ausgangspunkt bleibt der bisherige Marker bei 56.11246784 / 8.12092021. Das nächstliegende Gebäude ist OSM-Way **696149108**. **Im Snapshot sind keine Adressen enthalten; die Zuordnung dieses Gebäudes zu Harbo Stages Vej 3 / Esmark i6582 ist unbestätigt.** Es ist ein vorläufiges Ferienhausmodell, keine verifizierte Rekonstruktion des Mietobjekts.

OSM liefert Gebäudeumrisse und Straßenverläufe. Dachrichtung wird aus dem längsten Maß eines orientierten Grundrissrechtecks abgeleitet. Höhen, Dachneigungen, Fassaden, Straßenbreiten, Geländehöhen, Vegetation sowie Figuren, Auto und Muscheln sind Näherungen bzw. Spielobjekte. Die lokale Grundhöhe von 1,2 ist **kein** Bezug zu Meereshöhe. Es gibt keine importierten Höhen-, Küstenlinien- oder Luftbilddaten. Es werden keine geografisch exakten Dünen oder Grundstücksausstattungen behauptet.

Kartendaten: **© [OpenStreetMap-Mitwirkende](https://www.openstreetmap.org/copyright)**, verfügbar unter der [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/). Der unveränderte Quelldatensatz liegt in `data/sondervig-osm.json`, Datenstand 2026-11-14T17:02:51Z. Abgeleitete Kartendarstellungen behalten die Attribution. Three.js: MIT, siehe `vendor/THREE-LICENSE.txt`.

## Tests

```sh
npm test
```

Node.js 22 oder neuer, ohne Abhängigkeiten. Zusätzlich zu den sieben Weltgeometrieprüfungen gibt es sieben Prüfungen für GLB-Struktur, eigenständige Texturen, Höhe, Skinning, Animationsschleifen und Dateibudgets. Geprüft werden OSM-Knoten und Anzahlen, gedrehte Dächer, ebene Fundamente und Straßenkorridore, Geländehöhen, Kollisionen einschließlich schneller Bewegung sowie das Ausschneiden von Gebäudeumrissen aus Straßenflächen. Der neue PR-Workflow führt diese Tests und Syntaxprüfungen aus. Er veröffentlicht nichts und verändert keine OSM-Daten.

Für die automatisierte Browserprüfung: Python mit `playwright`, Chromium, laufender HTTP-Server:

```sh
python3 tests/browser_smoke.py
python3 tests/characters_browser.py
# Optional: CHROMIUM_PATH=/pfad/zu/chromium GAME_URL=http://localhost:8000
# Screenshots und report.json: /tmp/sondervig-browser-checks
```

Der Test verwendet Chromium mit Touch- und Viewport-Simulation für Desktop, zwei Smartphone-Größen, Tablet und Querformat. Er prüft echte Pointer-/Touch-Ereignisse, gleichzeitiges Gehen und Kameradrehen, Pinch/Pan, Abbruch, Tastatur/Maus, Kollisionen, Bodenhöhe, Interaktion, Straßenflächen, Hilfe und die bisherigen Einstiege. **Das ist kein Hardwaretest und kein Nachweis für Safari/iOS oder Windows.** Siehe [Testprotokoll](docs/phase-1-validation.md) und [Repository-Analyse](docs/repository-audit.md).

Vor Freigabe auf echten Geräten prüfen: iPhone/iPad mit Safari, Android mit Chrome und Windows mit Edge/Chrome; mindestens einmal drehen, zoomen, gleichzeitig gehen und drehen, an Haus und Auto entlanggehen, Muschel aufnehmen und zwischen Hochformat/Querformat wechseln. Im Browser-Performancepanel Bildrate und Ladezeit auf dem Zielgerät erfassen. Belastbare Smartphone-FPS sind noch nicht gemessen.

## Dateien und Deployment

| Pfad | Zweck |
| --- | --- |
| `index.html` | bisheriges v0.10-Spiel; nur Einstiegslink ergänzt |
| `osm-preview.html` | bisherige 2D/Extrusions-Testkarte, unverändert |
| `osm-3d-preview.html`, `src/game.css` | Oberfläche für Phase 1 |
| `src/game.js` | Three.js-Szene, Eingaben, Animation, Interaktionen |
| `src/world.js` | Projektion, Grundrisse, Geländehöhen, räumlicher Index, Kollisionen |
| `src/scenery.js` | Material-/Geometrieerzeugung, LOD, instanzierter Strandhafer |
| `data/sondervig-osm.json` | bestehender, unveränderter OSM-Snapshot |
| `.github/workflows/import-osm.yml` | bestehender OSM-Import, unverändert |

GitHub Pages verwendet das bestehende statische Projekt ohne zusätzliche Buildschritte. Alle neuen Ressourcenpfade sind relativ und funktionieren unter dem Repository-Unterpfad. Entwicklung ausschließlich auf `dev/phase-1-coastal-playground`, Prüfung per Pull Request gegen `main`; kein Merge oder Produktionsdeployment durch diese Entwicklungsphase.
