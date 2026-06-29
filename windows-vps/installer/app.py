"""
PARAKRAM VPS INSTALLER — APPLICATION LAYER (Military/Space Grade)
==================================================================
Classification: CONTROLLED
SLA: 99.999% uptime target | MTTR < 5 minutes
Design: Zero-trust input validation, graceful degradation,
        crash recovery via checkpoint system, comprehensive audit trail.

Principles:
  1. NEVER trust user input — validate every field at every boundary
  2. NEVER assume network availability — degrade gracefully
  3. NEVER lose state — checkpoint every step
  4. NEVER deadlock — timeouts on all blocking operations
  5. ALWAYS log — every action recorded with context and timing
  6. ALWAYS recover — crash-safe resume from last checkpoint

UI Philosophy: Apple-style clarity with space-grade reliability.
  - Every action has visual confirmation
  - Every error has a recovery hint
  - Every state is observable
  - No ambiguous progress indicators

Usage:
    python app.py                  # Launch GUI installer
    python app.py --headless       # Silent install (non-interactive)
    python app.py --headless --token=xxx  # Silent install with Cloudflare token
    python app.py --uninstall      # Remove all components
    python app.py --status         # Check installation status
"""

import sys
import os
import json
import time
import webbrowser
import threading
import tkinter as tk
from tkinter import font as tkfont
from pathlib import Path
from typing import Optional, Any
from enum import Enum

# ─── Third-party ─────────────────────────────────────────────────────────
try:
    import customtkinter as ctk
except ImportError:
    print("[CRITICAL] customtkinter not installed. Installing...")
    rc = os.system(f'"{sys.executable}" -m pip install customtkinter Pillow httpx')
    if rc != 0:
        print("[FATAL] Failed to install customtkinter. Run: pip install customtkinter Pillow httpx")
        sys.exit(1)
    import customtkinter as ctk

# ─── Local imports ───────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from theme import *
from core.api_client import ParakramAPI, APIError, ErrorSeverity
from core.setup_engine import SetupEngine, INSTALL_DIR, LOG_FILE, Checkpoint, InstallError
from core.updater import AutoUpdater, UpdateInfo
from core.heartbeat import HeartbeatService


# ═══════════════════════════════════════════════════════════════════════════
#  APPLICATION STATE
# ═══════════════════════════════════════════════════════════════════════════

class InstallState(Enum):
    """Finite state machine for the installation lifecycle."""
    IDLE = "IDLE"
    PRECHECK = "PRECHECK"
    INSTALLING = "INSTALLING"
    SUBSCRIBING = "SUBSCRIBING"
    VERIFYING = "VERIFYING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    ABORTED = "ABORTED"


# ═══════════════════════════════════════════════════════════════════════════
#  APPLICATION
# ═══════════════════════════════════════════════════════════════════════════

