# -*- coding: utf-8 -*-
"""
Disable Basic Auth Store - QGIS Plugin

Autor:     Dimitri Reimchen
Copyright: (C) 2026 Dimitri Reimchen
Lizenz:    GNU General Public License v2 oder neuer
Version:   1.2.0

Dieses Plugin deaktiviert alle "Speichern"-Checkboxen in QGIS-Verbindungs-
dialogen (PostgreSQL, WMS, WFS, SAP HANA etc.), um das versehentliche
Speichern von Zugangsdaten im Klartext zu verhindern.

Verbesserungen in v1.2.0 (basierend auf Security-Review):
- Signal-basierter Ansatz statt Polling-Timer (behebt Race Condition)
- Ausschliesslich ObjectName-Matching (keine fragile Texterkennung mehr)
- Verbessertes Audit-Logging im QGIS Message Log
- Hinweis auf Grenzen des Plugins (UI-only Control)
"""

from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtWidgets import QApplication, QCheckBox
from qgis.core import QgsMessageLog, Qgis


PLUGIN_NAME = "Disable Basic Auth Store"

# Ausschliesslich stabile ObjectNames - keine Texterkennung (locale-unabhaengig)
STORE_CHECKBOX_NAMES = {
    "cbStoreUsername",
    "cbStorePassword",
    "mSaveUsername",
    "mSavePassword",
    "chkStoreUsername",
    "chkStorePassword",
}

TOOLTIP_TEXT = (
    "Aus Sicherheitsgruenden deaktiviert.\n"
    "Bitte verwenden Sie den Tab 'Konfigurationen',\n"
    "um Zugangsdaten verschluesselt zu speichern.\n\n"
    "(C) 2026 Dimitri Reimchen"
)


class DisableBasicAuthStorePlugin(QObject):
    """
    Haupt-Plugin-Klasse.

    Verwendet einen Signal-basierten Ansatz ueber QApplication.focusChanged,
    um Dialoge sofort beim Oeffnen zu patchen - ohne Race Condition durch Polling.

    Hinweis: Dieses Plugin ist ein UI-only Control. Es verhindert versehentliches
    Speichern, ist aber kein Ersatz fuer Policy-basierte Haertung (GPO/Registry).
    Fuer echtes Enterprise-Hardening sollte es mit QGIS-Profil-Locking kombiniert
    werden.
    """

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self._patched = set()

    def initGui(self):
        """Wird von QGIS beim Laden des Plugins aufgerufen."""
        # Signal-basierter Ansatz: bei jedem Fokuswechsel pruefen
        QApplication.instance().focusChanged.connect(self._on_focus_changed)

        # Einmalig alle bereits offenen Widgets patchen (z.B. beim Reload)
        self._patch_all_open_widgets()

        QgsMessageLog.logMessage(
            "Plugin geladen (v1.2.0) - (C) 2026 Dimitri Reimchen. "
            "Signal-basiertes Monitoring aktiv. "
            "HINWEIS: UI-only Control - kein Ersatz fuer Policy-Haertung.",
            PLUGIN_NAME,
            Qgis.Info
        )

    def unload(self):
        """Wird von QGIS beim Entladen des Plugins aufgerufen."""
        try:
            QApplication.instance().focusChanged.disconnect(self._on_focus_changed)
        except RuntimeError:
            pass
        self._patched.clear()
        QgsMessageLog.logMessage(
            "Plugin entladen.",
            PLUGIN_NAME,
            Qgis.Info
        )

    def _on_focus_changed(self, old_widget, new_widget):
        """
        Wird bei jedem Fokuswechsel aufgerufen.
        Durchsucht das neue Widget und seinen Top-Level-Parent nach
        Speichern-Checkboxen.
        """
        if new_widget is None:
            return
        top = new_widget.window()
        if top:
            self._patch_widget(top)

    def _patch_all_open_widgets(self):
        """Patcht alle aktuell geoeffneten Top-Level-Widgets (einmalig beim Start)."""
        for top_widget in QApplication.topLevelWidgets():
            self._patch_widget(top_widget)

    def _patch_widget(self, widget):
        """
        Durchsucht ein Widget nach allen bekannten Speichern-Checkboxen
        anhand ihrer stabilen ObjectNames und deaktiviert sie.
        """
        for name in STORE_CHECKBOX_NAMES:
            checkbox = widget.findChild(QCheckBox, name)
            if checkbox:
                self._disable_checkbox(checkbox)

    def _disable_checkbox(self, checkbox):
        """
        Deaktiviert eine Checkbox und setzt Tooltip und Checked-State.
        Schreibt einen Audit-Eintrag ins QGIS Message Log.
        """
        widget_id = id(checkbox)

        if widget_id in self._patched and not checkbox.isEnabled():
            return

        if checkbox.isEnabled():
            checkbox.setEnabled(False)
            checkbox.setChecked(False)
            checkbox.setToolTip(TOOLTIP_TEXT)
            self._patched.add(widget_id)

            parent_name = checkbox.parent().__class__.__name__ if checkbox.parent() else "unknown"
            QgsMessageLog.logMessage(
                "[AUDIT] Checkbox deaktiviert: objectName='{}' "
                "in Widget '{}'. "
                "Klartext-Speicherung wurde verhindert.".format(
                    checkbox.objectName(), parent_name),
                PLUGIN_NAME,
                Qgis.Warning
            )
