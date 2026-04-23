# -*- coding: utf-8 -*-
"""
Disable Basic Auth Store - QGIS Plugin

Autor:     Dimitri Reimchen
Copyright: (C) 2026 Dimitri Reimchen
Lizenz:    GNU General Public License v2 oder neuer
"""


def classFactory(iface):
    from .plugin import DisableBasicAuthStorePlugin
    return DisableBasicAuthStorePlugin(iface)
