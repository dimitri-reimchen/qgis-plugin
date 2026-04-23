# -*- coding: utf-8 -*-
"""
Disable Basic Auth Store - QGIS Plugin

Autor:     Dimitri Reimchen
Copyright: (C) 2026 Dimitri Reimchen
Lizenz:    GNU General Public License v2 oder neuer
Version:   1.3.0

Dieses Plugin deaktiviert alle "Speichern"-Checkboxen in QGIS-Verbindungs-
dialogen (PostgreSQL, WMS, WFS, SAP HANA etc.), um das versehentliche
Speichern von Zugangsdaten im Klartext zu verhindern.

Verbesserungen in v1.3.0 (basierend auf Security-Review):
- Memory Leak behoben: _patched-Set wird via checkbox.destroyed-Signal
  aufgeraeumt, damit veraltete id()-Eintraege entfernt werden
- metadata.txt: tracker/repository/homepage zeigen auf eigenes Repo

Verbesserungen in v1.2.0:
- Signal-basierter Ansatz statt Polling-Timer (Race Condition behoben)
- Ausschliesslich ObjectName-Matching (keine fragile Texterkennung)
- Audit-Logging im QGIS Message Log
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
    um Dialoge sofort beim Oeffnen zu patchen - ohne Race Condition.

    Memory-Management: Wenn ein Qt-Widget zerstoert wird, wird seine id()
    via checkbox.destroyed-Signal aus _patched entfernt, um Memory Leaks
    bei langen QGIS-Sessions zu verhindern.

    Hinweis: UI-only Control - kein Ersatz fuer Policy-basierte Haertung
    (GPO/Registry/qgis_global_settings.ini).
    """

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self._patched = set()

    def initGui(self):
        """Wird von QGIS beim Laden des Plugins aufgerufen."""
        QApplication.instance().focusChanged.connect(self._on_focus_changed)
        self._patch_all_open_widgets()

        QgsMessageLog.logMessage(
            "Plugin geladen (v1.3.0) - (C) 2026 Dimitri Reimchen. "
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
        """Bei jedem Fokuswechsel das neue Top-Level-Widget patchen."""
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
        Deaktiviert eine Checkbox, setzt Tooltip und Checked-State.
        Verbindet checkbox.destroyed mit _on_checkbox_destroyed, um
        den _patched-Eintrag bei Widget-Zerstoerung aufzuraeumen (Memory Leak Fix).
        Schreibt einen Audit-Eintrag ins QGIS Message Log.
        """
        widget_id = id(checkbox)

        # Bereits gepatcht und noch deaktiviert? Nichts tun.
        if widget_id in self._patched and not checkbox.isEnabled():
            return

        if checkbox.isEnabled():
            checkbox.setEnabled(False)
            checkbox.setChecked(False)
            checkbox.setToolTip(TOOLTIP_TEXT)
            self._patched.add(widget_id)

            # Memory Leak Fix: bei Widget-Zerstoerung id() aus _patched entfernen
            checkbox.destroyed.connect(lambda: self._patched.discard(widget_id))

            parent_name = checkbox.parent().__class__.__name__ if checkbox.parent() else "unknown"
            QgsMessageLog.logMessage(
                "[AUDIT] Checkbox deaktiviert: objectName='{}' "
                "in Widget '{}'. "
                "Klartext-Speicherung wurde verhindert.".format(
                    checkbox.objectName(), parent_name),
                PLUGIN_NAME,
                Qgis.Warning
            )
