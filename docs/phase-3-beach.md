# v0.16 – erster Strandspaziergang

Aufbauend auf PR #2, separate Branch `dev/phase-3-beach-walk`. Bestehende Veröffentlichungen und main werden nicht verändert.

## Quellen und Genauigkeit

Der bisherige Datensatz `data/sondervig-osm.json` bleibt bytegleich erhalten. Ergänzend wurden am 16.11.2026 über die öffentliche OSM-API abgerufen:

- `data/coast-osm.json`: Küstenlinie Way 4125293. Quelle: https://api.openstreetmap.org/api/0.6/map?bbox=8.100,56.100,8.118,56.125 . Die Linie hat hier lange geradlinige Abschnitte; sie beschreibt weder aktuellen Wasserstand noch eine vermessene Strandkante.
- `data/coast-paths.json`: vier Wege einschließlich der westlichen Fortsetzung von Harbo Stages Vej. Quelle: https://api.openstreetmap.org/api/0.6/map?bbox=8.103,56.110,8.118,56.114 . Gemeinsame Koordinaten werden für die Route verwendet; die letzte kurze Strecke über den Sand ist frei begehbarer Spielbereich, kein zusätzlich behaupteter OSM-Weg.

© OpenStreetMap-Mitwirkende, ODbL 1.0. Quellen-URLs und Abrufdatum stehen auch in den Dateien. `src/coast.js` enthält die daraus projizierte Küstenlinie. Gelände, Vegetation, Wellen und Muschelpositionen sind künstlerische Ergänzungen. Kein Höhenmodell und keine geografische Exaktheit behauptet. Die Esmark-Seite ließ sich nicht abrufen (HTTP 403); die Zuordnung des Hauses zu i6582 bleibt unbestätigt.

## Spielablauf

Mit Swantje sprechen → den Wegpunkten nach Westen folgen → Strand erreichen → drei Muscheln über E/Aktion aufnehmen → zum Ferienhaus zurückkehren und E/Aktion drücken. Eine Richtungsanzeige zeigt den nächsten Wegpunkt. Das Wasser ist kein Schwimmbereich; Bewegung wird an der Uferzone begrenzt. Fortschritt und freie Spielerposition werden in einem eigenen versionierten localStorage-Eintrag gespeichert. Bei gesperrtem Speicher bleibt die Mission spielbar und zeigt den fehlenden Speicherzugriff an. Über Hilfe kann der Spaziergang neu begonnen werden.

Der Spielbereich reicht nun bis zur Küste. Figurengrößen und bestehende Steuerung bleiben erhalten. Simon erhält feinere Haarbüschel im bestehenden Modellgenerator. Die grundsätzliche Gesichtstopologie bleibt ein stilisierter Prototyp.

## Tests

`npm test`: Welt- und Modellprüfungen, Reihenfolge der Missionsschritte, eindeutiges Sammeln, ungültige Speicherstände und Wegprüfung entlang der gesamten verbundenen OSM-Route einschließlich Kollisions-/Geländeschritten.

`python3 tests/beach_browser.py`: vollständige Mission in Smartphone-Viewport, echte Touch-Ereignisse für gleichzeitiges Gehen/Drehen, Speicherung/Neuladen und Abschluss am Haus. Teleports beschleunigen im Browsertest die Wegstrecke; deren vollständige Begehbarkeit prüft separat der Node-Test. Keine Behauptung einer händisch gespielten kompletten Strecke oder echter Geräte-/FPS-Tests.
