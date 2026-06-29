"""
Parakram VPS — Design Theme
Black, white, and metallic gold palette.
"""

import customtkinter as ctk

# ─── Color Palette ───────────────────────────────────────────────────────
BLACK = "#070708"
DARK = "#0d0d0e"
DARK_BORDER = "#1a1a1c"
WHITE = "#e8e6e3"
GRAY = "#5a5a5a"
GRAY_LIGHT = "#8a8a8a"
GOLD = "#c9a96e"
GOLD_HOVER = "#b89540"
GOLD_DARK = "#a88740"
GOLD_GRADIENT_START = "#c9a96e"
GOLD_GRADIENT_END = "#a88740"
RED = "#ef4444"
GREEN = "#22c55e"

# ─── Font Sizes ──────────────────────────────────────────────────────────
FONT_LARGE = ("Segoe UI", 32, "bold")
FONT_TITLE = ("Segoe UI", 22, "bold")
FONT_HEADING = ("Segoe UI", 16, "bold")
FONT_BODY = ("Segoe UI", 13)
FONT_SMALL = ("Segoe UI", 11)
FONT_TINY = ("Segoe UI", 9)
FONT_MONO = ("Cascadia Code", 12)

# ─── CTk Theme Override ──────────────────────────────────────────────────
def apply_theme():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    theme = {
        "CTk": {
            "fg_color": BLACK,
        },
        "CTkFrame": {
            "fg_color": DARK,
            "border_color": DARK_BORDER,
            "corner_radius": 12,
        },
        "CTkEntry": {
            "fg_color": DARK,
            "border_color": DARK_BORDER,
            "text_color": WHITE,
            "placeholder_text_color": GRAY,
            "corner_radius": 8,
        },
        "CTkButton": {
            "fg_color": GOLD,
            "hover_color": GOLD_HOVER,
            "text_color": BLACK,
            "corner_radius": 10,
            "border_width": 0,
        },
        "CTkLabel": {
            "text_color": WHITE,
        },
        "CTkCheckBox": {
            "fg_color": DARK,
            "border_color": DARK_BORDER,
            "hover_color": GOLD_DARK,
        },
        "CTkProgressBar": {
            "fg_color": DARK,
            "progress_color": GOLD,
            "corner_radius": 6,
            "border_width": 0,
        },
        "CTkTextbox": {
            "fg_color": DARK,
            "border_color": DARK_BORDER,
            "text_color": WHITE,
            "corner_radius": 8,
        },
        "CTkScrollbar": {
            "fg_color": DARK,
            "button_color": GRAY,
            "button_hover_color": GOLD,
        },
        "CTkOptionMenu": {
            "fg_color": DARK,
            "button_color": GOLD,
            "button_hover_color": GOLD_HOVER,
            "text_color": WHITE,
        },
    }
    ctk.ThemeManager.theme["CTk"] = theme["CTk"]
    ctk.ThemeManager.theme["CTkFrame"] = theme["CTkFrame"]
    ctk.ThemeManager.theme["CTkEntry"] = theme["CTkEntry"]
    ctk.ThemeManager.theme["CTkButton"] = theme["CTkButton"]
    ctk.ThemeManager.theme["CTkLabel"] = theme["CTkLabel"]
    ctk.ThemeManager.theme["CTkCheckBox"] = theme["CTkCheckBox"]
    ctk.ThemeManager.theme["CTkProgressBar"] = theme["CTkProgressBar"]
    ctk.ThemeManager.theme["CTkTextbox"] = theme["CTkTextbox"]
    ctk.ThemeManager.theme["CTkScrollbar"] = theme["CTkScrollbar"]
    ctk.ThemeManager.theme["CTkOptionMenu"] = theme["CTkOptionMenu"]
