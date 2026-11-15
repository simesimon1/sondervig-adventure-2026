# Bestandsaufnahme vor Phase 1

Untersucht am 15.11.2026. Bestätigtes öffentliches Repository: `simesimon1/sondervig-adventure-2026`, Defaultbranch `main`, Ausgangscommit **3c501f546a03239825bf5c89920665ea7b77ed06**. Sauberer Checkout; keine vorbestehenden lokalen Änderungen oder AGENTS.md-Dateien. Alle sechs vorhandenen Dateien einschließlich Workflow und JSON-Struktur wurden untersucht. Die Entwicklungsbranch wurde vor Quelländerungen angelegt.

## Bestand und Architektur

- `README.md`: bislang nur Repositoryname.
- `index.html`: monolithisches v0.10-Spiel, Three.js 0.160.1 über CDN als globales Script. Eigene Geometrie, kein Framework/Build/Assetpipeline. Vereinfachte, nicht maßstabsgetreue Welten für Søndervig, Ringkøbing und Blåvand; Familienplatzhalter, Gespräche, Auto, Reisen, Muschelzähler, localStorage, Minikarte, Steuerkreuz und Kamera. Doris/Lena erscheinen im alten Spiel nach fünf Muscheln; dieses Verhalten wird in Phase 1 nicht erweitert.
- `osm-preview.html`: v0.11.2, ES-Modul über CDN, lokale JSON-Datei, projizierte Wege und extrudierte Grundrisse, Marker, Orbit/Pinch und Wiederholen-Schaltfläche. Von der Spielwelt unabhängig.
- `osm-3d-preview.html`: tatsächlicher letzter Stand **v0.13**, nicht v0.12. Three.js 0.160.1 als ES-Modul; gespeicherte OSM-Daten, Dächer, dekorative Düneninseln, Strandhaferkegel. Funktionierende Kamera: ein Finger/Mouse-Drag Orbit, zwei Finger Pinch und Pan, Mausrad, Zoomknöpfe und Zentrieren. Keine Spielfigur, keine Kollisionen oder Interaktionen.
- `data/sondervig-osm.json`: 177.989 Bytes, Overpass-JSON mit **349 Ways**: 122 `highway`, 227 `building`. Datenstand 2026-11-14T17:02:51Z. Ways mit Geometrie und teilweise OSM-Node-IDs; kein separater Node-Katalog. Gemeinsame Koordinaten reichen für deckungsgleiche Wegeknoten. Einige vollständige Ways reichen über die Import-Bounding-Box hinaus.
- `.github/workflows/import-osm.yml`: manueller Import oder Push einer Workflowänderung; drei Overpass-Server als Fallback, Query nur Gebäude und Straßen in 56.1099/8.1158 bis 56.115/8.126. Schreibt und committet den Snapshot auf die jeweilige ausgecheckte Branch. Kein Lauf wird in Phase 1 ausgelöst, da diese Datei nicht geändert wird.

Keine Modelle, Fotos, Texturdateien, Familienbildvorlagen, Höhenmodelle, Küstenlinien oder weiteren Quelldateien vorhanden. Sieben Gebäude haben ein `roof:shape=gabled`-Tag; keine Gebäude enthalten `addr:*`-Tags. Aus dem Startmarker lässt sich deshalb keine bestätigte Adresse ableiten.

## Pages und Actions

Es gibt keinen eingecheckten Pages-Deployment-Workflow. GitHub zeigt den dynamischen Workflow `pages build and deployment` für `main`; der jüngste Lauf [43620477896](https://github.com/simesimon1/sondervig-adventure-2026/actions/runs/43620477896) für den Ausgangscommit war erfolgreich. Das ist der beobachtete statische Pages-Build, kein Beleg für gelesene Administrationseinstellungen. Der erfolgreiche [OSM-Import 43618797726](https://github.com/simesimon1/sondervig-adventure-2026/actions/runs/43618797726) gehört zum vorhergehenden Importstand. Es gibt keine bestehende Test-/Buildkonfiguration im Checkout.

Der neue PR-Check ist ein eigener, nur lesender Workflow. Pages- und Importdateien bleiben bestehen. Die neuen Module brauchen weder npm-Installation noch Bundler; relative URLs erhalten den GitHub-Pages-Unterpfad.

## Identifizierte Fehlerquellen

1. **Falsche Dachorientierung:** v0.13 extrudiert korrekte Grundrisse, baut Dächer aber über deren achsenparallele Bounding-Box. Gedrehte und konkave Häuser erhalten überstehende oder unpassende Dächer. Fenster/Türen liegen ebenfalls an der Weltachse statt an der Fassade.
2. **Getrennte Bodengeometrie:** Straßen sind flache Boxsegmente bei fester Höhe, Dünen einzelne aufgesetzte Meshes. Es gibt keine gemeinsame Höhenfunktion, keine Neigungserkennung und keine Bodenbindung für eine Figur. Abstandskreise vermeiden manche Überschneidungen, bilden jedoch weder Grundstücke noch tatsächliche Dünen ab.
3. **Wegeverbindungen:** unverbundene Rechtecksegmente hinterlassen an Kurven spitze Lücken oder überbreite Ecken. Straßenklassen/Breiten werden grob zusammengefasst; Gebäudeschneidungen sind nicht geprüft.
4. **Kollisionen:** OSM-Vorschau ohne Kollisionen. Im alten Spiel nur achsenparallele Rechtecke, keine Fahrzeuge/NPCs, kein Gelände. Eine harte Z-Grenze bei -14,2 blockiert den Zugang zu den bei -17 bis -28 platzierten Muscheln. Diese Altspiel-Probleme werden dokumentiert, aber nicht in einer parallelen Umgestaltung des v0.10-Spiels bearbeitet.
5. **Eingaben:** die OSM-Kamera ist brauchbar und wird beibehalten; `lostpointercapture` und Fokusverlust können jedoch hängende Eingaben verursachen. Im alten Spiel fehlen Mausrad und Zwei-Finger-Pan; seine vorhandene Steuerung bleibt separat bestehen.
6. **Darstellung/Performance:** Lambert-Flächen ohne Texturen/Schatten, geometrisch vereinfachte Dünen, viele separate Meshes/Materialien und zufällige Landschaft im Altspiel. Keine einheitliche Objektverwaltung oder LOD-Strategie.
7. **Externe Abhängigkeit:** alle bisherigen Seiten brauchen ein CDN. Phase 1 liefert dieselbe Three.js-Version samt MIT-Lizenz lokal aus; die alten Seiten werden nicht grundlos auf eine neue Abhängigkeit umgestellt.

## Entscheidung für Phase 1

Weiterentwicklung der vorhandenen OSM-3D-Vorschau, kein Enginewechsel und kein Neubeginn des Projekts. Die kleine Oberfläche wird lesbar auf HTML/CSS/JS-Module verteilt. Weltkoordinaten und OSM-Snapshot bleiben unverändert. Der spielbare Detailbereich wird begrenzt, Gebäudedetails erhalten LOD, Straßen werden gebündelt, Vegetation instanziert und nach Entfernung ausgeblendet. Entwicklung und Begutachtung per separater Branch/PR. Die Rollen von Doris/Lena werden für diesen Abschnitt nicht festgelegt.
