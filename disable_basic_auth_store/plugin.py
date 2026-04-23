# -*- coding: utf-8 -*-
"""
Disable Basic Auth Store - QGIS Plugin

Autor:     Dimitri Reimchen
Copyright: (C) 2026 Dimitri Reimchen
Lizenz:    GNU General Public License v2 oder neuer
Version:   1.1.0

Dieses Plugin deaktiviert alle "Speichern"-Checkboxen (cbStoreUsername,
cbStorePassword) in ALLEN QGIS-Dialogen, die Zugangsdaten im Klartext
speichern könnten – inklusive PostgreSQL, WMS, WFS, SAP HANA etc.

Strategie: Ein QTimer durchsucht alle 300ms alle sichtbaren Top-Level-Widgets
rekursiv nach QCheckBoxen mit den bekannten Objektnamen UND nach
QCheckBoxen, deren Text "Speichern" oder "Store" enthält.
"""

from qgis.PyQt.QtCore import QTimer
from qgis.PyQt.QtWidgets import QApplication, QCheckBox
from qgis.core import QgsMessageLog, Qgis


PLUGIN_NAME = "Disable Basic Auth Store"

# Bekannte Objektnamen der Speichern-Checkboxen in QGIS-Dialogen
STORE_CHECKBOX_NAMES = {
    "cbStoreUsername",
    "cbStorePassword",
    "mSaveUsername",
    "mSavePassword",
    "chkStoreUsername",
    "chkStorePassword",
}

# Bekannte Label-Texte (Deutsch + Englisch) der Speichern-Checkboxen
STORE_CHECKBOX_TEXTS = {
    "speichern",
    "store",
    "save",
    "passwort speichern",
    "benutzername speichern",
    "save password",
    "save username",
    "store password",
    "store username",
}

TOOLTIP_TEXT = (
    "Aus Sicherheitsgründen deaktiviert.\n"
    "Bitte verwenden Sie den Tab 'Konfigurationen',\n"
    "um Zugangsdaten verschlüsselt zu speichern.\n\n"
    "© 2026 Dimitri Reimchen"
)


class DisableBasicAuthStorePlugin:
    """Haupt-Plugin-Klasse."""

    def __init__(self, iface):
        self.iface = iface
        self._timer = QTimer()
        self._timer.setInterval(300)  # alle 300ms prüfen
        self._timer.timeout.connect(self._patch_all_open_widgets)
        self._patched = set()  # bereits gepatchte Widgets (id) merken

    def initGui(self):
        """Wird von QGIS beim Laden des Plugins aufgerufen."""
        self._timer.start()
        QgsMessageLog.logMessage(
            "Plugin geladen (v1.1.0) – © 2026 Dimitri Reimchen: "
            "Alle Basic-Auth Store-Checkboxen werden deaktiviert.",
            PLUGIN_NAME,
            Qgis.Info
        )

    def unload(self):
        """Wird von QGIS beim Entladen des Plugins aufgerufen."""
        self._timer.stop()
        self._patched.clear()
        QgsMessageLog.logMessage(
            "Plugin entladen.",
            PLUGIN_NAME,
            Qgis.Info
        )

    def _patch_all_open_widgets(self):
        """
        Durchsucht alle aktuell sichtbaren Top-Level-Widgets nach
        Speichern-Checkboxen und deaktiviert sie.
        """
        for top_widget in QApplication.topLevelWidgets():
            for checkbox in top_widget.findChildren(QCheckBox):
                self._maybe_disable_checkbox(checkbox)

    def _maybe_disable_checkbox(self, checkbox):
        """
        Prüft ob eine Checkbox eine "Speichern"-Checkbox ist und
        deaktiviert sie gegebenenfalls.
        """
        widget_id = id(checkbox)

        # Bereits gepatcht und immer noch deaktiviert? Überspringen.
        if widget_id in self._patched and not checkbox.isEnabled():
            return

        should_disable = False

        # Prüfung 1: Bekannter Objektname
        if checkbox.objectName() in STORE_CHECKBOX_NAMES:
            should_disable = True

        # Prüfung 2: Text der Checkbox enthält "Speichern" / "Store" / "Save"
        if not should_disable:
            checkbox_text = checkbox.text().lower().strip()
            if checkbox_text in STORE_CHECKBOX_TEXTS:
                parent = checkbox.parent()
                if parent:
                    parent_class = parent.__class__.__name__
                    # Nur in Auth-relevanten Widgets deaktivieren
                    if any(keyword in parent_class.lower() for keyword in
                           ["auth", "connection", "connect", "login", "credential"]):
                        should_disable = True
                    # Auch direkt im QgsAuthSettingsWidget
                    if parent_class == "QgsAuthSettingsWidget":
                        should_disable = True

        if should_disable and checkbox.isEnabled():
            checkbox.setEnabled(False)
            checkbox.setChecked(False)
            checkbox.setToolTip(TOOLTIP_TEXT)
            self._patched.add(widget_id)
            QgsMessageLog.logMessage(
                f"Checkbox deaktiviert: '{checkbox.objectName()}' "
                f"(Text: '{checkbox.text()}') in {checkbox.parent().__class__.__name__}",
                PLUGIN_NAME,
                Qgis.Info
            )
