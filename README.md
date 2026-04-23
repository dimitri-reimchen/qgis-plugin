# Disable Basic Auth Store – QGIS Plugin

**Autor:** Dimitri Reimchen  
**Copyright:** © 2026 Dimitri Reimchen  
**Lizenz:** GNU General Public License v2 oder neuer  
**Version:** 1.1.0  
**QGIS Mindestversion:** 3.0  

---

## Beschreibung

Dieses QGIS-Plugin deaktiviert aus Sicherheitsgründen alle **"Speichern"-Checkboxen** in QGIS-Verbindungsdialogen, die Zugangsdaten (Benutzername und Passwort) im **Klartext** speichern würden.

Betroffen sind alle Verbindungsdialoge, u.a.:
- PostgreSQL
- WMS / WMTS
- WFS / OGC API
- SAP HANA
- MS SQL Server
- und weitere

Nutzer werden stattdessen auf den sicheren **"Konfigurationen"-Tab** verwiesen, der Zugangsdaten verschlüsselt in der QGIS-Authentifizierungsdatenbank speichert.

---

## Sicherheitsproblem

QGIS speichert bei aktivierter "Speichern"-Checkbox das Passwort im **Klartext** in der QGIS-Projektdatei (`.qgz`) oder in den Benutzereinstellungen. Dies stellt ein erhebliches Sicherheitsrisiko dar, insbesondere in Unternehmensumgebungen.

---

## Installation

### Methode 1 – Aus ZIP installieren (empfohlen)

1. ZIP-Datei [`disable_basic_auth_store_v1.1.0.zip`](./disable_basic_auth_store_v1.1.0.zip) herunterladen
2. QGIS öffnen
3. Menü **Erweiterungen** → **Erweiterungen verwalten und installieren**
4. Tab **Aus ZIP installieren** wählen
5. ZIP-Datei auswählen → **Erweiterung installieren**
6. Plugin unter **Installiert** aktivieren (Häkchen setzen)

### Methode 2 – Manuell (für SCCM / Unternehmensdeployment)

Plugin-Ordner `disable_basic_auth_store/` in das QGIS-Plugin-Verzeichnis kopieren:

```
# Windows (pro Benutzer)
C:\Users\<USERNAME>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\

# Windows (systemweit, erfordert Admin)
C:\Program Files\QGIS <Version>\apps\qgis\python\plugins\

# Linux
~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
```

---

## Funktionsweise

Das Plugin startet beim QGIS-Start einen Timer (alle 300 ms), der alle offenen Dialoge nach Speichern-Checkboxen durchsucht und diese deaktiviert. Die Erkennung erfolgt über:

1. **Objektname** – bekannte Namen wie `cbStorePassword`, `cbStoreUsername`
2. **Checkbox-Text** – Texte wie "Speichern", "Store", "Save" in Auth-relevanten Dialogen

---

## Download

| Version | Datei | Datum |
|---|---|---|
| 1.1.0 | [disable_basic_auth_store_v1.1.0.zip](./disable_basic_auth_store_v1.1.0.zip) | 2026-04-23 |