class ParakramVPSInstaller(ctk.CTk):
    """
    Main installer application with military-grade reliability.

    Architecture:
      - Finite state machine for installation lifecycle
      - Checkpoint-based crash recovery
      - Circuit-broken API client
      - Thread-safe UI updates
      - Comprehensive audit logging
    """

    WIDTH = 720
    HEIGHT = 620  # Increased height for better spacing

    def __init__(self):
        super().__init__()
        apply_theme()

        # ── Window ─────────────────────────────────────────────────────
        self.title("Parakram VPS — Mission Control")
        self.configure(fg_color=BLACK)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.resizable(False, False)
        self._center_window()

        # ── State Machine ──────────────────────────────────────────────
        self._page = 0
        self._state = InstallState.IDLE
        self._api = ParakramAPI()
        self._engine = SetupEngine(progress_callback=self._on_progress)
        self._auth_token: Optional[str] = None
        self._user_email: Optional[str] = None
        self._user_name: Optional[str] = None
        self._subscription_plan: str = "free"
        self._install_errors: list[str] = []
        self._install_warnings: list[str] = []
        self._install_result: Optional[dict] = None
        self._abort_requested = threading.Event()
        self._installed = self._check_installed()

        # ── UI Components ──────────────────────────────────────────────
        self.container = ctk.CTkFrame(self, fg_color=BLACK, corner_radius=0)
        self.container.pack(fill="both", expand=True)

        self._build_sidebar()
        self._pages: list[ctk.CTkFrame] = []
        self._build_pages()

        # ── Auto-Update & Heartbeat ──────────────────────────────────
        self._updater = AutoUpdater(current_version="2.0.0", install_dir=INSTALL_DIR)
        self._heartbeat: Optional[HeartbeatService] = None
        self._update_info: Optional[UpdateInfo] = None
        self._updater.check_async(callback=self._on_update_check_complete)

        # ── Crash Recovery ─────────────────────────────────────────────
        self._attempt_recovery()

        self._show_page(0)

        # ── Bind close ─────────────────────────────────────────────────
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # ── Go! ────────────────────────────────────────────────────────
        self.mainloop()

    # ─── Window Helpers ──────────────────────────────────────────────────

    def _center_window(self):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - self.WIDTH) // 2
        y = (sh - self.HEIGHT) // 2
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")

    def _check_installed(self) -> bool:
        """Check if VPS is already installed via atomic config."""
        return (INSTALL_DIR / "config.json").exists()

    def _attempt_recovery(self):
        """Check if a previous installation was interrupted and recoverable."""
        from core.setup_engine import Checkpoint
        completed = Checkpoint.load()
        if completed:
            # Partial installation detected — offer recovery
            self._install_warnings.append(
                f"Previous installation detected ({len(completed)} steps completed). "
                "Running in recovery mode."
            )
            from core.setup_engine import audit
            audit("RECOVERY_MODE", f"Resuming from checkpoint: {completed}", "WARNING")

    # ─── Sidebar ─────────────────────────────────────────────────────────

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self.container, width=180, corner_radius=0, fg_color=DARK,
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Brand header
        title = ctk.CTkLabel(
            self.sidebar, text="PARAKRAM", font=("Segoe UI", 14, "bold"),
            text_color=GOLD,
        )
        title.pack(pady=(28, 4))

        subtitle = ctk.CTkLabel(
            self.sidebar, text="MISSION CONTROL", font=("Segoe UI", 8),
            text_color=GRAY,
        )
        subtitle.pack(pady=(0, 28))

        # Steps
        self._steps = [
            ("Welcome", "circle"),
            ("Account", "person"),
            ("Configure", "settings"),
            ("Install", "arrow-down"),
            ("Complete", "check"),
        ]
        self._step_labels: list[ctk.CTkLabel] = []
        self._step_dots: list[ctk.CTkLabel] = []

        for i, (label, _) in enumerate(self._steps):
            dot = ctk.CTkLabel(
                self.sidebar, text="○", font=("Segoe UI", 10),
                text_color=GRAY,
            )
            dot.pack(pady=(0, 2))
            self._step_dots.append(dot)

            lbl = ctk.CTkLabel(
                self.sidebar, text=label, font=FONT_SMALL,
                text_color=GRAY,
            )
            lbl.pack(pady=(0, 16))
            self._step_labels.append(lbl)

        self._update_sidebar(0)

    def _update_sidebar(self, active: int):
        for i in range(len(self._steps)):
            if i < active:
                self._step_dots[i].configure(text="●", text_color=GOLD)
                self._step_labels[i].configure(text_color=GOLD)
            elif i == active:
                self._step_dots[i].configure(text="●", text_color=WHITE)
                self._step_labels[i].configure(text_color=WHITE)
            else:
                self._step_dots[i].configure(text="○", text_color=GRAY)
                self._step_labels[i].configure(text_color=GRAY)

    # ─── Page System ────────────────────────────────────────────────────

    def _build_pages(self):
        self._pages = [
            self._page_welcome(),
            self._page_auth(),
            self._page_config(),
            self._page_install(),
            self._page_complete(),
        ]

    def _show_page(self, idx: int):
        self._page = idx
        for i, p in enumerate(self._pages):
            p.pack_forget()
        self._pages[idx].pack(fill="both", expand=True, padx=32, pady=32)
        self._update_sidebar(idx)

    # ═══════════════════════════════════════════════════════════════════
    #  PAGE 0: WELCOME
    # ═══════════════════════════════════════════════════════════════════

    def _page_welcome(self) -> ctk.CTkFrame:
        page = ctk.CTkFrame(self.container, fg_color=BLACK, corner_radius=0)

        spacer = ctk.CTkLabel(page, text="", font=FONT_LARGE)
        spacer.pack(expand=True)

        # Icon / Logo area
        logo = ctk.CTkLabel(
            page, text="⏻", font=("Segoe UI", 48),
            text_color=GOLD,
        )
        logo.pack(pady=(0, 8))

        title = ctk.CTkLabel(
            page, text="Parakram VPS",
            font=FONT_LARGE, text_color=WHITE,
        )
        title.pack(pady=(0, 8))

        subtitle = ctk.CTkLabel(
            page,
            text="Turn any Windows machine into a production-ready\n"
                 "virtual private server. No cloud bills. No port forwarding.\n"
                 "No technical expertise required.",
            font=FONT_BODY, text_color=GRAY, justify="center",
        )
        subtitle.pack(pady=(0, 8))

        # Version info
        from core.setup_engine import INSTALLER_VERSION
        ctk.CTkLabel(
            page, text=f"v{INSTALLER_VERSION}", font=FONT_TINY, text_color=GRAY,
        ).pack(pady=(0, 24))

        # Warnings
        if self._install_warnings:
            warn_frame = ctk.CTkFrame(page, fg_color="#1a1a0a", corner_radius=8)
            warn_frame.pack(fill="x", padx=40, pady=(0, 16))
            for w in self._install_warnings:
                ctk.CTkLabel(
                    warn_frame, text=f"⚠ {w}",
                    font=FONT_TINY, text_color="#eab308", justify="center",
                    wraplength=500,
                ).pack(pady=4, padx=12)

        if self._installed:
            status = ctk.CTkLabel(
                page, text="✓ Parakram VPS is already installed",
                font=FONT_SMALL, text_color=GREEN,
            )
            status.pack(pady=(0, 8))
            reinstall_btn = ctk.CTkButton(
                page, text="Reinstall / Upgrade",
                command=lambda: self._show_page(1),
                fg_color=GOLD, text_color=BLACK, hover_color=GOLD_HOVER,
                font=FONT_BODY, width=220, height=42,
            )
            reinstall_btn.pack(pady=(0, 8))
        else:
            get_started = ctk.CTkButton(
                page, text="Begin Installation →",
                command=lambda: self._show_page(1),
                fg_color=GOLD, text_color=BLACK, hover_color=GOLD_HOVER,
                font=("Segoe UI", 14, "bold"), width=260, height=48,
            )
            get_started.pack(pady=(0, 16))

            # Feature badges
            features_frame = ctk.CTkFrame(page, fg_color="transparent")
            features_frame.pack(pady=(4, 0))
            for feat in [
                "OpenSSH Remote Access", "Cloudflare Tunnel",
                "Management Dashboard", "Auto-Start on Boot"
            ]:
                pill = ctk.CTkLabel(
                    features_frame, text=f"  ✦ {feat}  ",
                    font=FONT_TINY, text_color=GRAY,
                    fg_color=DARK, corner_radius=20,
                )
                pill.pack(side="left", padx=4)

        ctk.CTkLabel(page, text="", font=FONT_SMALL).pack(expand=True)
        return page

    # ═══════════════════════════════════════════════════════════════════
    #  PAGE 1: ACCOUNT
    # ═══════════════════════════════════════════════════════════════════

    def _page_auth(self) -> ctk.CTkFrame:
        page = ctk.CTkFrame(self.container, fg_color=BLACK, corner_radius=0)

        title = ctk.CTkLabel(
            page, text="Create your account",
            font=FONT_TITLE, text_color=WHITE,
        )
        title.pack(anchor="w", pady=(0, 4))

        subtitle = ctk.CTkLabel(
            page,
            text="Sign up to manage your VPS, subscriptions, and get priority support.",
            font=FONT_SMALL, text_color=GRAY, justify="left", wraplength=500,
        )
        subtitle.pack(anchor="w", pady=(0, 20))

        # ── Mode Toggle ───────────────────────────────────────────────
        toggle_frame = ctk.CTkFrame(page, fg_color=DARK, corner_radius=10)
        toggle_frame.pack(fill="x", pady=(0, 20))

        self._auth_mode = tk.StringVar(value="register")
        for val, txt in [("register", "Create Account"), ("login", "Sign In")]:
            btn = ctk.CTkButton(
                toggle_frame, text=txt, font=FONT_SMALL,
                fg_color=GOLD if val == "register" else DARK,
                text_color=BLACK if val == "register" else GRAY,
                hover_color=GOLD_HOVER,
                corner_radius=8, height=32,
                command=lambda v=val: self._toggle_auth(v),
            )
            btn.pack(side="left", fill="x", expand=True, padx=4, pady=4)
            if val == "register":
                self._auth_register_btn = btn
            else:
                self._auth_login_btn = btn

        # ── Form ──────────────────────────────────────────────────────
        form = ctk.CTkFrame(page, fg_color="transparent")
        form.pack(fill="x")

        ctk.CTkLabel(form, text="Full Name", font=FONT_SMALL, text_color=GRAY).pack(anchor="w")
        self._name_entry = ctk.CTkEntry(
            form, placeholder_text="Your full name",
            height=38, font=FONT_BODY,
        )
        self._name_entry.pack(fill="x", pady=(4, 12))

        ctk.CTkLabel(form, text="Email Address", font=FONT_SMALL, text_color=GRAY).pack(anchor="w")
        self._email_entry = ctk.CTkEntry(
            form, placeholder_text="you@example.com",
            height=38, font=FONT_BODY,
        )
        self._email_entry.pack(fill="x", pady=(4, 12))

        ctk.CTkLabel(form, text="Password", font=FONT_SMALL, text_color=GRAY).pack(anchor="w")
        self._pass_entry = ctk.CTkEntry(
            form, placeholder_text="Minimum 6 characters",
            show="•", height=38, font=FONT_BODY,
        )
        self._pass_entry.pack(fill="x", pady=(4, 4))

        # Password strength indicator
        self._pass_strength = ctk.CTkLabel(
            form, text="", font=FONT_TINY, text_color=GRAY,
        )
        self._pass_strength.pack(anchor="w", pady=(0, 4))
        self._pass_entry.bind("<KeyRelease>", self._on_password_change)

        # Error display
        self._auth_error = ctk.CTkLabel(
            form, text="", font=FONT_TINY, text_color=RED, wraplength=450,
        )
        self._auth_error.pack(anchor="w", pady=(2, 8))

        # Submit button
        self._auth_submit_btn = ctk.CTkButton(
            form, text="Create Account →", font=("Segoe UI", 13, "bold"),
            fg_color=GOLD, text_color=BLACK, hover_color=GOLD_HOVER,
            height=42, command=self._handle_auth,
        )
        self._auth_submit_btn.pack(fill="x", pady=(8, 0))

        # Toggle text
        self._auth_alt = ctk.CTkLabel(
            form, text="Already have an account? Sign in",
            font=FONT_TINY, text_color=GRAY,
            cursor="hand2",
        )
        self._auth_alt.pack(pady=(12, 0))
        self._auth_alt.bind("<Button-1>", lambda e: self._toggle_auth("login"))

        return page

    def _toggle_auth(self, mode: str):
        self._auth_mode.set(mode)
        is_reg = mode == "register"

        for btn, is_active in [
            (self._auth_register_btn, is_reg),
            (self._auth_login_btn, not is_reg),
        ]:
            btn.configure(
                fg_color=GOLD if is_active else DARK,
                text_color=BLACK if is_active else GRAY,
            )

        self._name_entry.pack_forget()
        if is_reg:
            self._name_entry.pack(fill="x", pady=(4, 12))
            self._auth_alt.configure(text="Already have an account? Sign in")
            self._auth_submit_btn.configure(text="Create Account →")
        else:
            self._auth_alt.configure(text="Don't have an account? Create one")
            self._auth_submit_btn.configure(text="Sign In →")
        self._auth_error.configure(text="")

    def _on_password_change(self, event=None):
        """Real-time password strength indicator."""
        pwd = self._pass_entry.get()
        if not pwd:
            self._pass_strength.configure(text="")
            return
        strength = 0
        if len(pwd) >= 8:
            strength += 1
        if any(c.isupper() for c in pwd):
            strength += 1
        if any(c.isdigit() for c in pwd):
            strength += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in pwd):
            strength += 1
        labels = {0: "Weak", 1: "Fair", 2: "Good", 3: "Strong", 4: "Very Strong"}
        colors = {0: RED, 1: "#eab308", 2: GOLD, 3: GREEN, 4: GREEN}
        self._pass_strength.configure(
            text=f"Password strength: {labels.get(strength, 'Unknown')}",
            text_color=colors.get(strength, GRAY),
        )

    def _handle_auth(self):
        """Validate and submit authentication with thread-safe UI."""
        email = self._email_entry.get().strip()
        password = self._pass_entry.get()
        name = self._name_entry.get().strip() if self._auth_mode.get() == "register" else ""

        # ── Client-side Validation ────────────────────────────────────
        if not email:
            self._auth_error.configure(text="Email is required")
            self._email_entry.focus()
            return
        if "@" not in email or "." not in email.split("@")[-1]:
            self._auth_error.configure(text="Please enter a valid email address")
            self._email_entry.focus()
            return
        if not password:
            self._auth_error.configure(text="Password is required")
            self._pass_entry.focus()
            return
        if self._auth_mode.get() == "register" and len(password) < 6:
            self._auth_error.configure(text="Password must be at least 6 characters")
            self._pass_entry.focus()
            return
        if self._auth_mode.get() == "register" and not name:
            self._auth_error.configure(text="Name is required for registration")
            self._name_entry.focus()
            return

        self._auth_error.configure(text="")
        self._auth_submit_btn.configure(state="disabled", text="Connecting...")

        def _do():
            try:
                if self._auth_mode.get() == "register":
                    data = self._api.signup(email, password, name)
                else:
                    data = self._api.login(email, password)

                self._auth_token = data["access_token"]
                self._user_email = data["user"]["email"]
                self._user_name = data["user"].get("full_name", email.split("@")[0])

                self.after(0, self._on_auth_success)
            except APIError as e:
                self.after(0, lambda: self._on_auth_error(str(e)))
            except Exception as e:
                self.after(0, lambda: self._on_auth_error(f"Connection failed: {e}"))
            finally:
                self.after(0, lambda: self._auth_submit_btn.configure(
                    state="normal",
                    text="Create Account →" if self._auth_mode.get() == "register" else "Sign In →",
                ))

        threading.Thread(target=_do, daemon=True).start()

    def _on_auth_success(self):
        self._auth_error.configure(text="✓ Connected", text_color=GREEN)
        # Brief pause for user to see success, then advance
        self.after(300, lambda: self._show_page(2))

    def _on_auth_error(self, msg: str):
        self._auth_error.configure(text=msg)

    # ═══════════════════════════════════════════════════════════════════
    #  PAGE 2: CONFIGURATION
    # ═══════════════════════════════════════════════════════════════════

    def _page_config(self) -> ctk.CTkFrame:
        page = ctk.CTkScrollableFrame(self.container, fg_color=BLACK, corner_radius=0)
        page.pack_forget()

        title = ctk.CTkLabel(
            page, text="Configure your VPS",
            font=FONT_TITLE, text_color=WHITE,
        )
        title.pack(anchor="w", pady=(0, 4))

        subtitle = ctk.CTkLabel(
            page,
            text="Set your preferences below. All settings can be changed later\nafter installation from the management dashboard.",
            font=FONT_SMALL, text_color=GRAY, justify="left",
        )
        subtitle.pack(anchor="w", pady=(0, 24))

        self._config_entries = []
        self._config_last_frame = None

        # ── Tunnel Name ──────────────────────────────────────────────
        default_tunnel = "vps-" + os.environ.get("COMPUTERNAME", "node").lower().replace(" ", "-")
        self._config_section(page, "🌐 Tunnel Name", [
            "A unique public name for your VPS tunnel. Creates a URL like:",
            f"https://{default_tunnel}.getparakram.in",
        ], lambda: self._config_entry(
            "Enter tunnel name", default_tunnel,
        ))

        # ── Cloudflare Token ──────────────────────────────────────────
        token_frame = self._config_section(page, "🔑 Cloudflare Token (optional but recommended)", [
            "An API token lets the installer automatically configure your Cloudflare tunnel.",
            "Without it, you'll need to set up the tunnel manually after installation.",
        ])
        self._cf_token_entry = ctk.CTkEntry(
            token_frame, placeholder_text="Paste your Cloudflare API token or leave blank",
            height=36, font=FONT_MONO,
        )
        self._cf_token_entry.pack(fill="x", pady=(4, 4))

        guide_btn = ctk.CTkButton(
            token_frame, text="📘 How to create a Cloudflare token",
            font=FONT_TINY, fg_color="transparent",
            text_color=GOLD, hover_color=DARK,
            command=lambda: webbrowser.open(
                "https://developers.cloudflare.com/fundamentals/api/get-started/create-token/"
            ),
            cursor="hand2",
        )
        guide_btn.pack(anchor="w")

        # ── Dashboard Port ────────────────────────────────────────────
        port_frame = self._config_section(page, "📊 Dashboard Port", [
            "The management dashboard runs on this local port on your machine.",
            "Default 9876 is suitable for most users.",
        ])
        port_row = ctk.CTkFrame(port_frame, fg_color="transparent")
        port_row.pack(fill="x")
        self._port_var = tk.StringVar(value="9876")
        port_entry = ctk.CTkEntry(
            port_row, textvariable=self._port_var,
            width=120, height=36, font=FONT_MONO,
        )
        port_entry.pack(side="left")
        ctk.CTkLabel(
            port_row, text="(1024–65535)", font=FONT_TINY, text_color=GRAY,
        ).pack(side="left", padx=(8, 0))

        # ── Subscription Plan ─────────────────────────────────────────
        plan_frame = self._config_section(page, "⭐ Subscription Plan", [
            "Choose a plan. Free tier includes 1 VPS tunnel with basic dashboard.",
            "Upgrade anytime from the management dashboard.",
        ])

        self._plan_var = tk.StringVar(value="free")
        plans = [
            ("free",  "Free",  "$0/mo — 1 VPS, basic dashboard, manual Cloudflare setup"),
            ("edge",  "Edge",  "$9/mo — 5 VPS, custom domain, automatic tunnel setup, priority support"),
            ("fleet", "Fleet", "$49/mo — Unlimited VPS, API access, team management, SLA"),
        ]
        for val, name, desc in plans:
            row = ctk.CTkFrame(plan_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            rb = ctk.CTkRadioButton(
                row, text="", variable=self._plan_var, value=val,
                fg_color=GOLD, hover_color=GOLD_HOVER,
            )
            rb.pack(side="left", padx=(0, 8))
            ctk.CTkLabel(
                row, text=name, font=FONT_BODY,
                text_color=WHITE,
            ).pack(side="left")
            ctk.CTkLabel(
                row, text=desc, font=FONT_TINY, text_color=GRAY,
            ).pack(side="left", padx=(8, 0))

        # ── Leads Backend Configuration ────────────────────────────
        leads_frame = self._config_section(page, "🤖 Leads Backend (optional)", [
            "Deploy the Parakram Leads Intelligence backend on this VPS.",
            "Requires Docker Desktop. An OpenAI API key is needed for AI-powered analysis.",
            "Leave blank to skip leads backend deployment.",
        ])
        self._leads_entries: dict[str, ctk.CTkEntry] = {}

        leads_fields = [
            ("OPENAI_API_KEY", "OpenAI API Key (required for AI analysis)", "", True),
            ("SMTP_HOST", "SMTP Host", "smtp.gmail.com", False),
            ("SMTP_PORT", "SMTP Port", "587", False),
            ("SMTP_USER", "SMTP Username", "", False),
            ("SMTP_PASSWORD", "SMTP Password (app password)", "", True),
            ("PERSONAL_ALERT_EMAIL", "Alert Email (for notifications)", "", False),
        ]
        for key, label, default, is_password in leads_fields:
            row = ctk.CTkFrame(leads_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=label, font=FONT_SMALL, text_color=GRAY, width=180).pack(side="left")
            entry = ctk.CTkEntry(
                row, placeholder_text=default or f"Enter {label.split('(')[0].strip()}",
                height=32, font=FONT_MONO,
                show="•" if is_password else "",
            )
            if default:
                entry.insert(0, default)
            entry.pack(side="left", fill="x", expand=True, padx=(4, 0))
            self._leads_entries[key] = entry

        # ── Buttons ───────────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(page, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(24, 0))

        back_btn = ctk.CTkButton(
            btn_frame, text="← Back", font=FONT_BODY,
            fg_color=DARK, text_color=WHITE, hover_color=DARK_BORDER,
            width=100, height=40,
            command=lambda: self._show_page(1),
        )
        back_btn.pack(side="left")

        self._config_install_btn = ctk.CTkButton(
            btn_frame, text="Install Now →", font=("Segoe UI", 13, "bold"),
            fg_color=GOLD, text_color=BLACK, hover_color=GOLD_HOVER,
            width=160, height=44,
            command=self._on_install_click,
        )
        self._config_install_btn.pack(side="right")

        return page

    def _config_section(self, parent: ctk.CTkFrame, heading: str,
                        help_lines: list[str],
                        extra_widget_fn: Optional[callable] = None) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(frame, text=heading, font=FONT_HEADING, text_color=WHITE).pack(anchor="w")
        for line in help_lines:
            ctk.CTkLabel(frame, text=line, font=FONT_TINY, text_color=GRAY, wraplength=450).pack(anchor="w")

        if extra_widget_fn:
            return extra_widget_fn()

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="x", pady=(4, 0))
        self._config_last_frame = inner
        return inner

    def _config_entry(self, placeholder: str, default: str = "") -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self._config_last_frame, fg_color="transparent")
        frame.pack(fill="x", pady=(4, 0))
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, height=36, font=FONT_BODY)
        entry.insert(0, default)
        entry.pack(fill="x")
        self._config_entries.append(entry)
        return frame

    def _on_install_click(self):
        """Validate config and begin installation."""
        # ── Validate port ─────────────────────────────────────────────
        port_str = self._port_var.get().strip()
        try:
            port = int(port_str)
            if port < 1024 or port > 65535:
                raise ValueError("Port must be 1024–65535")
        except ValueError:
            self._port_var.set("9876")
            self._config_install_btn.configure(text="Invalid port — using 9876")
            self.after(2000, lambda: self._config_install_btn.configure(text="Install Now →"))
            return

        # ── Validate tunnel name ─────────────────────────────────────
        tunnel_entry = self._config_entries[0] if self._config_entries else None
        if tunnel_entry:
            tunnel_name = tunnel_entry.get().strip()
            if not tunnel_name:
                tunnel_entry.insert(0, "vps-" + os.environ.get("COMPUTERNAME", "node").lower())
            elif not tunnel_name.replace("-", "").replace("_", "").isalnum():
                self._config_install_btn.configure(text="Tunnel name: letters, numbers, hyphens only")
                self.after(2000, lambda: self._config_install_btn.configure(text="Install Now →"))
                return

        self._config_install_btn.configure(state="disabled", text="Starting installation...")
        self._subscription_plan = self._plan_var.get()
        self._show_page(3)

        # ── Collect leads config (in-memory only, not saved to disk) ──
        leads_config = {}
        if hasattr(self, "_leads_entries"):
            for key, entry in self._leads_entries.items():
                val = entry.get().strip()
                if val:
                    leads_config[key] = val
        # Auto-generate DB_PASSWORD and SECRET_KEY
        if "DB_PASSWORD" not in leads_config:
            import secrets as _secrets
            leads_config["DB_PASSWORD"] = _secrets.token_hex(16)
        if "SECRET_KEY" not in leads_config:
            import secrets as _secrets
            leads_config["SECRET_KEY"] = _secrets.token_hex(32)
        self._engine._config["leads_config"] = leads_config
        from core.setup_engine import audit
        audit("LEADS_CONFIG", f"Leads config collected: {', '.join(k for k in leads_config if not any(s in k for s in ['PASSWORD', 'KEY', 'TOKEN', 'SECRET']))}", "INFO")

        def _do():
            try:
                cf_token = self._cf_token_entry.get().strip() if hasattr(self, "_cf_token_entry") else ""
                result = self._engine.run_all(cloudflared_token=cf_token)
                self._install_result = result

                if result.get("success"):
                    # Handle subscription after successful install
                    if self._subscription_plan != "free" and self._auth_token:
                        self._state = InstallState.SUBSCRIBING
                        self.after(0, lambda: self._on_progress(85, "Activating subscription..."))
                        try:
                            from core.setup_engine import audit
                            self._api.token = self._auth_token
                            sub_data = self._api.create_vps_subscription(self._subscription_plan)
                            audit("SUBSCRIPTION_CREATED",
                                  f"Plan={self._subscription_plan}, id={sub_data.get('subscription_id', 'N/A')}",
                                  "INFO")
                        except Exception as e:
                            self._install_warnings.append(f"Subscription activation: {e}")

                    self.after(0, self._on_install_done)
                else:
                    errs = result.get("errors", [])
                    for e in errs:
                        self._install_errors.append(e)
                    self.after(0, self._on_install_failed)

            except Exception as e:
                self._install_errors.append(str(e))
                self.after(0, self._on_install_failed)

        threading.Thread(target=_do, daemon=True).start()

    # ═══════════════════════════════════════════════════════════════════
    #  PAGE 3: INSTALLATION PROGRESS
    # ═══════════════════════════════════════════════════════════════════

    def _page_install(self) -> ctk.CTkFrame:
        page = ctk.CTkFrame(self.container, fg_color=BLACK, corner_radius=0)

        ctk.CTkLabel(
            page, text="Installing",
            font=FONT_TITLE, text_color=WHITE,
        ).pack(anchor="w", pady=(0, 4))

        ctk.CTkLabel(
            page,
            text="Setting up your Parakram VPS. This typically takes 2–5 minutes.\n"
                 "Do not close this window or restart your computer during installation.",
            font=FONT_SMALL, text_color=GRAY, justify="left",
        ).pack(anchor="w", pady=(0, 32))

        # Progress bar
        self._progress = ctk.CTkProgressBar(page, width=560, height=10)
        self._progress.pack(pady=(0, 12))
        self._progress.set(0)

        # Status text
        self._status_label = ctk.CTkLabel(
            page, text="Pre-flight checks...", font=FONT_BODY, text_color=GRAY,
        )
        self._status_label.pack(pady=(0, 24))

        # Progress steps
        self._steps_frame = ctk.CTkFrame(page, fg_color="transparent")
        self._steps_frame.pack(fill="x", pady=(0, 16))
        self._step_statuses: dict[str, ctk.CTkLabel] = {}
        install_steps = [
            "Pre-flight Checks", "OpenSSH Server", "Management Dashboard",
            "Cloudflare Tunnel", "Auto-Start", "Start Dashboard",
            "Firewall Configuration", "Docker Desktop",
            "Leads Backend Deployment", "Leads Tunnel Route",
            "Post-Install Verification",
        ]
        for step_name in install_steps:
            row = ctk.CTkFrame(self._steps_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            indicator = ctk.CTkLabel(
                row, text="○", font=FONT_SMALL, text_color=GRAY, width=20,
            )
            indicator.pack(side="left")
            label = ctk.CTkLabel(
                row, text=step_name, font=FONT_SMALL, text_color=GRAY,
            )
            label.pack(side="left", padx=(4, 0))
            self._step_statuses[step_name] = indicator

        # Log output
        self._install_log = ctk.CTkTextbox(
            page, height=120, font=FONT_TINY,
            fg_color=DARK, text_color=GRAY,
        )
        self._install_log.pack(fill="x")
        self._install_log.insert("0.0", "  [SYSTEM] Waiting for installation to begin...\n")
        self._install_log.configure(state="disabled")

        return page

    def _on_progress(self, pct: int, status: str):
        """Thread-safe progress update."""
        self.after(0, lambda: self._progress.set(pct / 100))
        self.after(0, lambda: self._status_label.configure(text=status))

        # Update step indicators
        if "..." in status:
            step_name = status.split("...")[0].strip()
            if step_name in self._step_statuses:
                self.after(0, lambda n=step_name: self._step_statuses[n].configure(
                    text="⟳", text_color=GOLD
                ))
        elif status.endswith("!"):
            step_name = status.replace("!", "").strip()
            # Try to match step name
            for known_step in self._step_statuses:
                if known_step.lower() in status.lower() or status.lower() in known_step.lower():
                    self.after(0, lambda n=known_step: self._step_statuses[n].configure(
                        text="✓", text_color=GREEN
                    ))
                    break

        if hasattr(self, "_install_log"):
            self.after(0, lambda: self._log_install(status))

    def _log_install(self, msg: str):
        """Thread-safe log append."""
        try:
            self._install_log.configure(state="normal")
            self._install_log.insert("end", f"  [{time.strftime('%H:%M:%S')}] {msg}\n")
            self._install_log.see("end")
            self._install_log.configure(state="disabled")
        except Exception:
            pass

    def _on_install_done(self):
        """Installation completed successfully."""
        self._state = InstallState.COMPLETE
        # Mark all steps as completed
        for step_name in self._step_statuses:
            self._step_statuses[step_name].configure(text="✓", text_color=GREEN)
        self._progress.set(1.0)
        self._status_label.configure(text="Installation complete!", text_color=GREEN)
        self._log_install("✓ All steps completed successfully")
        self._log_install("✓ Parakram VPS is now operational")
        # Start heartbeat reporting to backend
        self._start_heartbeat()
        self.after(1000, lambda: self._show_page(4))

    def _on_install_failed(self):
        """Installation failed — show error state."""
        self._state = InstallState.FAILED
        self._status_label.configure(text="Installation encountered errors", text_color=RED)
        self._log_install(f"✗ Installation failed: {'; '.join(self._install_errors[-3:])}")
        self.after(1000, lambda: self._show_page(4))

    # ═══════════════════════════════════════════════════════════════════
    #  PAGE 4: COMPLETE
    # ═══════════════════════════════════════════════════════════════════

    def _page_complete(self) -> ctk.CTkFrame:
        page = ctk.CTkFrame(self.container, fg_color=BLACK, corner_radius=0)

        has_errors = len(self._install_errors) > 0

        if has_errors:
            icon = ctk.CTkLabel(
                page, text="⚠", font=("Segoe UI", 48),
                text_color="#eab308",
            )
            icon.pack(pady=(20, 4))
            ctk.CTkLabel(
                page, text="Installation Complete with Warnings",
                font=FONT_TITLE, text_color="#eab308",
            ).pack(pady=(0, 4))
        else:
            icon = ctk.CTkLabel(
                page, text="✓", font=("Segoe UI", 48),
                text_color=GREEN,
            )
            icon.pack(pady=(20, 4))
            ctk.CTkLabel(
                page, text="Your VPS is Ready",
                font=FONT_TITLE, text_color=WHITE,
            ).pack(pady=(0, 4))

        ctk.CTkLabel(
            page, text=f"Installed at {INSTALL_DIR}",
            font=FONT_SMALL, text_color=GRAY,
        ).pack(pady=(0, 20))

        # ── Credentials Box ────────────────────────────────────────────
        creds = ctk.CTkFrame(page, fg_color=DARK, corner_radius=12)
        creds.pack(fill="x", padx=20, pady=(0, 16))

        dashboard_port = (self._install_result or {}).get("dashboard_port", 9876)
        items = [
            ("📡 Dashboard", f"http://localhost:{dashboard_port}"),
            ("🔐 SSH", f"ssh {os.environ.get('USERNAME', 'user')}@localhost"),
            ("📁 Install Path", str(INSTALL_DIR)),
            ("👤 Account", self._user_email or "Local only"),
            ("⭐ Plan", self._subscription_plan.capitalize()),
        ]
        if self._install_result:
            recovered = self._install_result.get("checkpoint_recovered", [])
            if recovered:
                items.append(("♻ Recovery", f"{len(recovered)} steps recovered"))

        for label, value in items:
            row = ctk.CTkFrame(creds, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=3)
            ctk.CTkLabel(
                row, text=label, font=FONT_SMALL, text_color=GRAY, width=120,
            ).pack(side="left")
            ctk.CTkLabel(
                row, text=value, font=FONT_SMALL, text_color=WHITE,
            ).pack(side="left", padx=(8, 0))

        # ── Error/Warning Display ──────────────────────────────────────
        if self._install_errors:
            err_frame = ctk.CTkFrame(page, fg_color="#1a0a0a", corner_radius=8)
            err_frame.pack(fill="x", padx=20, pady=(0, 8))
            ctk.CTkLabel(
                err_frame, text="Issues Encountered",
                font=FONT_SMALL, text_color=RED, anchor="w",
            ).pack(padx=12, pady=(8, 4), anchor="w")

            err_text = ctk.CTkTextbox(
                err_frame, height=60, font=FONT_TINY,
                fg_color="transparent", text_color=RED,
            )
            err_text.pack(fill="x", padx=12, pady=(0, 8))
            for e in self._install_errors:
                err_text.insert("end", f"  ⚠ {e}\n")
            err_text.configure(state="disabled")

        if self._install_warnings:
            warn_frame = ctk.CTkFrame(page, fg_color="#1a1a0a", corner_radius=8)
            warn_frame.pack(fill="x", padx=20, pady=(0, 8))
            for w in self._install_warnings:
                ctk.CTkLabel(
                    warn_frame, text=f"  ⚡ {w}",
                    font=FONT_TINY, text_color="#eab308", wraplength=450,
                ).pack(anchor="w", padx=12, pady=2)

        # ── Actions ────────────────────────────────────────────────────
        action_frame = ctk.CTkFrame(page, fg_color="transparent")
        action_frame.pack(pady=(8, 0))

        ctk.CTkButton(
            action_frame, text="Open Dashboard",
            fg_color=GOLD, text_color=BLACK, hover_color=GOLD_HOVER,
            font=("Segoe UI", 13, "bold"), width=200, height=42,
            command=lambda: webbrowser.open(f"http://localhost:{dashboard_port}"),
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            action_frame, text="Finish",
            fg_color=DARK, text_color=WHITE, hover_color=DARK_BORDER,
            font=FONT_BODY, width=120, height=42,
            command=self._on_close,
        ).pack(side="left", padx=6)

        return page

    # ─── Auto-Update ────────────────────────────────────────────────────

    def _on_update_check_complete(self, update_info: Optional[UpdateInfo]):
        """Called from background thread when update check finishes."""
        if update_info is None:
            return
        self._update_info = update_info
        self.after(0, self._show_update_banner)

    def _show_update_banner(self):
        """Show update notification in the welcome page."""
        if not self._update_info:
            return
        from core.setup_engine import audit
        audit(
            "UPDATE_AVAILABLE",
            f"v{self._update_info.version} (critical={self._update_info.is_critical})",
            "INFO",
        )

    # ─── Heartbeat ────────────────────────────────────────────────────

    def _start_heartbeat(self):
        """Start heartbeat service after successful installation."""
        if not self._auth_token:
            return
        try:
            vps_id = self._engine.get_config("vps_id") or f"vps-{os.environ.get('COMPUTERNAME', 'unknown').lower()}"
            self._heartbeat = HeartbeatService(
                auth_token=self._auth_token,
                vps_id=vps_id,
                version="2.0.0",
                install_dir=INSTALL_DIR,
            )
            self._heartbeat.start()
        except Exception:
            pass

    # ─── Close ──────────────────────────────────────────────────────────

    def _on_close(self):
        """Graceful shutdown — release all resources."""
        from core.setup_engine import audit
        audit("APP_CLOSE", "User closed installer", "INFO")
        try:
            if self._heartbeat:
                self._heartbeat.stop()
        except Exception:
            pass
        try:
            self._api.close()
        except Exception:
            pass
        self.destroy()


# ═══════════════════════════════════════════════════════════════════════════
#  COMMAND-LINE INTERFACE
# ═══════════════════════════════════════════════════════════════════════════

def run_headless(args: list[str]):
    """Non-interactive installation with logging."""
    from core.setup_engine import SetupEngine, audit, log

    audit("HEADLESS_START", "Non-interactive installation", "INFO")

    token = ""
    leads_prefix = "--leads-"
    leads_config = {}
    import secrets as _secrets
    for arg in args:
        if arg.startswith("--token="):
            token = arg.split("=", 1)[1]
        elif arg.startswith(leads_prefix):
            key, val = arg[len(leads_prefix):].split("=", 1) if "=" in arg[len(leads_prefix):] else (arg[len(leads_prefix):], "")
            leads_config[key.upper()] = val
        elif arg == "--headless":
            continue

    engine = SetupEngine()
    if leads_config:
        if "DB_PASSWORD" not in leads_config:
            leads_config["DB_PASSWORD"] = _secrets.token_hex(16)
        if "SECRET_KEY" not in leads_config:
            leads_config["SECRET_KEY"] = _secrets.token_hex(32)
        engine._config["leads_config"] = leads_config
        audit("HEADLESS", f"Leads config provided: {', '.join(k for k in leads_config if not any(s in k for s in ['PASSWORD', 'KEY', 'TOKEN', 'SECRET']))}", "INFO")
    result = engine.run_all(cloudflared_token=token)

    if result.get("success"):
        port = result.get("dashboard_port", 9876)
        print(f"[OK] Installation complete.")
        print(f"[OK] Dashboard: http://localhost:{port}")
        if result.get("checkpoint_recovered"):
            print(f"[OK] Recovered {len(result['checkpoint_recovered'])} steps from checkpoint")
        sys.exit(0)
    else:
        for err in result.get("errors", []):
            print(f"[FAIL] {err}")
        sys.exit(1)


def run_uninstall():
    """Full uninstall with confirmation."""
    from core.setup_engine import SetupEngine, audit
    audit("UNINSTALL_START", "User requested uninstall", "INFO")
    print("[INFO] Uninstalling Parakram VPS...")
    engine = SetupEngine()
    result = engine.uninstall()
    for k, v in result.items():
        print(f"  {k}: {'✓' if v else '✗'}")
    print("[OK] Uninstall complete.")
    sys.exit(0)


def show_status():
    """Display installation status."""
    from core.setup_engine import SetupEngine, CONFIG_FILE, Checkpoint
    engine = SetupEngine()

    if not CONFIG_FILE.exists():
        print("[INFO] Parakram VPS is NOT installed.")
        sys.exit(0)

    config = engine.get_all_config()
    completed = Checkpoint.load()

    print(f"[OK] Parakram VPS is installed")
    print(f"     Version: {config.get('install_version', 'unknown')}")
    print(f"     Dashboard port: {config.get('dashboard_port', '9876')}")
    print(f"     Steps completed: {len(completed)}/{len(Checkpoint.STEPS)}")
    print(f"     Config: {CONFIG_FILE}")
    sys.exit(0)


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--headless" in args:
        run_headless(args)
    elif "--uninstall" in args:
        run_uninstall()
    elif "--status" in args:
        show_status()
    else:
        app = ParakramVPSInstaller()
