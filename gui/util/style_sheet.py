# coding: utf-8
from enum import Enum

from qfluentwidgets import StyleSheetBase, Theme, isDarkTheme, qconfig


class StyleSheet(StyleSheetBase, Enum):
    """ Style sheet  """

    HOME = "home"
    PROCESS = "process"
    SETTINGS = "settings"
    SWITCH = "switch"

    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        return f"gui/assets/qss/{theme.value.lower()}/{self.value}.qss"