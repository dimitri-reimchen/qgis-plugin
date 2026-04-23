# Disable Basic Auth Store – QGIS Plugin

**Autor:** Dimitri Reimchen  
**Copyright:** © 2026 Dimitri Reimchen  
**Lizenz:** GNU General Public License v2 oder neuer  
**Version:** 1.2.0  
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

> **Hinweis:** Dieses Plugin ist ein UI-only Control. Es verhindert versehentliches Speichern, ist aber kein Ersatz für Policy-basierte Härtung (GPO/Registry/QGIS-Profil-Locking). Für echtes Enterprise-Hardening sollte es mit QGIS-Profil-Locking kombiniert werden.

---

## Sicherheitsproblem

QGIS speichert bei aktivierter "Speichern"-Checkbox das Passwort im **Klartext** in der QGIS-Projektdatei (`.qgz`) oder in den Benutzereinstellungen. Dies stellt ein erhebliches Sicherheitsrisiko dar, insbesondere in Unternehmensumgebungen.

---

## Installation

### Methode 1 – Aus ZIP installieren (empfohlen)

1. ZIP-Datei [`disable_basic_auth_store_v1.2.0.zip`](./disable_basic_auth_store_v1.2.0.zip) herunterladen
2. SHA256-Prüfsumme verifizieren (siehe unten)
3. QGIS öffnen
4. Menü **Erweiterungen** → **Erweiterungen verwalten und installieren**
5. Tab **Aus ZIP installieren** wählen
6. ZIP-Datei auswählen → **Erweiterung installieren**
7. Plugin unter **Installiert** aktivieren (Häkchen setzen)

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

## SHA256-Prüfsummen (Verifikation)

Vor der Installation die Integrität der ZIP-Datei prüfen:

```bash
# Linux / macOS
sha256sum disable_basic_auth_store_v1.2.0.zip

# Windows (PowerShell)
Get-FileHash disable_basic_auth_store_v1.2.0.zip -Algorithm SHA256
```

| Version | SHA256 |
|---|---|
| 1.2.0 | `9896c59abad2aa4a38f30c52ce0e3eaf987016ac7ca9395d218f0d6cacded91f` |

---

## Funktionsweise

Das Plugin verwendet einen **Signal-basierten Ansatz** (`QApplication.focusChanged`), der Dialoge sofort beim Öffnen patcht – ohne Race Condition durch Polling. Die Erkennung erfolgt ausschließlich über stabile **ObjectNames** (`cbStorePassword`, `cbStoreUsername` etc.), nicht über locale-abhängige UI-Texte.

Bei jeder Deaktivierung wird ein **Audit-Eintrag** im QGIS Message Log geschrieben (`Warnung`-Ebene).

---

## Changelog

### v1.2.0 (2026-04-23)
- Signal-basierter Ansatz statt Polling-Timer (Race Condition behoben)
- Ausschließlich ObjectName-Matching (keine fragile Texterkennung mehr)
- Verbessertes Audit-Logging im QGIS Message Log
- SHA256-Prüfsumme im README
- Hinweis auf Grenzen des Plugins (UI-only Control)

### v1.1.0 (2026-04-23)
- Unterstützung für PostgreSQL-Verbindungsdialog hinzugefügt
- Erweiterte Erkennung über Checkbox-Text (Deutsch/Englisch)

### v1.0.0 (2026-04-23)
- Erstveröffentlichung

---

## Download

| Version | Datei | SHA256 |
|---|---|---|
| **1.2.0** | [disable_basic_auth_store_v1.2.0.zip](./disable_basic_auth_store_v1.2.0.zip) | `9896c59abad2aa4a38f30c52ce0e3eaf987016ac7ca9395d218f0d6cacded91f` |
