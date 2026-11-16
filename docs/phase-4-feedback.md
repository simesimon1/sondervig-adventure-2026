# v0.17 – Tempoauswahl und erste Referenzkorrektur am Haus

Ausgangsstand: v0.16, Benutzer hat die Mission abgeschlossen, Wege wiedererkannt und keine Kollisionen bemängelt. Wunsch: manuell wählbare Beschleunigungsstufen; gesamte Optik weiterhin zu blockhaft, fehlende Hausdetails und unzureichende Charakterähnlichkeit.

## Tempo

Normal 3,2 m/s, Mittel 6,4 m/s, Schnell 9,6 m/s. Die höheren Werte sind bewusst Spielbeschleunigungen, keine behaupteten realistischen Laufleistungen. Auswahl über drei gleichzeitig sichtbare Tasten oder PC-Tasten 1/2/3, gespeichert getrennt vom Missionsstand. Kurze weiche Übergänge; Kollisionsunterteilung bleibt aktiv. Animationsgeschwindigkeit wird begrenzt angepasst.

## Hausquelle

Esmark: https://esmark.de/ferienhaus-i6582/ (Recherche 16.11.2026), Außenfoto https://img.svc.esmark.dk/images/lodgings/Feriehus-i6582-467658.jpg . Das Foto wurde nur lokal zur Analyse betrachtet, nicht ins öffentliche Repository kopiert oder als Textur verwendet.

Die Seite bestätigt i6582 als Harbo Stages Vej 3. Der genaue Abgleich mit OSM-Way 696149108 bleibt unbestätigt. Sichtbare Merkmale des Fotos: dunkle horizontale Holzfassade, große Glasöffnungen, dunkle Rahmen, Dachüberstand/-rinne, Satellitenschüssel, Terrassenpflaster und Sitzmöbel. Der neue Entwurf übernimmt diese Merkmale mit eigenen Geometrien, echten Öffnungen/Rezessierung und genäherter Anordnung. Gartenrasen ist eine künstlerische Flächenzuordnung, keine vermessene Parzelle.

Die in der Beschreibung genannten weiteren Gartenelemente (Spielturm, Trampolin, Shelter, Sauna) sind noch nicht vollständig nachgebaut. Es werden weder maßstäbliche Genauigkeit noch eine fertige Rekonstruktion behauptet. Möbel sind im Kollisionssystem registriert; Türen bleiben vorerst ohne betretbaren Innenraum. Der Innenraum hinter den Fenstern ist eine neutrale Kulisse.

## Grafik und Figuren – ausdrücklich ungelöst

Die Rückmeldung zur Gesamtoptik ist berechtigt. Die bisherigen prozeduralen Figuren erreichen weder Gesicht, Haarform, Kleidungsfall noch Oberflächenqualität der Charakterkarten. In diesem Stand werden sie nicht durch eine weitere kleine Generatoränderung als „realistisch“ bezeichnet. Für den nächsten visuellen Meilenstein braucht es einen gezielt modellierten, texturierten und geprüften Simon als Referenzmodell mit Front-/Seiten-/Rückansichtsvergleich, bevor weitere Figuren nachgezogen werden. Keine Unreal- oder Fotorealismus-Behauptung.

## Prüfungen

`npm test`: bestehende Geometrie-/Missions-/GLB-Prüfungen sowie Tempoverhältnis 1:2:3, sichere Standardwerte, sanfter Übergang und Schutz gegen Durchlaufen schmaler Hindernisse auch mit Schnell.

Browser: `tests/speed_browser.py` für die UI, gemessene Zeit pro simulierter Frame, Persistenz, Tastatur/Touch, Hausöffnungen und Möbelkollisionen; bestehender Missionsdurchlauf bleibt gesondert über `tests/beach_browser.py` prüfbar. Software-Chromium, kein Hardware-FPS-Nachweis.
