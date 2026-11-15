# Figuren- und Materialprototyp v0.15

Aufbauend auf PR #1 / `ddf3ba22cccd905c847348aaa3989e3247436449`. Separate Branch `dev/phase-2-character-style`; `main`, PR #1 und die veröffentlichte v0.14 bleiben erhalten.

## Umsetzung

- Drei neu erzeugte, tatsächlich vorhandene GLB-Modelle mit 18 Knochen und Idle-/Walk-Animationen: Simon, Swantje, Ida. Entwurf nach den im Chat gelieferten Charakterkarten; Herkunft und Grenzen in `assets/characters/README.md`.
- Simon bleibt steuerbarer Spieler; Swantje und Ida stehen als interaktive NPCs beim Startpunkt und besitzen Kollisionen. Karten sind Designvorgaben, keine als Texturen verwendeten Fotos.
- Kleiner lokaler glTF-Lader passend zu Three.js 0.160.1, ohne CDN-/Decoder-Abhängigkeit. Bei einem fehlgeschlagenen Modell-Download bleibt die Szene mit erkennbar gekennzeichneter Ersatzfigur spielbar.
- `character-studio.html`: Ganzkörper-/Gesichtsansicht, drehbare Figur, Wechsel zwischen den drei Figuren und Stand-/Gehanimation, auch mit Touch.
- Generiertes Reflexionslicht, Himmel, dezente Oberflächenreliefs für Holz/Sand/Dach sowie gekrümmte, leicht bewegte Strandhaferblätter. Kontaktschatten bleiben auch im sparsamen Grafikmodus sichtbar.
- Bestehende Steuerung, OSM-Projektion, Grundrisse, Gelände- und Straßenhöhen sowie Spielfigurenkollisionen weiterverwendet.

## Lokal prüfen

Den vorhandenen statischen Server verwenden; `osm-3d-preview.html` startet die Szene. Über `?` → „Figurenatelier öffnen“ zur Nahansicht. Alternativ `character-studio.html` direkt öffnen. Browserbesucher der separaten Pages-Testversion brauchen keine Installation.

`npm test` führt Geometrie-/Bewegungstests sowie GLB-Struktur-, Höhen-, Gewichtungs-, Animations- und Budgetprüfungen aus. `python3 tests/browser_smoke.py` prüft weiterhin die eigentliche Steuerung auf mehreren Viewports. `python3 tests/characters_browser.py` prüft die Integration der Modelle, Figurenatelier und Ersatzfigur bei unterbrochenem Modellabruf.

Blender wird nur zur erneuten Erstellung der Modelle gebraucht:

```sh
blender --background --factory-startup --python tools/build-characters.py
```

## Grenzen

Stilisierter erster Modell- und Animationsdurchgang. Keine Unreal-Engine-Qualität oder Übereinstimmung mit der Detailtreue der Charakterkarten behauptet. Tilda und weitere Familienmitglieder noch nicht modelliert. Keine neuen behaupteten geografischen Details. Keine neue Bestätigung der Hausadresse oder echten Geländehöhen. Noch keine Hardwaremessung von Android/iOS-Bildraten; Software-WebGL dient der Funktionsprüfung, nicht als Smartphone-Benchmark.

## Durchgeführte lokale Prüfung

Am 15.11.2026 bestanden: 14/14 Node-Tests, fünf Bildschirmkonfigurationen des bestehenden Browser-Smoke-Tests, sechs Figuren-/Höhen-/Animationsprüfungen in Desktop- und Smartphone-Ansicht sowie der simulierte Ausfall einer GLB-Datei. Modulsyntax und unveränderte OSM-Geometrie ebenfalls geprüft. Die Browser laufen auf Linux/SwiftShader; dies ist kein Nachweis einer bestimmten Bildrate auf echten Mobilgeräten.
