"""
================================================================================
IP_Scan_Tools - Motor de Temas y Estilos Visuales Premium
Propiedad y Desarrollo por: Ezequiel Díaz
Todos los derechos reservados © 2026 Ezequiel Díaz
================================================================================
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

THEMES = {
    "🌙 Obsidian Cyber": {
        "appearance": "Dark",
        "bg_main": "#0b0f19",
        "card_bg": "#111827",
        "card_border": "#1f2937",
        "card_border_width": 1,
        "header_bg": "#111827",
        "accent_primary": "#06b6d4",       # Electric Cyan
        "accent_primary_hover": "#0891b2",
        "accent_secondary": "#10b981",     # Emerald Green
        "accent_secondary_hover": "#059669",
        "accent_purple": "#8b5cf6",        # Cyber Purple
        "accent_purple_hover": "#7c3aed",
        "accent_blue": "#3b82f6",          # Vibrant Blue
        "accent_blue_hover": "#2563eb",
        "accent_danger": "#ef4444",        # Crimson Red
        "accent_danger_hover": "#dc2626",
        "accent_warning": "#f59e0b",       # Amber
        "accent_warning_hover": "#d97706",
        "text_primary": "#f9fafb",
        "text_secondary": "#9ca3af",
        "text_muted": "#6b7280",
        "tree_bg": "#111827",
        "tree_fg": "#f3f4f6",
        "tree_heading_bg": "#1f2937",
        "tree_heading_fg": "#38bdf8",
        "tree_selected_bg": "#0369a1",
        "tree_selected_fg": "#ffffff",
        "tree_grid_line": "#1f2937",
        "badge_online_bg": "#064e3b",
        "badge_online_fg": "#34d399",
        "badge_offline_bg": "#7f1d1d",
        "badge_offline_fg": "#fca5a5"
    },
    "💼 Titanium Luxe": {
        "appearance": "Dark",
        "bg_main": "#0f172a",
        "card_bg": "#1e293b",
        "card_border": "#334155",
        "card_border_width": 1,
        "header_bg": "#1e293b",
        "accent_primary": "#6366f1",       # Royal Indigo
        "accent_primary_hover": "#4f46e5",
        "accent_secondary": "#10b981",     # Emerald
        "accent_secondary_hover": "#059669",
        "accent_purple": "#a855f7",        # Royal Purple
        "accent_purple_hover": "#9333ea",
        "accent_blue": "#0284c7",          # Sapphire
        "accent_blue_hover": "#0369a1",
        "accent_danger": "#f43f5e",        # Rose Red
        "accent_danger_hover": "#e11d48",
        "accent_warning": "#f59e0b",       # Amber Gold
        "accent_warning_hover": "#d97706",
        "text_primary": "#f8fafc",
        "text_secondary": "#94a3b8",
        "text_muted": "#64748b",
        "tree_bg": "#1e293b",
        "tree_fg": "#f8fafc",
        "tree_heading_bg": "#334155",
        "tree_heading_fg": "#818cf8",
        "tree_selected_bg": "#4338ca",
        "tree_selected_fg": "#ffffff",
        "tree_grid_line": "#334155",
        "badge_online_bg": "#064e3b",
        "badge_online_fg": "#6ee7b7",
        "badge_offline_bg": "#881337",
        "badge_offline_fg": "#fecdd3"
    },
    "❄️ Nordic Frost": {
        "appearance": "Light",
        "bg_main": "#f8fafc",
        "card_bg": "#ffffff",
        "card_border": "#e2e8f0",
        "card_border_width": 1,
        "header_bg": "#ffffff",
        "accent_primary": "#2563eb",       # Sapphire Blue
        "accent_primary_hover": "#1d4ed8",
        "accent_secondary": "#0d9488",     # Teal
        "accent_secondary_hover": "#0f766e",
        "accent_purple": "#7c3aed",        # Deep Violet
        "accent_purple_hover": "#6d28d9",
        "accent_blue": "#0284c7",          # Sky Blue
        "accent_blue_hover": "#0369a1",
        "accent_danger": "#dc2626",        # Red
        "accent_danger_hover": "#b91c1c",
        "accent_warning": "#d97706",       # Amber
        "accent_warning_hover": "#b45309",
        "text_primary": "#0f172a",
        "text_secondary": "#64748b",
        "text_muted": "#94a3b8",
        "tree_bg": "#ffffff",
        "tree_fg": "#0f172a",
        "tree_heading_bg": "#f1f5f9",
        "tree_heading_fg": "#1e40af",
        "tree_selected_bg": "#cbd5e1",
        "tree_selected_fg": "#0f172a",
        "tree_grid_line": "#e2e8f0",
        "badge_online_bg": "#d1fae5",
        "badge_online_fg": "#065f46",
        "badge_offline_bg": "#fee2e2",
        "badge_offline_fg": "#991b1b"
    },
    "⚡ Cyberpunk Neon": {
        "appearance": "Dark",
        "bg_main": "#050508",
        "card_bg": "#0d0d15",
        "card_border": "#1a1a2e",
        "card_border_width": 1,
        "header_bg": "#0d0d15",
        "accent_primary": "#a855f7",       # Neon Purple
        "accent_primary_hover": "#9333ea",
        "accent_secondary": "#10b981",     # Neon Emerald
        "accent_secondary_hover": "#059669",
        "accent_purple": "#ec4899",        # Neon Pink
        "accent_purple_hover": "#db2777",
        "accent_blue": "#06b6d4",          # Electric Cyan
        "accent_blue_hover": "#0891b2",
        "accent_danger": "#f43f5e",        # Neon Rose
        "accent_danger_hover": "#e11d48",
        "accent_warning": "#f59e0b",       # Neon Amber
        "accent_warning_hover": "#d97706",
        "text_primary": "#f3f4f6",
        "text_secondary": "#9ca3af",
        "text_muted": "#6b7280",
        "tree_bg": "#0d0d15",
        "tree_fg": "#e5e7eb",
        "tree_heading_bg": "#1a1a2e",
        "tree_heading_fg": "#c084fc",
        "tree_selected_bg": "#6b21a8",
        "tree_selected_fg": "#ffffff",
        "tree_grid_line": "#1a1a2e",
        "badge_online_bg": "#064e3b",
        "badge_online_fg": "#34d399",
        "badge_offline_bg": "#831843",
        "badge_offline_fg": "#f472b6"
    }
}

DEFAULT_THEME_NAME = "🌙 Obsidian Cyber"

class ThemeManager:
    """Gestor centralizado de temas y estilos visuales para IP_Scan_Tools."""
    
    @staticmethod
    def get_theme_names():
        return list(THEMES.keys())

    @staticmethod
    def get_theme(name):
        return THEMES.get(name, THEMES[DEFAULT_THEME_NAME])

    @staticmethod
    def apply_treeview_style(theme_dict):
        """Aplica estilos dinámicos a las tablas ttk.Treeview de la aplicación."""
        style = ttk.Style()
        style.theme_use("default")

        bg_color = theme_dict["tree_bg"]
        fg_color = theme_dict["tree_fg"]
        head_bg = theme_dict["tree_heading_bg"]
        head_fg = theme_dict["tree_heading_fg"]
        selected_bg = theme_dict["tree_selected_bg"]
        selected_fg = theme_dict["tree_selected_fg"]
        border_col = theme_dict["card_border"]

        style.configure(
            "Treeview",
            background=bg_color,
            foreground=fg_color,
            rowheight=38,
            fieldbackground=bg_color,
            bordercolor=border_col,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Treeview.Heading",
            background=head_bg,
            foreground=head_fg,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=(6, 6)
        )
        style.map(
            "Treeview",
            background=[("selected", selected_bg)],
            foreground=[("selected", selected_fg)]
        )
