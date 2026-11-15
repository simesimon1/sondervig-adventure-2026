# Prüfung der ersten Entwicklungsphase

## Ausgangszustand

Ausgangscommit `3c501f546a03239825bf5c89920665ea7b77ed06`. Lokaler statischer HTTP-Server, Chromium auf Linux mit SwiftShader. v0.13 wurde gestartet: Status „122 Wege · 227 Gebäude · 65 freie Dünenflächen“, keine JavaScript-Ausnahmen. Für den Vorher-Screenshot wurde die unveränderte Three.js-Moduldatei lokal auf die CDN-URL gemappt. Das alte v0.10-Spiel wurde ebenfalls geöffnet, ohne JavaScript-Ausnahmen.

## Automatisierte Prüfungen

Ergebnis des lokalen Laufs am 15.11.2026: **7/7 Node-Tests bestanden; alle 5 Browserkonfigurationen bestanden.** In 20.437 gerenderten Straßendreiecken wurden keine Mittelpunkte innerhalb von Gebäuden gefunden. Straßen-Vertices stimmen mit der Geländehöhe plus 0,045 m bis auf numerische Rundung überein. Keine JavaScript-Ausnahmen oder fehlgeschlagenen Ressourcenanforderungen in den geprüften neuen Szenen. Die beiden bisherigen Einstiege wurden ebenfalls erfolgreich geprüft.

`npm test`: sieben Tests für den unveränderten OSM-Bestand und gemeinsame Knoten, orientierte Dachgeometrie, ebene Fundamente/Straßenkorridore, Interpolation auf Geländedreiecken, Bewegung mit Unterteilung und Wandgleiten, konkave Kollisionsumrisse sowie Flächenausschnitt an Gebäuden.

`python3 tests/browser_smoke.py`: wiederholbare Browserprüfung über den HTTP-Server. Screenshots und ein JSON-Protokoll werden außerhalb des öffentlichen Repositories abgelegt. Der Test prüft:

- Desktop-Tastatur, Kamerarichtung, Mausorbit, Mausrad, Kamerarücksetzung und Fokusverlust.
- Hauskollision über tatsächliche Tastatureingabe, Fahrzeugkollision, Bodenbindung auf Dünen, Muschelaufnahme und Einmaligkeit der Interaktion.
- Gerenderte Straßenflächen: Dreiecksmittelpunkte außerhalb der Gebäudeflächen, Vertices auf gemeinsamer Geländeoberfläche plus 4,5 cm Abstand.
- Touchgrößen 390 × 844, 412 × 915, 820 × 1180 sowie 844 × 390: gleichzeitiger Joystick und Kamera, Zwei-Finger-Zoom/Pan, Touch-Abbruch und losgelassene Eingaben, Hilfe, Qualitätswechsel und erreichbare Bedienelemente.
- Alte Einstiege: v0.10-Startknopf und neue Verlinkung; OSM-Testkarte lädt weiterhin 122/227 Elemente.

Die Browserdatei wird bewusst nicht als automatischer Hardware-/Safari-Nachweis bezeichnet. Der PR-Workflow führt nur Node-Tests und Modulsyntaxprüfungen aus; der lokale Browserlauf ist gesondert dokumentiert.

Während der Prüfung behoben: Kamerafokus lag zunächst im Gebäude; die erste Ansicht fokussiert jetzt die freie Spielfigur. Das Schattenkamera-Projektionsfenster wird nach seiner Konfiguration aktualisiert. Im Smartphone-Querformat fing eine gestreckte Navigationsfläche Kameraberührungen ab; sie liegt jetzt begrenzt am unteren Rand. Fokusverlust und Touch-Abbruch setzen Eingaben zurück. Nach Zwei-Finger-Pan passt sich die Fokus-Höhe auch wieder nach unten an; beim Fokussieren eines Gebäudes wird die Kamera nicht in dessen Innenraum gezogen.

## Grenzen und manuelle Freigabe

Keine physischen Android-, iPhone-, iPad- oder Windows-Geräte verfügbar. WebKit/Safari war zunächst nicht installiert. Keine behaupteten Smartphone-FPS, Akkumessungen oder Netzladezeiten. Die neue Szene benötigt rund 1,5 MB unkomprimierte Kernressourcen einschließlich Three.js und OSM; keine zusätzlichen Foto-/Modell-Downloads. Draw Calls und Dreieckszahlen variieren mit Kamerawinkel, Entfernung und Qualitätsstufe. Für ein Zielgerät sind reale Messungen weiterhin erforderlich.

Vor dem Merge auf mindestens einem echten Touchgerät prüfen: Spaziergang mit zweitem Kamerafinger, Pinch/Pan, Appwechsel/Zurückkehren, Bildschirmdrehung, Haus- und Autokollision, Dünenboden und Aktionstaste. Danach auf Safari/iPad und Windows nachziehen. Aussehen und Adresse des Ferienhauses sowie echte Höhen/Dachrichtung brauchen belastbare, nicht private Referenzen. Der PR selbst deployt nicht nach GitHub Pages.
