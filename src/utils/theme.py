"""
ThermaX Theme System
Provides dark/light mode with futuristic neon glow design tokens
"""

DARK_THEME = {
    # Backgrounds
    "bg_primary":      "#0A0E1A",
    "bg_secondary":    "#0F1526",
    "bg_card":         "#111827",
    "bg_card_hover":   "#1A2235",
    "bg_sidebar":      "#080C18",

    # Neon Accent Colors
    "accent_blue":     "#00D4FF",
    "accent_purple":   "#8B5CF6",
    "accent_cyan":     "#06B6D4",
    "accent_pink":     "#F472B6",
    "accent_green":    "#10B981",
    "accent_orange":   "#F59E0B",
    "accent_red":      "#EF4444",

    # Text
    "text_primary":    "#E2E8F0",
    "text_secondary":  "#94A3B8",
    "text_muted":      "#475569",
    "text_accent":     "#00D4FF",

    # Borders
    "border":          "#1E293B",
    "border_accent":   "#00D4FF33",
    "border_glow":     "#8B5CF633",

    # Gauge colors (low/mid/high)
    "gauge_low":       "#10B981",
    "gauge_mid":       "#F59E0B",
    "gauge_high":      "#EF4444",

    # Graph colors
    "graph_cpu":       "#00D4FF",
    "graph_gpu":       "#8B5CF6",
    "graph_ram":       "#10B981",
    "graph_disk":      "#F59E0B",
    "graph_net":       "#F472B6",

    # Shadows / glow
    "glow_blue":       "0 0 20px #00D4FF55",
    "glow_purple":     "0 0 20px #8B5CF655",

    # Status
    "status_good":     "#10B981",
    "status_moderate": "#F59E0B",
    "status_critical": "#EF4444",

    # Mode colors
    "mode_quiet":      "#06B6D4",
    "mode_balanced":   "#10B981",
    "mode_performance":"#8B5CF6",
    "mode_turbo":      "#EF4444",
}

LIGHT_THEME = {
    "bg_primary":      "#F1F5F9",
    "bg_secondary":    "#E2E8F0",
    "bg_card":         "#FFFFFF",
    "bg_card_hover":   "#F8FAFC",
    "bg_sidebar":      "#E2E8F0",

    "accent_blue":     "#0EA5E9",
    "accent_purple":   "#7C3AED",
    "accent_cyan":     "#0891B2",
    "accent_pink":     "#EC4899",
    "accent_green":    "#059669",
    "accent_orange":   "#D97706",
    "accent_red":      "#DC2626",

    "text_primary":    "#0F172A",
    "text_secondary":  "#475569",
    "text_muted":      "#94A3B8",
    "text_accent":     "#0EA5E9",

    "border":          "#CBD5E1",
    "border_accent":   "#0EA5E933",
    "border_glow":     "#7C3AED33",

    "gauge_low":       "#059669",
    "gauge_mid":       "#D97706",
    "gauge_high":      "#DC2626",

    "graph_cpu":       "#0EA5E9",
    "graph_gpu":       "#7C3AED",
    "graph_ram":       "#059669",
    "graph_disk":      "#D97706",
    "graph_net":       "#EC4899",

    "glow_blue":       "none",
    "glow_purple":     "none",

    "status_good":     "#059669",
    "status_moderate": "#D97706",
    "status_critical": "#DC2626",

    "mode_quiet":      "#0891B2",
    "mode_balanced":   "#059669",
    "mode_performance":"#7C3AED",
    "mode_turbo":      "#DC2626",
}


class ThemeManager:
    """Singleton theme manager"""
    _instance = None
    _is_dark = True
    _callbacks = []

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def colors(self):
        return DARK_THEME if self._is_dark else LIGHT_THEME

    @property
    def is_dark(self):
        return self._is_dark

    def toggle(self):
        self._is_dark = not self._is_dark
        for cb in self._callbacks:
            cb(self.colors)

    def set_dark(self, dark: bool):
        self._is_dark = dark
        for cb in self._callbacks:
            cb(self.colors)

    def register(self, callback):
        """Register a callback fn(colors) called on theme change"""
        self._callbacks.append(callback)

    def get(self, key: str, fallback: str = "#FFFFFF") -> str:
        return self.colors.get(key, fallback)

    def stylesheet(self) -> str:
        """Generate the global QSS stylesheet"""
        c = self.colors
        return f"""
        /* ========== Global ========== */
        QWidget {{
            background-color: {c['bg_primary']};
            color: {c['text_primary']};
            font-family: 'Segoe UI', 'Arial', sans-serif;
            font-size: 13px;
            border: none;
        }}

        /* ========== Scroll Bars ========== */
        QScrollBar:vertical {{
            background: {c['bg_secondary']};
            width: 6px;
            border-radius: 3px;
        }}
        QScrollBar::handle:vertical {{
            background: {c['accent_blue']};
            border-radius: 3px;
            min-height: 30px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        QScrollBar:horizontal {{
            background: {c['bg_secondary']};
            height: 6px;
            border-radius: 3px;
        }}
        QScrollBar::handle:horizontal {{
            background: {c['accent_blue']};
            border-radius: 3px;
        }}

        /* ========== Tool Tips ========== */
        QToolTip {{
            background-color: {c['bg_card']};
            color: {c['text_primary']};
            border: 1px solid {c['accent_blue']};
            padding: 4px 8px;
            border-radius: 4px;
        }}

        /* ========== Sliders ========== */
        QSlider::groove:horizontal {{
            height: 4px;
            background: {c['border']};
            border-radius: 2px;
        }}
        QSlider::handle:horizontal {{
            background: {c['accent_blue']};
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }}
        QSlider::sub-page:horizontal {{
            background: {c['accent_blue']};
            border-radius: 2px;
        }}

        /* ========== Combo Box ========== */
        QComboBox {{
            background-color: {c['bg_card']};
            color: {c['text_primary']};
            border: 1px solid {c['border']};
            border-radius: 6px;
            padding: 4px 8px;
        }}
        QComboBox::drop-down {{
            border: none;
        }}
        QComboBox QAbstractItemView {{
            background-color: {c['bg_card']};
            color: {c['text_primary']};
            selection-background-color: {c['accent_blue']}33;
        }}

        /* ========== Line Edit ========== */
        QLineEdit {{
            background-color: {c['bg_card']};
            color: {c['text_primary']};
            border: 1px solid {c['border']};
            border-radius: 6px;
            padding: 4px 8px;
        }}
        QLineEdit:focus {{
            border: 1px solid {c['accent_blue']};
        }}

        /* ========== Check Box ========== */
        QCheckBox {{
            color: {c['text_primary']};
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 4px;
            border: 1px solid {c['border']};
            background: {c['bg_card']};
        }}
        QCheckBox::indicator:checked {{
            background: {c['accent_blue']};
            border: 1px solid {c['accent_blue']};
        }}
        """
