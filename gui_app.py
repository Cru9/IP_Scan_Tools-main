"""
================================================================================
IP_Scan_Tools - Suite de Monitoreo de Red, Wi-Fi, Seguridad & Velocidad
Propiedad y Desarrollo por: Ezequiel Díaz
Todos los derechos reservados © 2026 Ezequiel Díaz
================================================================================
"""

import os
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import threading
import webbrowser
import socket

from scanner import NetworkScanner
from port_scanner import scan_target_ports
from speed_tester import run_speedtest
from wifi_scanner import scan_wifi_networks, get_single_network_signal
from network_heartbeat import NetworkHeartbeat
from dns_whois import get_dns_info, get_whois_info

from PIL import Image, ImageTk

from theme_manager import ThemeManager, THEMES, DEFAULT_THEME_NAME

# Theme default configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

CATEGORY_OPTIONS = {
    "pc": "💻 Laptop / PC",
    "mobile": "📱 Smartphone / Tablet",
    "tv": "📺 Smart TV / Streaming",
    "printer": "🖨️ Impresora",
    "camera": "📹 Cámara IP / Seguridad",
    "router": "🌐 Router / Red",
    "other": "🤖 Servidor / IoT"
}

SUBNET_PRESETS = [
    "Auto (Local)"
]

class ScanIPApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Hide main window initially for splash screen
        self.withdraw()
        
        # Init Scanner, In-Memory State and Network Heartbeat
        self.wifi_networks = []
        self.custom_host_names = {}
        self.scanner = NetworkScanner(interval=30)
        self.heartbeat = NetworkHeartbeat(check_interval=3)
        self.heartbeat.register_callback(self._on_heartbeat_update)
        self.heartbeat.start()
        
        # Theme System Setup
        self.current_theme_name = DEFAULT_THEME_NAME
        self.theme = ThemeManager.get_theme(self.current_theme_name)
        ctk.set_appearance_mode(self.theme["appearance"])
        
        self.is_scanning_wifi = False
        
        # Window setup
        self.title("IP_Scan_Tools - Monitor de Red, Wifi, Seguridad & Velocidad (Propiedad de Ezequiel Díaz)")
        self.geometry("1380x840")
        self.minsize(1060, 680)
        
        self.configure(fg_color=self.theme["bg_main"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # 1. Header Frame
        self._create_header()
        
        # 2. Summary Cards Frame
        self._create_cards()
        
        # 3. Main Content Tabview
        self._create_tabview()
        
        # Style Treeview
        self._style_treeviews()
        
        # Initial load & schedule auto-refresh
        self.refresh_all()
        self.schedule_auto_refresh()
        
        # Launch Splash Screen
        SplashScreen(self)

    def _create_header(self):
        self.header_frame = ctk.CTkFrame(
            self, 
            corner_radius=16, 
            fg_color=self.theme["card_bg"],
            border_width=self.theme["card_border_width"],
            border_color=self.theme["card_border"]
        )
        self.header_frame.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="ew")
        self.header_frame.grid_columnconfigure(1, weight=1)

        # App Logo & Title
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="📡 IP_Scan_Tools", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.theme["accent_primary"]
        )
        self.title_label.grid(row=0, column=0, padx=(20, 10), pady=14)

        # Subtitle & Security Status & Ownership
        sub_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        sub_frame.grid(row=0, column=1, padx=10, pady=12, sticky="w")

        self.subtitle_label = ctk.CTkLabel(
            sub_frame, 
            text="Monitoreo de Red, Wifi, Subredes & Seguridad  |  Propiedad de Ezequiel Díaz", 
            font=ctk.CTkFont(size=12),
            text_color=self.theme["text_secondary"]
        )
        self.subtitle_label.pack(anchor="w")

        hb_row = ctk.CTkFrame(sub_frame, fg_color="transparent")
        hb_row.pack(anchor="w", pady=(3, 0))
        
        self.security_badge = ctk.CTkLabel(
            hb_row,
            text="🛡️ Red Segura (Sin amenazas)",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.theme["badge_online_fg"]
        )
        self.security_badge.pack(side="left", padx=(0, 15))

        self.internet_badge = ctk.CTkButton(
            hb_row,
            text="🌐 Internet: ⏳ Eval...",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=self.theme["card_border"],
            text_color=self.theme["badge_online_fg"],
            hover_color=self.theme["card_bg"],
            height=24,
            corner_radius=8,
            command=self.open_heartbeat_dialog
        )
        self.internet_badge.pack(side="left", padx=(0, 8))

        self.gateway_badge = ctk.CTkButton(
            hb_row,
            text="🌐 Router: ⏳ Eval...",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=self.theme["card_border"],
            text_color=self.theme["badge_online_fg"],
            hover_color=self.theme["card_bg"],
            height=24,
            corner_radius=8,
            command=self.open_heartbeat_dialog
        )
        self.gateway_badge.pack(side="left")

        # Subnet Selector, Theme Toggle & Action Buttons Frame
        btn_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=2, padx=20, pady=12)

        # Theme Switcher Dropdown
        self.theme_var = ctk.StringVar(value=self.current_theme_name)
        self.theme_dropdown = ctk.CTkOptionMenu(
            btn_frame,
            values=ThemeManager.get_theme_names(),
            variable=self.theme_var,
            width=175,
            fg_color=self.theme["accent_primary"],
            button_color=self.theme["accent_primary_hover"],
            button_hover_color=self.theme["accent_primary_hover"],
            command=self.toggle_theme
        )
        self.theme_dropdown.pack(side="left", padx=(0, 10))

        # Subnet Combo
        self.lbl_subnet = ctk.CTkLabel(btn_frame, text="Subred:", font=ctk.CTkFont(size=11), text_color=self.theme["text_secondary"])
        self.lbl_subnet.pack(side="left", padx=(0, 5))

        self.subnet_var = ctk.StringVar(value="Auto (Local)")
        self.subnet_entry = ctk.CTkComboBox(
            btn_frame, 
            values=SUBNET_PRESETS,
            variable=self.subnet_var,
            width=135,
            command=self.on_subnet_change,
            state="readonly"
        )
        self.subnet_entry.pack(side="left", padx=(0, 10))

        self.speedtest_btn = ctk.CTkButton(
            btn_frame, 
            text="⚡ SpeedTest", 
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.theme["accent_blue"],
            hover_color=self.theme["accent_blue_hover"],
            width=105,
            command=self.open_speedtest_dialog
        )
        self.speedtest_btn.pack(side="left", padx=(0, 10))

        self.traceroute_btn = ctk.CTkButton(
            btn_frame, 
            text="🛣️ Traceroute", 
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.theme["accent_purple"],
            hover_color=self.theme["accent_purple_hover"],
            width=110,
            command=self.open_traceroute_dialog
        )
        self.traceroute_btn.pack(side="left", padx=(0, 10))

        self.dns_whois_btn = ctk.CTkButton(
            btn_frame, 
            text="🌐 DNS/WHOIS", 
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.theme["accent_blue"],
            hover_color=self.theme["accent_blue_hover"],
            width=110,
            command=self.open_dns_whois_dialog
        )
        self.dns_whois_btn.pack(side="left", padx=(0, 10))

        self.scan_btn = ctk.CTkButton(
            btn_frame, 
            text="🔍 Escanear Red", 
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.theme["accent_secondary"],
            hover_color=self.theme["accent_secondary_hover"],
            width=125,
            command=self.trigger_scan
        )
        self.scan_btn.pack(side="left", padx=(0, 10))

        self.about_btn = ctk.CTkButton(
            btn_frame,
            text="ℹ️ Acerca de",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.theme["card_border"],
            hover_color=self.theme["accent_primary"],
            width=100,
            command=self.open_about_dialog
        )
        self.about_btn.pack(side="left")


    def toggle_theme(self, selected_theme_name):
        self.current_theme_name = selected_theme_name
        self.theme = ThemeManager.get_theme(selected_theme_name)
        
        ctk.set_appearance_mode(self.theme["appearance"])
        self.configure(fg_color=self.theme["bg_main"])
        
        # Apply theme updates across widgets
        self.header_frame.configure(
            fg_color=self.theme["card_bg"],
            border_color=self.theme["card_border"]
        )
        self.title_label.configure(text_color=self.theme["accent_primary"])
        self.subtitle_label.configure(text_color=self.theme["text_secondary"])
        self.lbl_subnet.configure(text_color=self.theme["text_secondary"])
        
        self.theme_dropdown.configure(
            fg_color=self.theme["accent_primary"],
            button_color=self.theme["accent_primary_hover"],
            button_hover_color=self.theme["accent_primary_hover"]
        )
        self.speedtest_btn.configure(
            fg_color=self.theme["accent_blue"],
            hover_color=self.theme["accent_blue_hover"]
        )
        self.traceroute_btn.configure(
            fg_color=self.theme["accent_purple"],
            hover_color=self.theme["accent_purple_hover"]
        )
        self.scan_btn.configure(
            fg_color=self.theme["accent_secondary"],
            hover_color=self.theme["accent_secondary_hover"]
        )
        self.about_btn.configure(fg_color=self.theme["card_border"])
        
        if hasattr(self, 'port_scan_btn'):
            self.port_scan_btn.configure(fg_color=self.theme["accent_secondary"], hover_color=self.theme["accent_secondary_hover"])
        if hasattr(self, 'ping_btn'):
            self.ping_btn.configure(fg_color=self.theme["accent_primary"], hover_color=self.theme["accent_primary_hover"])
        if hasattr(self, 'wifi_btn'):
            self.wifi_btn.configure(fg_color=self.theme["accent_secondary"], hover_color=self.theme["accent_secondary_hover"])
        if hasattr(self, 'wifi_monitor_btn'):
            self.wifi_monitor_btn.configure(fg_color=self.theme["accent_primary"], hover_color=self.theme["accent_primary_hover"])

        self._style_treeviews()
        self.refresh_all()

    def on_subnet_change(self, selected_val):
        valid, msg = self.scanner.set_custom_subnet(selected_val)
        if not valid:
            messagebox.showerror("Subred Inválida", msg)

    def _create_cards(self):
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.card_total_val = self._build_card(cards_frame, 0, "TOTAL DISPOSITIVOS", "0", self.theme["accent_primary"], "Subred Local Detectada")
        self.card_online_val = self._build_card(cards_frame, 1, "EN LÍNEA", "0", self.theme["accent_secondary"], "Respondiendo ICMP/ARP")
        self.card_offline_val = self._build_card(cards_frame, 2, "DESCONECTADOS", "0", self.theme["accent_danger"], "Inactivos o Fuera de Red")
        self.card_wifi_val = self._build_card(cards_frame, 3, "REDES WI-FI VISIBLES", "0", self.theme["accent_purple"], "Antenas Cercanas")

    def _build_card(self, parent, col, title, value, accent_color, subtext):
        card = ctk.CTkFrame(
            parent, 
            corner_radius=14, 
            border_width=self.theme["card_border_width"],
            fg_color=self.theme["card_bg"],
            border_color=self.theme["card_border"]
        )
        card.grid(row=0, column=col, padx=5, pady=5, sticky="ew")

        # Visual accent top border strip
        accent_bar = ctk.CTkFrame(card, height=4, fg_color=accent_color, corner_radius=2)
        accent_bar.pack(fill="x", padx=12, pady=(8, 0))

        lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=10, weight="bold"), text_color=self.theme["text_secondary"])
        lbl_title.pack(anchor="w", padx=16, pady=(8, 2))

        lbl_val = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=28, weight="bold"), text_color=accent_color)
        lbl_val.pack(anchor="w", padx=16, pady=(0, 2))
        
        lbl_sub = ctk.CTkLabel(card, text=subtext, font=ctk.CTkFont(size=9), text_color=self.theme["text_muted"])
        lbl_sub.pack(anchor="w", padx=16, pady=(0, 10))

        return lbl_val

    def _create_tabview(self):
        self.tabview = ctk.CTkTabview(self, corner_radius=15)
        self.tabview.grid(row=2, column=0, padx=20, pady=(10, 15), sticky="nsew")

        # Tab 1: Hosts
        self.tab_hosts = self.tabview.add("💻 Dispositivos Detectados")
        self._setup_hosts_tab()

        # Tab 2: Wifi
        self.tab_wifi = self.tabview.add("Wifi")
        self._setup_wifi_tab()

    def _setup_hosts_tab(self):
        self.tab_hosts.grid_columnconfigure(0, weight=1)
        self.tab_hosts.grid_rowconfigure(1, weight=1)

        filter_frame = ctk.CTkFrame(self.tab_hosts, fg_color="transparent")
        filter_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        filter_frame.grid_columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.load_hosts())
        self.search_entry = ctk.CTkEntry(
            filter_frame, 
            placeholder_text="🔎 Buscar por Nombre, IP, MAC, Categoría o Fabricante...",
            textvariable=self.search_var
        )
        self.search_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.status_var = ctk.StringVar(value="Todos los Estados")
        self.status_dropdown = ctk.CTkOptionMenu(
            filter_frame,
            values=["Todos los Estados", "online", "offline"],
            variable=self.status_var,
            command=lambda val: self.load_hosts()
        )
        self.status_dropdown.grid(row=0, column=1, padx=(0, 10))

        self.port_scan_btn = ctk.CTkButton(
            filter_frame, 
            text="🔌 Escanear Puertos", 
            fg_color="#10b981",
            hover_color="#059669",
            command=self.open_port_scan_dialog
        )
        self.port_scan_btn.grid(row=0, column=2, padx=(0, 10))

        self.ping_btn = ctk.CTkButton(
            filter_frame, 
            text="⚡ Ping Continuo (-t)", 
            fg_color="#06b6d4",
            hover_color="#0891b2",
            command=self.open_continuous_ping_dialog
        )
        self.ping_btn.grid(row=0, column=3, padx=(0, 10))

        self.os_ttl_btn = ctk.CTkButton(
            filter_frame, 
            text="🔍 Detectar OS (TTL)", 
            fg_color="#8b5cf6",
            hover_color="#7c3aed",
            command=self.detect_os_ttl
        )
        self.os_ttl_btn.grid(row=0, column=4, padx=(0, 10))

        tree_frame = ctk.CTkFrame(self.tab_hosts, fg_color="transparent")
        tree_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        columns = ("status", "category", "name", "ip", "mac", "vendor", "os", "latency", "last_seen")
        self.hosts_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="extended")

        # Configurar colores para las filas
        self.hosts_tree.tag_configure("online", foreground="#10b981") # Verde
        self.hosts_tree.tag_configure("offline", foreground="#ef4444") # Rojo

        self.hosts_tree.heading("status", text="Estado")
        self.hosts_tree.heading("category", text="Categoría")
        self.hosts_tree.heading("name", text="Nombre / Alias")
        self.hosts_tree.heading("ip", text="Dirección IP")
        self.hosts_tree.heading("mac", text="Dirección MAC")
        self.hosts_tree.heading("vendor", text="Fabricante")
        self.hosts_tree.heading("os", text="OS (TTL)")
        self.hosts_tree.heading("latency", text="Ping")
        self.hosts_tree.heading("last_seen", text="Última Vista")

        self.hosts_tree.column("status", width=90, anchor="center")
        self.hosts_tree.column("category", width=160, anchor="w")
        self.hosts_tree.column("name", width=180, anchor="w")
        self.hosts_tree.column("ip", width=120, anchor="center")
        self.hosts_tree.column("mac", width=140, anchor="center")
        self.hosts_tree.column("vendor", width=150, anchor="w")
        self.hosts_tree.column("os", width=140, anchor="center")
        self.hosts_tree.column("latency", width=80, anchor="center")
        self.hosts_tree.column("last_seen", width=140, anchor="center")

        scrollbar = ctk.CTkScrollbar(tree_frame, orientation="vertical", command=self.hosts_tree.yview)
        self.hosts_tree.configure(yscrollcommand=scrollbar.set)

        self.hosts_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.hosts_tree.bind("<Double-1>", lambda event: self.open_continuous_ping_dialog())
        self.hosts_tree.bind("<Button-3>", self._show_hosts_context_menu)
        self.hosts_tree.bind("<Button-2>", self._show_hosts_context_menu)
        self.hosts_tree.bind("<Control-c>", self._copy_tree_row)

    def _copy_tree_row(self, event=None):
        selected = self.hosts_tree.selection()
        if not selected:
            return
            
        lines = []
        for item in selected:
            values = self.hosts_tree.item(item, "values")
            if values:
                clean_values = [str(v).replace("🟢 ", "").replace("🔴 ", "") for v in values]
                lines.append(" \t ".join(clean_values))
                
        if lines:
            self.clipboard_clear()
            self.clipboard_append("\n".join(lines))
            messagebox.showinfo("Copiado", "La información seleccionada ha sido copiada al portapapeles.")

    def _setup_wifi_tab(self):
        self.tab_wifi.grid_columnconfigure(0, weight=1)
        self.tab_wifi.grid_rowconfigure(1, weight=1)

        action_frame = ctk.CTkFrame(self.tab_wifi, fg_color="transparent")
        action_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.wifi_btn = ctk.CTkButton(
            action_frame,
            text="📶 Escanear Redes Wifi y Cobertura",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669",
            command=self.trigger_wifi_scan
        )
        self.wifi_btn.pack(side="left")

        self.wifi_monitor_btn = ctk.CTkButton(
            action_frame,
            text="📊 Monitorear Cobertura en Vivo (1s)",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#06b6d4",
            hover_color="#0891b2",
            command=self.open_wifi_monitor_dialog
        )
        self.wifi_monitor_btn.pack(side="left", padx=10)

        legend_label = ctk.CTkLabel(
            action_frame,
            text="Mapa de Calor:  🟩🟩🟩 Zona Fuerte (75%-100%)    🟨🟨⬜ Zona Media (40%-74%)    🟥⬜⬜ Zona Débil (0%-39%)",
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8"
        )
        legend_label.pack(side="right", padx=10)

        tree_frame = ctk.CTkFrame(self.tab_wifi, fg_color="transparent")
        tree_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        columns = ("ssid", "bssid", "heatbar", "signal", "channel", "band", "auth", "last_seen")
        self.wifi_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

        self.wifi_tree.heading("ssid", text="Red Wifi (SSID)")
        self.wifi_tree.heading("bssid", text="MAC de Antena (BSSID)")
        self.wifi_tree.heading("heatbar", text="Barra Térmica de Cobertura")
        self.wifi_tree.heading("signal", text="Potencia")
        self.wifi_tree.heading("channel", text="Canal")
        self.wifi_tree.heading("band", text="Frecuencia / Banda")
        self.wifi_tree.heading("auth", text="Seguridad / Cifrado")
        self.wifi_tree.heading("last_seen", text="Última Detección")

        self.wifi_tree.column("ssid", width=180, anchor="w")
        self.wifi_tree.column("bssid", width=140, anchor="center")
        self.wifi_tree.column("heatbar", width=200, anchor="center")
        self.wifi_tree.column("signal", width=80, anchor="center")
        self.wifi_tree.column("channel", width=80, anchor="center")
        self.wifi_tree.column("band", width=110, anchor="center")
        self.wifi_tree.column("auth", width=150, anchor="center")
        self.wifi_tree.column("last_seen", width=130, anchor="center")

        scrollbar = ctk.CTkScrollbar(tree_frame, orientation="vertical", command=self.wifi_tree.yview)
        self.wifi_tree.configure(yscrollcommand=scrollbar.set)

        self.wifi_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.wifi_tree.bind("<Double-1>", lambda event: self.open_wifi_monitor_dialog())
        self.wifi_tree.bind("<Button-3>", self._show_wifi_context_menu)
        self.wifi_tree.bind("<Button-2>", self._show_wifi_context_menu)

    def _style_treeviews(self):
        ThemeManager.apply_treeview_style(self.theme)

    def refresh_all(self):
        self.load_stats()
        self.load_hosts()
        self.load_wifi()
        self.update_security_status()

    def schedule_auto_refresh(self):
        self.refresh_all()
        self.after(5000, self.schedule_auto_refresh)

    def update_security_status(self):
        threats = self.scanner.security_monitor.security_threats
        if threats:
            self.security_badge.configure(
                text=f"🚨 ALERTA: {len(threats)} amenaza(s) de red detectada(s)",
                text_color="#ef4444"
            )
        else:
            self.security_badge.configure(
                text="🛡️ Red Segura (Sin conflictos o spoofing)",
                text_color="#10b981"
            )

    def load_stats(self):
        total = len(self.scanner.hosts)
        online = sum(1 for h in self.scanner.hosts if h.get("status") == "online")
        offline = total - online
        wifi_count = len(self.wifi_networks)
        self.card_total_val.configure(text=str(total))
        self.card_online_val.configure(text=str(online))
        self.card_offline_val.configure(text=str(offline))
        self.card_wifi_val.configure(text=str(wifi_count))

        if self.scanner.is_scanning:
            self.scan_btn.configure(text="⚡ Escaneando...", state="disabled")
        else:
            self.scan_btn.configure(text="🔍 Escanear Red", state="normal")

    def load_hosts(self):
        search = self.search_var.get().strip().lower()
        status_val = self.status_var.get()
        status_filter = status_val if status_val != "Todos los Estados" else None

        hosts = []
        for h in self.scanner.hosts:
            h_copy = dict(h)
            if h_copy["mac"] in self.custom_host_names:
                override = self.custom_host_names[h_copy["mac"]]
                if override.get("name"):
                    h_copy["name"] = override["name"]
                if override.get("category"):
                    h_copy["category"] = override["category"]

            if status_filter == "online" and h_copy.get("status") != "online":
                continue
            if status_filter == "offline" and h_copy.get("status") != "offline":
                continue

            if search:
                match = (
                    search in h_copy["ip"].lower()
                    or search in h_copy["mac"].lower()
                    or search in h_copy["name"].lower()
                    or search in h_copy["vendor"].lower()
                    or search in h_copy["category"].lower()
                )
                if not match:
                    continue

            hosts.append(h_copy)

        existing_items = self.hosts_tree.get_children()
        existing_ips = {}
        for item in existing_items:
            vals = self.hosts_tree.item(item, "values")
            if vals and len(vals) > 3:
                existing_ips[vals[3]] = item

        for h in hosts:
            status_str = "🟢 En Línea" if h["status"] == "online" else "🔴 Off"
            name_str = h["name"] if h["name"] else "—"
            cat_key = h.get("category", "pc")
            category_str = CATEGORY_OPTIONS.get(cat_key, "💻 Laptop / PC")
            latency_str = f"⚡ {h['latency']} ms" if h["status"] == "online" and h["latency"] > 0 else "—"
            os_val = h.get("os", "—")

            new_values = (
                status_str,
                category_str,
                name_str,
                h["ip"],
                h["mac"],
                h["vendor"],
                os_val,
                latency_str,
                h["last_seen"]
            )

            if h["ip"] in existing_ips:
                item = existing_ips[h["ip"]]
                self.hosts_tree.item(item, values=new_values, tags=(h["status"],))
                del existing_ips[h["ip"]]
            else:
                self.hosts_tree.insert("", "end", values=new_values, tags=(h["status"],))

        for item in existing_ips.values():
            self.hosts_tree.delete(item)

    def detect_os_ttl(self):
        if getattr(self, "_is_detecting_os", False):
            return
        self.os_ttl_btn.configure(state="disabled", text="Detectando...")
        self._is_detecting_os = True
        
        def _task():
            import subprocess
            import re
            from concurrent.futures import ThreadPoolExecutor
            
            items = self.hosts_tree.get_children()
            active_items = []
            
            # Recolectar solo dispositivos en línea
            for item in items:
                values = list(self.hosts_tree.item(item, "values"))
                status = values[0]
                if "Off" not in status:
                    active_items.append((item, values))
            
            def check_os(data):
                item, values = data
                ip = values[3]
                os_result = "Sin respuesta"
                try:
                    res = subprocess.run(['ping', '-n', '1', '-w', '200', ip], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
                    if res.returncode == 0:
                        match = re.search(r'TTL=(\d+)', res.stdout, re.IGNORECASE)
                        if match:
                            ttl = int(match.group(1))
                            if ttl <= 64:
                                os_name = "Linux/Mac/Android"
                            elif ttl <= 128:
                                os_name = "Windows"
                            else:
                                os_name = "Router/Switch"
                            os_result = f"{os_name} (TTL:{ttl})"
                        else:
                            os_result = "TTL Oculto"
                except Exception:
                    pass
                return item, values, os_result

            # Ping concurrente muy rápido
            results = []
            if active_items:
                with ThreadPoolExecutor(max_workers=50) as executor:
                    results = list(executor.map(check_os, active_items))
                    
            def update_ui():
                for item, values, os_result in results:
                    ip = values[3]
                    try:
                        if len(values) > 6:
                            values[6] = os_result
                        else:
                            values.append(os_result)
                            
                        self.hosts_tree.item(item, values=values)
                        
                        # Guardar el valor en self.scanner.hosts para que el auto-refresh no lo borre
                        for h in self.scanner.hosts:
                            if h["ip"] == ip:
                                h["os"] = os_result
                                break
                    except Exception as e:
                        print(f"Error updating item {item}: {e}")
                self._is_detecting_os = False
                self.os_ttl_btn.configure(state="normal", text="🔍 Detectar OS (TTL)")
                
            self.after(0, update_ui)
            
        threading.Thread(target=_task, daemon=True).start()

    def load_wifi(self):
        wifi_list = self.wifi_networks

        for item in self.wifi_tree.get_children():
            self.wifi_tree.delete(item)

        for w in wifi_list:
            sig = w["signal"]
            ch = w.get("channel", 0)
            ch_str = f"Canal {ch}" if ch > 0 else "—"
            band_str = w.get("band", "Desconocido")
            
            # Generate Heatbar visual indicator
            if sig >= 75:
                heatbar = f"🟩🟩🟩🟩 Zona Fuerte ({sig}%)"
            elif sig >= 45:
                heatbar = f"🟨🟨🟨⬜ Zona Media ({sig}%)"
            else:
                heatbar = f"🟥🟥⬜⬜ Zona Débil ({sig}%)"

            self.wifi_tree.insert("", "end", values=(
                w["ssid"],
                w["bssid"],
                heatbar,
                f"{sig}%",
                ch_str,
                band_str,
                w["auth"],
                w.get("last_seen", "—")
            ))

    def open_wifi_monitor_dialog(self):
        selected_item = self.wifi_tree.selection()
        if not selected_item:
            messagebox.showwarning(
                "Seleccionar Red Wi-Fi",
                "Por favor selecciona una red Wi-Fi de la lista para iniciar el monitoreo de cobertura en tiempo real."
            )
            return
        
        row_values = self.wifi_tree.item(selected_item[0], "values")
        if not row_values:
            return
        
        target_network = {
            "ssid": row_values[0],
            "bssid": row_values[1],
            "heatbar": row_values[2],
            "signal_str": row_values[3],
            "channel_str": row_values[4],
            "band_str": row_values[5],
            "auth_str": row_values[6]
        }
        
        WiFiCoverageMonitorDialog(self, target_network)

    def open_dns_whois_dialog(self):
        DnsWhoisDialog(self)

    def trigger_scan(self):
        subnet_val = self.ip_range_entry.get() if hasattr(self, 'ip_range_entry') else self.subnet_var.get()
        valid, msg = self.scanner.set_custom_subnet(subnet_val)
        if not valid:
            messagebox.showerror("Subred Inválida", msg)
            return

        if not self.scanner.is_scanning:
            self.scan_btn.configure(text="⚡ Escaneando...", state="disabled")
            
            def _async_scan():
                self.scanner.perform_scan()
                self.after(0, self._on_scan_complete)
                
            threading.Thread(target=_async_scan, daemon=True).start()

    def _on_scan_complete(self):
        self.scan_btn.configure(text="🔍 Escanear Red", state="normal")
        self.load_hosts()
        self.load_stats()

    def trigger_wifi_scan(self):
        if not self.is_scanning_wifi:
            self.is_scanning_wifi = True
            self.wifi_btn.configure(text="⏳ Evaluando Cobertura y Redes Wifi...", state="disabled")
            
            def _async_wifi():
                networks = scan_wifi_networks()
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for net in networks:
                    net["last_seen"] = now_str
                self.wifi_networks = networks
                self.after(0, self._on_wifi_scan_complete)
                
            threading.Thread(target=_async_wifi, daemon=True).start()

    def _on_wifi_scan_complete(self):
        self.is_scanning_wifi = False
        self.wifi_btn.configure(text="📶 Escanear Redes Wifi y Cobertura", state="normal")
        self.load_wifi()

    def open_edit_dialog(self):
        selected = self.hosts_tree.selection()
        if not selected:
            messagebox.showwarning("Selección vacía", "Por favor selecciona un dispositivo de la lista para editar.")
            return

        values = self.hosts_tree.item(selected[0])["values"]
        cat_str = values[1]
        name_val = values[2] if values[2] != "—" else ""
        mac_val = values[4]

        cat_key = "pc"
        for k, v in CATEGORY_OPTIONS.items():
            if v == cat_str:
                cat_key = k
                break

        EditDeviceDialog(self, mac_val, name_val, cat_key, self.refresh_all)

    def open_continuous_ping_dialog(self):
        selected = self.hosts_tree.selection()
        if not selected:
            messagebox.showwarning("Selección vacía", "Por favor selecciona un dispositivo de la lista para hacer Ping Continuo (-t).")
            return

        values = self.hosts_tree.item(selected[0])["values"]
        if not values:
            return

        target_info = {
            "status": values[0],
            "category": values[1],
            "name": values[2],
            "ip": values[3],
            "mac": values[4],
            "vendor": values[5]
        }

        ContinuousPingDialog(self, target_info)

    def open_port_scan_dialog(self):
        selected = self.hosts_tree.selection()
        if not selected:
            messagebox.showwarning("Selección vacía", "Por favor selecciona un dispositivo de la lista para auditar sus puertos.")
            return

        values = self.hosts_tree.item(selected[0])["values"]
        name_val = values[2]
        ip_val = values[3]
        mac_val = values[4]

        PortScanDialog(self, ip_val, mac_val, name_val)

    def open_speedtest_dialog(self):
        SpeedTestDialog(self)

    def open_traceroute_dialog(self, target=None):
        if not target or target is True:
            selected = self.hosts_tree.selection()
            if selected:
                values = self.hosts_tree.item(selected[0])["values"]
                if values and len(values) > 3:
                    target = values[3]
                    
        if not target or target is True:
            target = "8.8.8.8"
            
        TracerouteDialog(self, default_target=target)

    def copy_to_clipboard(self, text, label="Texto"):
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("IP_Scan_Tools - Copiado", f"✅ {label} '{text}' copiado exitosamente al portapapeles.")

    def send_wake_on_lan(self, mac):
        try:
            mac_clean = mac.replace(":", "").replace("-", "")
            if len(mac_clean) != 12:
                messagebox.showerror("Error Wake-on-LAN", f"La dirección MAC '{mac}' no es válida.")
                return
                
            data = bytes.fromhex("FF" * 6 + mac_clean * 16)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(data, ("255.255.255.255", 9))
            sock.close()
            messagebox.showinfo("Wake-on-LAN Enviado", f"🔌 Paquete Mágico Wake-on-LAN enviado exitosamente a la MAC:\n{mac}")
        except Exception as e:
            messagebox.showerror("Error Wake-on-LAN", f"No se pudo enviar el paquete Wake-on-LAN:\n{e}")

    def _show_hosts_context_menu(self, event):
        item = self.hosts_tree.identify_row(event.y)
        if not item:
            return
            
        selected = self.hosts_tree.selection()
        if item not in selected:
            self.hosts_tree.selection_set(item)
            selected = (item,)
            
        values = self.hosts_tree.item(item, "values")
        if not values:
            return
            
        status_str, cat_str, name_str, ip, mac, vendor, os_str, latency_str, last_seen = values
        
        bg = "#1e293b" if self.current_theme_name == "Dark" else "#ffffff"
        fg = "#f8fafc" if self.current_theme_name == "Dark" else "#0f172a"
        active_bg = "#3b82f6"
        active_fg = "#ffffff"
        
        menu = tk.Menu(self, tearoff=0, bg=bg, fg=fg, activebackground=active_bg, activeforeground=active_fg, bd=1)
        
        if len(selected) == 1:
            header = f"💻 Dispositivo: {ip}" if name_str == "—" else f"💻 {name_str} ({ip})"
            menu.add_command(label=header, state="disabled")
            menu.add_separator()
            menu.add_command(label="⚡ Ping Continuo (-t)", command=self.open_continuous_ping_dialog)
            menu.add_command(label="🔍 Escanear Puertos TCP", command=self.open_port_scan_dialog)
            menu.add_command(label="🚀 Ejecutar Traceroute", command=lambda: self.open_traceroute_dialog(ip))
            menu.add_separator()
            menu.add_command(label="🌐 Abrir Panel Web (http://...)", command=lambda: webbrowser.open(f"http://{ip}"))
            menu.add_command(label="🔒 Abrir Panel Web Seguro (https://...)", command=lambda: webbrowser.open(f"https://{ip}"))
            menu.add_separator()
            menu.add_command(label="🔌 Enviar Wake-on-LAN (Encender PC)", command=lambda: self.send_wake_on_lan(mac))
            menu.add_separator()
        else:
            menu.add_command(label=f"💻 {len(selected)} dispositivos seleccionados", state="disabled")
            menu.add_separator()

        copy_menu = tk.Menu(menu, tearoff=0, bg=bg, fg=fg, activebackground=active_bg, activeforeground=active_fg, bd=1)
        copy_menu.add_command(label="Copiar Todo", command=self._copy_tree_row)
        
        if len(selected) == 1:
            copy_menu.add_command(label="Copiar Dirección IP", command=lambda: self.copy_to_clipboard(ip, "IP"))
            copy_menu.add_command(label="Copiar Dirección MAC", command=lambda: self.copy_to_clipboard(mac, "MAC"))
            
        menu.add_cascade(label="📋 Copiar Datos", menu=copy_menu)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _show_wifi_context_menu(self, event):
        item = self.wifi_tree.identify_row(event.y)
        if not item:
            return
        self.wifi_tree.selection_set(item)
        values = self.wifi_tree.item(item, "values")
        if not values:
            return
            
        ssid, bssid = values[0], values[1]
        
        bg = "#1e293b" if self.current_theme_name == "Dark" else "#ffffff"
        fg = "#f8fafc" if self.current_theme_name == "Dark" else "#0f172a"
        active_bg = "#06b6d4"
        active_fg = "#ffffff"
        
        menu = tk.Menu(self, tearoff=0, bg=bg, fg=fg, activebackground=active_bg, activeforeground=active_fg, bd=1)
        
        menu.add_command(label=f"📶 Red Wi-Fi: {ssid}", state="disabled")
        menu.add_separator()
        menu.add_command(label="📊 Monitorear Cobertura en Vivo (1s)", command=self.open_wifi_monitor_dialog)
        menu.add_separator()
        menu.add_command(label="📋 Copiar SSID (Nombre de Red)", command=lambda: self.copy_to_clipboard(ssid, "SSID"))
        menu.add_command(label="📋 Copiar BSSID (MAC de Antena)", command=lambda: self.copy_to_clipboard(bssid, "BSSID"))
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _on_heartbeat_update(self, hb):
        self.after(0, lambda: self._update_header_badges(hb))

    def _update_header_badges(self, hb):
        if not self.winfo_exists():
            return
            
        if hb.wan_online:
            if hb.wan_ms > 150:
                self.internet_badge.configure(text=f"🌐 Internet: 🟨 {hb.wan_ms} ms", text_color="#f59e0b")
            else:
                self.internet_badge.configure(text=f"🌐 Internet: 🟢 {hb.wan_ms} ms", text_color="#10b981")
        else:
            self.internet_badge.configure(text="🌐 Internet: 🔴 Caído", text_color="#ef4444")
            
        if hb.gateway_online:
            self.gateway_badge.configure(text=f"🌐 Router: 🟢 {hb.gateway_ms} ms", text_color="#10b981")
        else:
            self.gateway_badge.configure(text="🌐 Router: 🔴 Off", text_color="#ef4444")

    def open_heartbeat_dialog(self):
        NetworkHeartbeatDialog(self, self.heartbeat)

    def open_about_dialog(self):
        AboutDialog(self)



class SpeedTestDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("⚡ Test de Velocidad - IP_Scan_Tools")
        self.geometry("450x360")
        self.resizable(False, False)
        self.grab_set()

        lbl_title = ctk.CTkLabel(self, text="⚡ Medidor de Ancho de Banda", font=ctk.CTkFont(size=18, weight="bold"))
        lbl_title.pack(padx=20, pady=(20, 5))

        self.lbl_status = ctk.CTkLabel(self, text="Iniciando prueba de velocidad...", text_color="#38bdf8")
        self.lbl_status.pack(padx=20, pady=5)

        self.progress = ctk.CTkProgressBar(self, mode="indeterminate", width=350)
        self.progress.pack(padx=20, pady=15)
        self.progress.start()

        res_frame = ctk.CTkFrame(self, corner_radius=12)
        res_frame.pack(padx=20, pady=10, fill="both", expand=True)
        res_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(res_frame, text="📥 Descarga", font=ctk.CTkFont(size=11), text_color="#94a3b8").grid(row=0, column=0, padx=15, pady=(15, 2))
        self.lbl_dl = ctk.CTkLabel(res_frame, text="-- Mbps", font=ctk.CTkFont(size=20, weight="bold"), text_color="#10b981")
        self.lbl_dl.grid(row=1, column=0, padx=15, pady=(0, 15))

        ctk.CTkLabel(res_frame, text="📤 Subida", font=ctk.CTkFont(size=11), text_color="#94a3b8").grid(row=0, column=1, padx=15, pady=(15, 2))
        self.lbl_ul = ctk.CTkLabel(res_frame, text="-- Mbps", font=ctk.CTkFont(size=20, weight="bold"), text_color="#38bdf8")
        self.lbl_ul.grid(row=1, column=1, padx=15, pady=(0, 15))

        self.lbl_ping = ctk.CTkLabel(res_frame, text="Ping: -- ms | Servidor: --", text_color="#94a3b8", font=ctk.CTkFont(size=11))
        self.lbl_ping.grid(row=2, column=0, columnspan=2, padx=15, pady=(0, 15))

        self.btn_close = ctk.CTkButton(self, text="Cerrar", fg_color="#475569", command=self.destroy)
        self.btn_close.pack(padx=20, pady=(5, 15))

        threading.Thread(target=self._run_test, daemon=True).start()

    def _run_test(self):
        res = run_speedtest()
        self.after(0, lambda: self._update_ui(res))

    def _update_ui(self, res):
        self.progress.stop()
        self.progress.pack_forget()

        if res.get("success"):
            self.lbl_status.configure(text="✅ Prueba completada con éxito", text_color="#10b981")
            self.lbl_dl.configure(text=f"{res['download']} Mbps")
            self.lbl_ul.configure(text=f"{res['upload']} Mbps")
            self.lbl_ping.configure(text=f"Ping: {res['ping']} ms  |  Servidor: {res['server']}")
        else:
            self.lbl_status.configure(text="❌ Error al medir velocidad de red", text_color="#ef4444")


class PortScanDialog(ctk.CTkToplevel):
    def __init__(self, parent, ip, mac, name):
        super().__init__(parent)
        self.ip = ip
        self.mac = mac

        self.title(f"Escáner de Puertos - {ip}")
        self.geometry("700x420")
        self.resizable(False, False)
        self.grab_set()

        lbl_title = ctk.CTkLabel(self, text="🔌 Auditoría de Puertos Abiertos", font=ctk.CTkFont(size=16, weight="bold"))
        lbl_title.pack(padx=20, pady=(20, 2))

        lbl_target = ctk.CTkLabel(self, text=f"Objetivo: {name or 'Dispositivo'} ({ip} - {mac})", text_color="#38bdf8")
        lbl_target.pack(padx=20, pady=(0, 10))

        self.lbl_status = ctk.CTkLabel(self, text="⏳ Escaneando puertos principales...", text_color="#f59e0b")
        self.lbl_status.pack(padx=20, pady=5)

        tree_frame = ctk.CTkFrame(self, fg_color="transparent")
        tree_frame.pack(padx=20, pady=10, fill="both", expand=True)

        columns = ("port", "service", "banner")
        self.ports_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.ports_tree.heading("port", text="Puerto")
        self.ports_tree.heading("service", text="Servicio Detectado")
        self.ports_tree.heading("banner", text="Banner / Detalles")
        self.ports_tree.column("port", width=100, anchor="center")
        self.ports_tree.column("service", width=250, anchor="w")
        self.ports_tree.column("banner", width=300, anchor="w")

        scrollbar = ctk.CTkScrollbar(tree_frame, orientation="vertical", command=self.ports_tree.yview)
        self.ports_tree.configure(yscrollcommand=scrollbar.set)

        self.ports_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        btn_close = ctk.CTkButton(self, text="Cerrar Ventana", fg_color="#475569", command=self.destroy)
        btn_close.pack(padx=20, pady=(5, 15))

        threading.Thread(target=self._run_scan, daemon=True).start()

    def _run_scan(self):
        open_ports = scan_target_ports(self.ip)
        self.after(0, lambda: self._update_ui(open_ports))

    def _update_ui(self, open_ports):
        if not open_ports:
            self.lbl_status.configure(text="✅ Escaneo finalizado: No se encontraron puertos abiertos.", text_color="#10b981")
        else:
            self.lbl_status.configure(text=f"🚨 Escaneo finalizado: ¡Se encontraron {len(open_ports)} puertos abiertos!", text_color="#ef4444")
            for port, service, banner in open_ports:
                self.ports_tree.insert("", "end", values=(f"TCP {port}", service, banner))


class EditDeviceDialog(ctk.CTkToplevel):
    def __init__(self, parent, mac, name, category, on_save_callback):
        super().__init__(parent)
        self.mac = mac
        self.on_save_callback = on_save_callback

        self.title("Editar Dispositivo - IP_Scan_Tools")
        self.geometry("440x310")
        self.resizable(False, False)
        self.grab_set()

        lbl_title = ctk.CTkLabel(self, text="Editar Detalles de Dispositivo", font=ctk.CTkFont(size=16, weight="bold"))
        lbl_title.pack(padx=20, pady=(20, 2))

        lbl_mac = ctk.CTkLabel(self, text=f"MAC: {mac}", text_color="#38bdf8", font=ctk.CTkFont(size=12))
        lbl_mac.pack(padx=20, pady=(0, 15))

        lbl_name = ctk.CTkLabel(self, text="Nombre o Alias asignado:", anchor="w")
        lbl_name.pack(padx=20, fill="x")

        self.entry_name = ctk.CTkEntry(self, placeholder_text="Ej: Router Principal, Smart TV, iPhone")
        self.entry_name.insert(0, name)
        self.entry_name.pack(padx=20, pady=(5, 12), fill="x")

        lbl_cat = ctk.CTkLabel(self, text="Categoría de Dispositivo:", anchor="w")
        lbl_cat.pack(padx=20, fill="x")

        initial_cat_label = CATEGORY_OPTIONS.get(category, "💻 Laptop / PC")
        self.cat_var = ctk.StringVar(value=initial_cat_label)
        self.cat_dropdown = ctk.CTkOptionMenu(
            self,
            values=list(CATEGORY_OPTIONS.values()),
            variable=self.cat_var
        )
        self.cat_dropdown.pack(padx=20, pady=(5, 15), fill="x")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(padx=20, pady=15, fill="x")

        btn_cancel = ctk.CTkButton(btn_frame, text="Cancelar", fg_color="#475569", command=self.destroy)
        btn_cancel.pack(side="left", expand=True, padx=(0, 5))

        btn_save = ctk.CTkButton(btn_frame, text="Guardar Cambios", fg_color="#10b981", hover_color="#059669", command=self.save)
        btn_save.pack(side="right", expand=True, padx=(5, 0))

    def save(self):
        new_name = self.entry_name.get().strip()
        selected_cat_str = self.cat_var.get()
        
        cat_key = "pc"
        for k, v in CATEGORY_OPTIONS.items():
            if v == selected_cat_str:
                cat_key = k
                break
                
        if hasattr(self.master, "custom_host_names"):
            self.master.custom_host_names[self.mac] = {"name": new_name, "category": cat_key}
        if self.on_save_callback:
            self.on_save_callback()
        self.destroy()


class ContinuousPingDialog(ctk.CTkToplevel):
    def __init__(self, parent, target_info):
        super().__init__(parent)
        self.parent = parent
        self.target_info = target_info
        self.target_ip = target_info["ip"]
        
        self.title(f"⚡ Ping Continuo (-t) en Tiempo Real - {self.target_ip}")
        self.geometry("760x640")
        self.resizable(False, False)
        self.grab_set()
        
        self.is_pinging = True
        self.is_paused = False
        self.start_time = datetime.now()
        self.sent_count = 0
        self.received_count = 0
        self.lost_count = 0
        self.ping_times = []
        self.log_entries = []
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        # 1. Header Frame
        hdr_frame = ctk.CTkFrame(self, corner_radius=12)
        hdr_frame.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="ew")
        hdr_frame.grid_columnconfigure(0, weight=1)
        
        dev_title = target_info["name"] if target_info["name"] and target_info["name"] != "—" else target_info["vendor"]
        lbl_title = ctk.CTkLabel(
            hdr_frame, 
            text=f"🖥️ Host: {self.target_ip} ({dev_title})", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        lbl_title.grid(row=0, column=0, padx=15, pady=(10, 2), sticky="w")
        
        meta_str = f"MAC: {target_info['mac']}   |   Categoría: {target_info['category']}   |   Fabricante: {target_info['vendor']}"
        lbl_meta = ctk.CTkLabel(
            hdr_frame,
            text=meta_str,
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8"
        )
        lbl_meta.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")
        
        # 2. Stats Cards Grid
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        stats_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        self.val_current = self._build_stat_card(stats_frame, 0, "ACTUAL", "-- ms", "#10b981")
        self.val_min = self._build_stat_card(stats_frame, 1, "MÍNIMO", "-- ms", "#06b6d4")
        self.val_max = self._build_stat_card(stats_frame, 2, "MÁXIMO", "-- ms", "#f59e0b")
        self.val_avg = self._build_stat_card(stats_frame, 3, "PROMEDIO", "-- ms", "#3b82f6")
        self.val_loss = self._build_stat_card(stats_frame, 4, "PERDIDOS", "0 (0%)", "#ef4444")
        
        # 3. Status Bar Indicator
        self.status_bar = ctk.CTkLabel(
            self,
            text="🟢 Monitoreando respuesta ICMP (ping -t activo)...",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#10b981"
        )
        self.status_bar.grid(row=2, column=0, padx=20, pady=(5, 5), sticky="w")
        
        # 4. Terminal Log Console
        log_frame = ctk.CTkFrame(self, corner_radius=12)
        log_frame.grid(row=3, column=0, padx=20, pady=5, sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)
        
        lbl_log_title = ctk.CTkLabel(log_frame, text="💻 Consola de Salida de Ping (ping -t)", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_log_title.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        
        self.log_box = ctk.CTkTextbox(
            log_frame, 
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#090d16",
            text_color="#10b981"
        )
        self.log_box.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="nsew")
        
        # 5. Bottom Buttons Frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, padx=20, pady=(10, 15), sticky="ew")
        
        self.btn_pause = ctk.CTkButton(
            btn_frame,
            text="⏹️ Pausar Ping",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#f59e0b",
            hover_color="#d97706",
            width=130,
            command=self.toggle_pause
        )
        self.btn_pause.pack(side="left", padx=(0, 10))
        
        self.btn_export = ctk.CTkButton(
            btn_frame,
            text="📄 Exportar Bitácora",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669",
            width=140,
            command=self.export_log
        )
        self.btn_export.pack(side="left")
        
        self.btn_close = ctk.CTkButton(
            btn_frame,
            text="Cerrar",
            fg_color="#475569",
            hover_color="#334155",
            width=100,
            command=self.on_close
        )
        self.btn_close.pack(side="right")
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Start background ping thread
        threading.Thread(target=self._ping_loop, daemon=True).start()

    def _build_stat_card(self, parent, col, title, initial_val, color):
        card = ctk.CTkFrame(parent, corner_radius=10, border_width=1)
        card.grid(row=0, column=col, padx=3, pady=2, sticky="ew")
        
        lbl_t = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=9, weight="bold"), text_color="#94a3b8")
        lbl_t.pack(anchor="w", padx=8, pady=(8, 2))
        
        lbl_v = ctk.CTkLabel(card, text=initial_val, font=ctk.CTkFont(size=15, weight="bold"), text_color=color)
        lbl_v.pack(anchor="w", padx=8, pady=(0, 8))
        return lbl_v

    def _ping_loop(self):
        import platform
        import re
        import subprocess
        is_win = platform.system().lower() == "windows"
        
        while self.is_pinging:
            if self.is_paused:
                time.sleep(0.5)
                continue
                
            now_str = datetime.now().strftime("%H:%M:%S")
            self.sent_count += 1
            
            if is_win:
                cmd = ["ping", "-n", "1", "-w", "1000", self.target_ip]
            else:
                cmd = ["ping", "-c", "1", "-W", "1", self.target_ip]
                
            try:
                t0 = time.time()
                proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=2.5)
                dt = (time.time() - t0) * 1000.0
                
                success = False
                latency = 0
                ttl_val = None
                bytes_val = 32
                
                if proc.returncode == 0:
                    out = proc.stdout
                    
                    # En Windows, "Host inaccesible" también devuelve returncode=0.
                    # La única forma segura de saber si respondió es buscando el valor TTL.
                    match_ttl = re.search(r"TTL=(\d+)", out, re.IGNORECASE)
                    
                    if match_ttl:
                        ttl_val = match_ttl.group(1)
                        success = True
                        
                        match_time = re.search(r"(?:tiempo|time)[=<](\d+)ms", out, re.IGNORECASE)
                        if match_time:
                            latency = int(match_time.group(1))
                        elif "tiempo<1ms" in out or "time<1ms" in out or "<1ms" in out:
                            latency = 1
                        else:
                            latency = int(dt)
                
                if success:
                    self.received_count += 1
                    self.ping_times.append(latency)
                    ttl_str = f" TTL={ttl_val}" if ttl_val else ""
                    line = f"[{now_str}] Muestra #{self.sent_count:03d} -> Respuesta desde {self.target_ip}: bytes={bytes_val} tiempo={latency}ms{ttl_str}"
                else:
                    self.lost_count += 1
                    line = f"[{now_str}] Muestra #{self.sent_count:03d} -> Tiempo de espera agotado para esta solicitud. (Paquete Perdido ❌)"
                    
            except subprocess.TimeoutExpired:
                self.lost_count += 1
                line = f"[{now_str}] Muestra #{self.sent_count:03d} -> Tiempo de espera agotado. (Timeout ❌)"
            except Exception as e:
                self.lost_count += 1
                line = f"[{now_str}] Muestra #{self.sent_count:03d} -> Error de red: {e}"

            self.log_entries.append(line)
            
            self.after(0, lambda l=line, s=success, lat=latency: self._update_gui(l, s, lat))
            time.sleep(1.0)

    def _update_gui(self, line, success, latency):
        if not self.winfo_exists():
            return
            
        if success:
            self.val_current.configure(text=f"{latency} ms")
            if latency < 50:
                self.val_current.configure(text_color="#10b981")
            elif latency < 150:
                self.val_current.configure(text_color="#f59e0b")
            else:
                self.val_current.configure(text_color="#ef4444")
        else:
            self.val_current.configure(text="PERDIDO", text_color="#ef4444")
            
        if self.ping_times:
            min_p = min(self.ping_times)
            max_p = max(self.ping_times)
            avg_p = sum(self.ping_times) / len(self.ping_times)
            
            self.val_min.configure(text=f"{min_p} ms")
            self.val_max.configure(text=f"{max_p} ms")
            self.val_avg.configure(text=f"{avg_p:.1f} ms")
            
        loss_pct = (self.lost_count / self.sent_count * 100.0) if self.sent_count > 0 else 0.0
        self.val_loss.configure(text=f"{self.lost_count} ({loss_pct:.0f}%)")
        
        if loss_pct > 20:
            self.status_bar.configure(text="🚨 Conexión Inestable: Alta pérdida de paquetes", text_color="#ef4444")
        elif loss_pct > 0:
            self.status_bar.configure(text="🟨 Conexión con Fluctuación: Paquetes perdidos detectados", text_color="#f59e0b")
        else:
            self.status_bar.configure(text=f"🟢 Conexión Estable con {self.target_ip} (0% pérdida)", text_color="#10b981")
            
        self.log_box.insert("end", line + "\n")
        self.log_box.see("end")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.btn_pause.configure(text="▶️ Reanudar Ping", fg_color="#10b981", hover_color="#059669")
            self.status_bar.configure(text="⏸️ Ping Continuo Pausado", text_color="#f59e0b")
        else:
            self.btn_pause.configure(text="⏹️ Pausar Ping", fg_color="#f59e0b", hover_color="#d97706")
            self.status_bar.configure(text=f"🟢 Monitoreando respuesta ICMP con {self.target_ip}...", text_color="#10b981")

    def export_log(self):
        if not self.log_entries:
            messagebox.showwarning("Sin Datos", "No hay datos de ping recolectados para exportar.")
            return
            
        now_dt = datetime.now()
        date_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
        elapsed_sec = int((now_dt - self.start_time).total_seconds())
        mins, secs = divmod(elapsed_sec, 60)
        
        min_p = min(self.ping_times) if self.ping_times else 0
        max_p = max(self.ping_times) if self.ping_times else 0
        avg_p = (sum(self.ping_times) / len(self.ping_times)) if self.ping_times else 0
        loss_pct = (self.lost_count / self.sent_count * 100.0) if self.sent_count > 0 else 0.0
        
        report = f"""================================================================================
              BITÁCORA DE PING CONTINUO EN TIEMPO REAL (ping -t)
          Scan IP - Sistema de Monitoreo, Cobertura & Diagnóstico de Red
                         Propiedad de Ezequiel Díaz
================================================================================

Fecha y Hora de Inicio : {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
Fecha y Hora de Cierre : {date_str}
Tiempo Transcurrido    : {mins:02d}m {secs:02d}s ({elapsed_sec} segundos)

--- DATOS DEL DISPOSITIVO OBJETIVO ---
Dirección IP           : {self.target_ip}
Nombre / Alias         : {self.target_info['name']}
Dirección MAC          : {self.target_info['mac']}
Categoría              : {self.target_info['category']}
Fabricante             : {self.target_info['vendor']}

--- ESTADÍSTICAS Y RENDIMIENTO ICMP ---
Paquetes Enviados      : {self.sent_count}
Paquetes Recibidos     : {self.received_count}
Paquetes Perdidos      : {self.lost_count} ({loss_pct:.1f}% pérdida)
Tiempo Mínimo (Ping)   : {min_p} ms
Tiempo Máximo (Ping)   : {max_p} ms
Tiempo Promedio (Ping) : {avg_p:.1f} ms

--- REGISTRO DE SALIDA PAQUETE A PAQUETE ---
"""
        for line in self.log_entries:
            report += line + "\n"
            
        report += "\n================================================================================\n"
        report += "Fin de Bitácora de Ping - Scan IP (Propiedad de Ezequiel Díaz)\n"
        
        filename = f"Reporte_Ping_{self.target_ip.replace('.', '_')}_{now_dt.strftime('%Y%m%d_%H%M%S')}.txt"
        save_path = os.path.join(os.path.dirname(__file__), filename)
        
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(report)
            messagebox.showinfo(
                "Bitácora Exportada",
                f"La bitácora de ping continuo fue guardada exitosamente en:\n\n{save_path}"
            )
        except Exception as e:
            messagebox.showerror("Error al Exportar", f"No se pudo guardar la bitácora: {e}")

    def on_close(self):
        self.is_pinging = False
        self.destroy()


class WiFiCoverageMonitorDialog(ctk.CTkToplevel):
    def __init__(self, parent, target_net):
        super().__init__(parent)
        self.parent = parent
        self.target_net = target_net
        
        self.title(f"📊 Monitoreo de Cobertura en Vivo (1s) - {target_net['ssid']}")
        self.geometry("760x640")
        self.resizable(False, False)
        self.grab_set()
        
        self.is_monitoring = True
        self.start_time = datetime.now()
        self.readings = []  # list of dicts: {"time": "HH:MM:SS", "signal": 85, "channel": 44, "band": "5 GHz"}
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        # 1. Header Frame
        hdr_frame = ctk.CTkFrame(self, corner_radius=12)
        hdr_frame.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="ew")
        hdr_frame.grid_columnconfigure(0, weight=1)
        
        lbl_title = ctk.CTkLabel(
            hdr_frame, 
            text=f"📡 Red: {target_net['ssid']}", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        lbl_title.grid(row=0, column=0, padx=15, pady=(10, 2), sticky="w")
        
        meta_str = f"MAC: {target_net['bssid']}   |   {target_net['channel_str']}   |   {target_net['band_str']}   |   Seguridad: {target_net['auth_str']}"
        lbl_meta = ctk.CTkLabel(
            hdr_frame,
            text=meta_str,
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8"
        )
        lbl_meta.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")
        
        # 2. Live Signal Meter Frame
        meter_frame = ctk.CTkFrame(self, corner_radius=12)
        meter_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        lbl_meter_title = ctk.CTkLabel(
            meter_frame, 
            text="MEDIDOR DE COBERTURA EN TIEMPO REAL (Muestreo cada 1s)", 
            font=ctk.CTkFont(size=10, weight="bold"), 
            text_color="#94a3b8"
        )
        lbl_meter_title.pack(anchor="w", padx=15, pady=(10, 2))
        
        self.lbl_current_signal = ctk.CTkLabel(
            meter_frame,
            text="-- %",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#10b981"
        )
        self.lbl_current_signal.pack(anchor="w", padx=15, pady=(0, 2))
        
        self.progress_bar = ctk.CTkProgressBar(meter_frame, height=18)
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 12))
        self.progress_bar.set(0.0)
        
        # 3. Stats Cards Grid
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        stats_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        self.val_min = self._build_stat_card(stats_frame, 0, "MÍNIMA", "-- %", "#ef4444")
        self.val_max = self._build_stat_card(stats_frame, 1, "MÁXIMA", "-- %", "#10b981")
        self.val_avg = self._build_stat_card(stats_frame, 2, "PROMEDIO", "-- %", "#0284c7")
        self.val_samples = self._build_stat_card(stats_frame, 3, "MUESTRAS", "0", "#8b5cf6")
        self.val_time = self._build_stat_card(stats_frame, 4, "TIEMPO", "00:00", "#f59e0b")
        
        # 4. Real-time Reading Log
        log_frame = ctk.CTkFrame(self, corner_radius=12)
        log_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)
        
        lbl_log_title = ctk.CTkLabel(log_frame, text="📜 Historial de Lecturas de Cobertura (1s)", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_log_title.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        
        self.log_box = ctk.CTkTextbox(log_frame, font=ctk.CTkFont(family="Consolas", size=11))
        self.log_box.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="nsew")
        
        # 5. Bottom Buttons Frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, padx=20, pady=(0, 15), sticky="ew")
        
        self.btn_stop = ctk.CTkButton(
            btn_frame,
            text="📄 Detener y Guardar Reporte",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669",
            command=self.stop_and_generate_report
        )
        self.btn_stop.pack(side="left")
        
        self.btn_close = ctk.CTkButton(
            btn_frame,
            text="Cerrar",
            fg_color="#475569",
            hover_color="#334155",
            command=self.on_close
        )
        self.btn_close.pack(side="right")
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Start background polling thread
        threading.Thread(target=self._polling_loop, daemon=True).start()

    def _build_stat_card(self, parent, col, title, initial_val, color):
        card = ctk.CTkFrame(parent, corner_radius=10, border_width=1)
        card.grid(row=0, column=col, padx=3, pady=2, sticky="ew")
        
        lbl_t = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=9, weight="bold"), text_color="#94a3b8")
        lbl_t.pack(anchor="w", padx=8, pady=(8, 2))
        
        lbl_v = ctk.CTkLabel(card, text=initial_val, font=ctk.CTkFont(size=15, weight="bold"), text_color=color)
        lbl_v.pack(anchor="w", padx=8, pady=(0, 8))
        return lbl_v

    def _polling_loop(self):
        target_bssid = self.target_net["bssid"]
        target_ssid = self.target_net["ssid"]
        
        while self.is_monitoring:
            info = get_single_network_signal(target_bssid=target_bssid, target_ssid=target_ssid)
            now_str = datetime.now().strftime("%H:%M:%S")
            
            sig = info["signal"] if info else 0
            ch = info["channel"] if info else 0
            band = info["band"] if info else "Desconocido"
            
            reading = {
                "time": now_str,
                "signal": sig,
                "channel": ch,
                "band": band
            }
            self.readings.append(reading)
            
            # Schedule GUI update safely on main thread
            self.after(0, lambda r=reading: self._update_gui(r))
            time.sleep(1.0)

    def _update_gui(self, reading):
        if not self.winfo_exists():
            return
            
        sig = reading["signal"]
        
        # Update current signal label and progress bar
        self.lbl_current_signal.configure(text=f"{sig}%")
        self.progress_bar.set(sig / 100.0)
        
        if sig >= 75:
            self.progress_bar.configure(progress_color="#10b981")
            self.lbl_current_signal.configure(text_color="#10b981")
            zone_str = "Zona Fuerte 🟩"
        elif sig >= 45:
            self.progress_bar.configure(progress_color="#f59e0b")
            self.lbl_current_signal.configure(text_color="#f59e0b")
            zone_str = "Zona Media 🟨"
        else:
            self.progress_bar.configure(progress_color="#ef4444")
            self.lbl_current_signal.configure(text_color="#ef4444")
            zone_str = "Zona Débil 🟥"
            
        # Update metrics
        signals = [r["signal"] for r in self.readings if r["signal"] > 0]
        if signals:
            min_s = min(signals)
            max_s = max(signals)
            avg_s = sum(signals) / len(signals)
            
            self.val_min.configure(text=f"{min_s}%")
            self.val_max.configure(text=f"{max_s}%")
            self.val_avg.configure(text=f"{avg_s:.1f}%")
        
        self.val_samples.configure(text=str(len(self.readings)))
        
        elapsed_sec = int((datetime.now() - self.start_time).total_seconds())
        mins, secs = divmod(elapsed_sec, 60)
        self.val_time.configure(text=f"{mins:02d}:{secs:02d}")
        
        # Append line to log box
        ch_text = f"Canal {reading['channel']}" if reading['channel'] > 0 else "Canal --"
        log_line = f"[{reading['time']}] Muestra #{len(self.readings):03d} -> Potencia: {sig:3d}%  |  {ch_text} ({reading['band']})  |  {zone_str}\n"
        
        self.log_box.insert("end", log_line)
        self.log_box.see("end")

    def stop_and_generate_report(self):
        self.is_monitoring = False
        self.btn_stop.configure(state="disabled", text="✅ Reporte Generado")
        
        if not self.readings:
            messagebox.showwarning("Sin Muestras", "No se recolectaron muestras suficientes para generar el reporte.")
            return
            
        signals = [r["signal"] for r in self.readings]
        valid_signals = [s for s in signals if s > 0]
        
        min_s = min(valid_signals) if valid_signals else 0
        max_s = max(valid_signals) if valid_signals else 0
        avg_s = sum(valid_signals) / len(valid_signals) if valid_signals else 0
        
        # Stability index assessment
        diff = max_s - min_s
        if diff <= 5:
            stability_str = "EXCELENTE (Señal altamente estable, variaciones mínimas)"
        elif diff <= 15:
            stability_str = "ACEPTABLE / ESTABLE (Fluctuaciones normales del entorno)"
        else:
            stability_str = "INESTABLE / CON INTERFERENCIA (Variaciones drásticas de señal)"
            
        now_dt = datetime.now()
        date_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
        elapsed_sec = int((now_dt - self.start_time).total_seconds())
        mins, secs = divmod(elapsed_sec, 60)
        
        # Build Report Text
        report_text = f"""================================================================================
               REPORTE TÉCNICO DE EVALUACIÓN DE COBERTURA WI-FI
          Scan IP - Sistema de Monitoreo, Cobertura & Diagnóstico de Red
                         Propiedad de Ezequiel Díaz
================================================================================

Fecha y Hora de Evaluación: {date_str}

--- DATOS DE LA RED EVALUADA ---
Red Wi-Fi (SSID)       : {self.target_net['ssid']}
Dirección MAC (BSSID)  : {self.target_net['bssid']}
Canal de Transmisión   : {self.target_net['channel_str']}
Banda de Frecuencia    : {self.target_net['band_str']}
Seguridad / Cifrado    : {self.target_net['auth_str']}

--- MÉTRICAS Y ANÁLISIS DE COBERTURA ---
Tiempo de Monitoreo    : {mins:02d}m {secs:02d}s ({elapsed_sec} segundos)
Muestras Recolectadas  : {len(self.readings)} lecturas (Frecuencia: 1 muestra/segundo)
Potencia Inicial       : {signals[0]}%
Potencia Final         : {signals[-1]}%
Potencia Mínima        : {min_s}%
Potencia Máxima        : {max_s}%
Potencia Promedio      : {avg_s:.1f}%
Índice de Estabilidad  : {stability_str}

--- REGISTRO DETALLADO SEGUNDO A SEGUNDO ---
"""
        for i, r in enumerate(self.readings, start=1):
            s = r["signal"]
            zone = "Zona Fuerte (🟩)" if s >= 75 else ("Zona Media (🟨)" if s >= 45 else "Zona Débil (🟥)")
            ch_str = f"Canal {r['channel']}" if r['channel'] > 0 else "Canal --"
            report_text += f"[{r['time']}] Muestra #{i:03d} -> Potencia: {s:3d}% | {ch_str:<9} ({r['band']:<7}) | {zone}\n"

        report_text += "\n================================================================================\n"
        report_text += "Fin del Reporte de Cobertura - Scan IP (Propiedad de Ezequiel Díaz)\n"
        
        # Save file to project workspace
        safe_ssid = "".join(c for c in self.target_net['ssid'] if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
        filename = f"Reporte_Cobertura_{safe_ssid}_{now_dt.strftime('%Y%m%d_%H%M%S')}.txt"
        save_path = os.path.join(os.path.dirname(__file__), filename)
        
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(report_text)
            messagebox.showinfo(
                "Reporte de Cobertura Generado",
                f"El reporte de cobertura ha sido guardado exitosamente en:\n\n{save_path}"
            )
        except Exception as e:
            messagebox.showerror("Error al Guardar Reporte", f"No se pudo guardar el archivo: {e}")

    def on_close(self):
        self.is_monitoring = False
        self.destroy()


class TracerouteDialog(ctk.CTkToplevel):
    def __init__(self, parent, default_target="8.8.8.8"):
        super().__init__(parent)
        self.parent = parent
        
        self.title("🛣️ Herramienta Traceroute / MTR - Rastreo de Ruta & Congestión")
        self.geometry("840x680")
        self.resizable(False, False)
        self.grab_set()
        
        self.is_tracing = False
        self.start_time = None
        self.target_host = ""
        self.hop_data = []
        self.raw_logs = []
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # 1. Target Input Header Frame
        hdr_frame = ctk.CTkFrame(self, corner_radius=12)
        hdr_frame.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="ew")
        hdr_frame.grid_columnconfigure(1, weight=1)
        
        lbl_target = ctk.CTkLabel(hdr_frame, text="🌐 Host / IP Destino:", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_target.grid(row=0, column=0, padx=(15, 5), pady=12)
        
        self.entry_target = ctk.CTkEntry(
            hdr_frame,
            placeholder_text="Ej: google.com, 8.8.8.8 o 192.168.1.1"
        )
        self.entry_target.insert(0, default_target)
        self.entry_target.grid(row=0, column=1, padx=5, pady=12, sticky="ew")
        
        self.btn_start = ctk.CTkButton(
            hdr_frame,
            text="▶️ Iniciar Rastreo",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#8b5cf6",
            hover_color="#7c3aed",
            width=140,
            command=self.start_traceroute
        )
        self.btn_start.grid(row=0, column=2, padx=(5, 15), pady=12)
        
        # 2. Status Label
        self.lbl_status = ctk.CTkLabel(
            self,
            text="💡 Ingrese una IP o Dominio y presione 'Iniciar Rastreo' para evaluar la ruta de red.",
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8"
        )
        self.lbl_status.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="w")
        
        # 3. Hop Table Frame
        tree_frame = ctk.CTkFrame(self, corner_radius=12)
        tree_frame.grid(row=2, column=0, padx=20, pady=5, sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        columns = ("hop", "ip", "hostname", "p1", "p2", "p3", "status")
        self.hops_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        self.hops_tree.heading("hop", text="Salto #")
        self.hops_tree.heading("ip", text="Dirección IP de Router")
        self.hops_tree.heading("hostname", text="Nombre de Host / Proveedor")
        self.hops_tree.heading("p1", text="Ping 1")
        self.hops_tree.heading("p2", text="Ping 2")
        self.hops_tree.heading("p3", text="Ping 3")
        self.hops_tree.heading("status", text="Diagnóstico de Salto")
        
        self.hops_tree.column("hop", width=60, anchor="center")
        self.hops_tree.column("ip", width=140, anchor="center")
        self.hops_tree.column("hostname", width=180, anchor="w")
        self.hops_tree.column("p1", width=75, anchor="center")
        self.hops_tree.column("p2", width=75, anchor="center")
        self.hops_tree.column("p3", width=75, anchor="center")
        self.hops_tree.column("status", width=170, anchor="center")
        
        scrollbar = ctk.CTkScrollbar(tree_frame, orientation="vertical", command=self.hops_tree.yview)
        self.hops_tree.configure(yscrollcommand=scrollbar.set)
        
        self.hops_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # 4. Console Output Box
        log_frame = ctk.CTkFrame(self, corner_radius=12)
        log_frame.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        log_frame.grid_columnconfigure(0, weight=1)
        
        self.log_box = ctk.CTkTextbox(
            log_frame,
            height=110,
            font=ctk.CTkFont(family="Consolas", size=10),
            fg_color="#090d16",
            text_color="#38bdf8"
        )
        self.log_box.grid(row=0, column=0, padx=10, pady=8, sticky="ew")
        
        # 5. Bottom Buttons Frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, padx=20, pady=(5, 15), sticky="ew")
        
        self.btn_export = ctk.CTkButton(
            btn_frame,
            text="📄 Exportar Reporte de Ruta",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#06b6d4",
            hover_color="#0891b2",
            width=180,
            command=self.export_report
        )
        self.btn_export.pack(side="left")
        
        self.btn_close = ctk.CTkButton(
            btn_frame,
            text="Cerrar",
            fg_color="#475569",
            hover_color="#334155",
            width=100,
            command=self.on_close
        )
        self.btn_close.pack(side="right")
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_traceroute(self):
        target = self.entry_target.get().strip()
        if not target:
            messagebox.showwarning("Destino Vacío", "Por favor ingresa una IP o Dominio válido.")
            return
            
        self.target_host = target
        self.is_tracing = True
        self.btn_start.configure(state="disabled", text="⏳ Rastreando...")
        self.entry_target.configure(state="disabled")
        self.lbl_status.configure(text=f"🔄 Rastreando ruta salto por salto hacia {target}...", text_color="#8b5cf6")
        
        for item in self.hops_tree.get_children():
            self.hops_tree.delete(item)
        self.log_box.delete("1.0", "end")
        self.hop_data.clear()
        self.raw_logs.clear()
        
        threading.Thread(target=self._tracert_thread, args=(target,), daemon=True).start()

    def _tracert_thread(self, target):
        import platform
        import re
        import socket
        import subprocess
        
        self.start_time = datetime.now()
        is_win = platform.system().lower() == "windows"
        cmd = ["tracert", "-d", "-h", "20", target] if is_win else ["traceroute", "-n", "-m", "20", target]
        
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="ignore")
            
            for line in iter(proc.stdout.readline, ""):
                if not self.is_tracing:
                    proc.terminate()
                    break
                    
                line_str = line.strip()
                if not line_str:
                    continue
                    
                self.raw_logs.append(line_str)
                self.after(0, lambda l=line_str: self._log_line(l))
                
                match_hop = re.match(r"^(\d+)\s+(.+)$", line_str)
                if match_hop:
                    hop_num = int(match_hop.group(1))
                    rest = match_hop.group(2)
                    
                    ip_match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[a-fA-F0-9\:]+)", rest)
                    ip = ip_match.group(1) if ip_match else "Tiempo de espera agotado"
                    
                    probes = re.findall(r"([<\d]+\s*ms|\*)", rest)
                    p1 = probes[0] if len(probes) > 0 else "—"
                    p2 = probes[1] if len(probes) > 1 else "—"
                    p3 = probes[2] if len(probes) > 2 else "—"
                    
                    hostname = "—"
                    if ip != "Tiempo de espera agotado":
                        try:
                            hostname = socket.gethostbyaddr(ip)[0]
                        except Exception:
                            if ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172."):
                                hostname = "Router Local / LAN"
                            else:
                                hostname = "IP Externa / ISP"
                    
                    if ip == "Tiempo de espera agotado" or (probes and all(p == "*" for p in probes)):
                        status = "🟥 Paquete Perdido (Timeout)"
                    elif "*" in probes:
                        status = "🟨 Pérdida Parcial (*)"
                    else:
                        max_ms = 0
                        for p in probes:
                            m = re.search(r"(\d+)", p)
                            if m and int(m.group(1)) > max_ms:
                                max_ms = int(m.group(1))
                        
                        if max_ms > 120:
                            status = "🟨 Congestionado (>120ms)"
                        else:
                            status = "🟩 Excelente / Fluido"
                            
                    hop_entry = {
                        "hop": hop_num,
                        "ip": ip,
                        "hostname": hostname,
                        "p1": p1,
                        "p2": p2,
                        "p3": p3,
                        "status": status
                    }
                    self.hop_data.append(hop_entry)
                    self.after(0, lambda h=hop_entry: self._add_hop_to_tree(h))

            proc.wait()
        except Exception as e:
            self.after(0, lambda: self._log_line(f"[Error] {e}"))
            
        self.after(0, self._on_trace_complete)

    def _log_line(self, line):
        if self.winfo_exists():
            self.log_box.insert("end", line + "\n")
            self.log_box.see("end")

    def _add_hop_to_tree(self, h):
        if self.winfo_exists():
            self.hops_tree.insert("", "end", values=(
                f"#{h['hop']:02d}",
                h["ip"],
                h["hostname"],
                h["p1"],
                h["p2"],
                h["p3"],
                h["status"]
            ))

    def _on_trace_complete(self):
        if not self.winfo_exists():
            return
        self.is_tracing = False
        self.btn_start.configure(state="normal", text="▶️ Iniciar Rastreo")
        self.entry_target.configure(state="normal")
        self.lbl_status.configure(
            text=f"✅ Rastreo finalizado. Se completaron {len(self.hop_data)} saltos hacia {self.target_host}.",
            text_color="#10b981"
        )

    def export_report(self):
        if not self.hop_data:
            messagebox.showwarning("Sin Datos", "No hay datos de rastreo para exportar.")
            return
            
        now_dt = datetime.now()
        date_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
        elapsed_sec = int((now_dt - self.start_time).total_seconds()) if self.start_time else 0
        mins, secs = divmod(elapsed_sec, 60)
        
        report = f"""================================================================================
            REPORTE DE RASTREO DE RUTA & DIAGNÓSTICO MTR (Traceroute)
          Scan IP - Sistema de Monitoreo, Cobertura & Diagnóstico de Red
                         Propiedad de Ezequiel Díaz
================================================================================

Fecha y Hora de Diagnóstico : {date_str}
Host / Destino Evaluado     : {self.target_host}
Tiempo de Ejecución        : {mins:02d}m {secs:02d}s ({elapsed_sec} segundos)
Total de Saltos Detectados  : {len(self.hop_data)} saltos de red

--- RESUMEN Y MATRIZ DE SALTOS ---
"""
        for h in self.hop_data:
            report += f"Salto #{h['hop']:02d} -> IP: {h['ip']:<16} | Host: {h['hostname']:<25} | Pings: [{h['p1']}, {h['p2']}, {h['p3']}] | Estado: {h['status']}\n"

        report += "\n--- BITÁCORA RAW DE COMANDOS DE RED ---\n"
        for line in self.raw_logs:
            report += line + "\n"

        report += "\n================================================================================\n"
        report += "Fin del Reporte de Traceroute - Scan IP (Propiedad de Ezequiel Díaz)\n"
        
        safe_target = "".join(c for c in self.target_host if c.isalnum() or c in ('.', '_', '-')).strip()
        filename = f"Reporte_Traceroute_{safe_target}_{now_dt.strftime('%Y%m%d_%H%M%S')}.txt"
        save_path = os.path.join(os.path.dirname(__file__), filename)
        
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(report)
            messagebox.showinfo(
                "Reporte Exportado",
                f"El reporte de Traceroute ha sido guardado exitosamente en:\n\n{save_path}"
            )
        except Exception as e:
            messagebox.showerror("Error al Guardar", f"No se pudo guardar el archivo: {e}")

    def on_close(self):
        self.is_tracing = False
        self.destroy()


class NetworkHeartbeatDialog(ctk.CTkToplevel):
    def __init__(self, parent, heartbeat):
        super().__init__(parent)
        self.parent = parent
        self.heartbeat = heartbeat
        
        self.title("🌐 Monitor Heartbeat de Salud de Red & Internet")
        self.geometry("780x640")
        self.resizable(False, False)
        self.grab_set()
        
        self.is_active = True
        self.start_time = datetime.now()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        # 1. Header Frame
        hdr_frame = ctk.CTkFrame(self, corner_radius=12)
        hdr_frame.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="ew")
        hdr_frame.grid_columnconfigure(0, weight=1)
        
        lbl_title = ctk.CTkLabel(
            hdr_frame, 
            text="🌐 Diagnóstico Heartbeat de Conectividad", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        lbl_title.grid(row=0, column=0, padx=15, pady=(10, 2), sticky="w")
        
        meta_str = f"Router Gateway Local: {heartbeat.gateway_ip}   |   Internet WAN: {heartbeat.wan_ip} (Google DNS)"
        lbl_meta = ctk.CTkLabel(
            hdr_frame,
            text=meta_str,
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8"
        )
        lbl_meta.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")
        
        # 2. Stats Cards Grid
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.val_gw = self._build_stat_card(stats_frame, 0, "LATENCIA ROUTER", "-- ms", "#10b981")
        self.val_wan = self._build_stat_card(stats_frame, 1, "LATENCIA INTERNET", "-- ms", "#06b6d4")
        self.val_health = self._build_stat_card(stats_frame, 2, "SALUD DE RED", "100%", "#10b981")
        self.val_loss = self._build_stat_card(stats_frame, 3, "PÉRDIDA PAQUETES", "0%", "#8b5cf6")
        
        # 3. Status Bar Indicator
        self.status_bar = ctk.CTkLabel(
            self,
            text="🟢 Conexión local al Router y salida a Internet 100% estables.",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#10b981"
        )
        self.status_bar.grid(row=2, column=0, padx=20, pady=(5, 5), sticky="w")
        
        # 4. Console Log Box
        log_frame = ctk.CTkFrame(self, corner_radius=12)
        log_frame.grid(row=3, column=0, padx=20, pady=5, sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)
        
        lbl_log_title = ctk.CTkLabel(log_frame, text="📜 Bitácora de Heartbeat en Tiempo Real", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_log_title.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        
        self.log_box = ctk.CTkTextbox(
            log_frame, 
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#090d16",
            text_color="#10b981"
        )
        self.log_box.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="nsew")
        
        # 5. Bottom Buttons Frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, padx=20, pady=(10, 15), sticky="ew")
        
        self.btn_export = ctk.CTkButton(
            btn_frame,
            text="📄 Exportar Bitácora de Salud",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669",
            width=180,
            command=self.export_log
        )
        self.btn_export.pack(side="left")
        
        self.btn_close = ctk.CTkButton(
            btn_frame,
            text="Cerrar",
            fg_color="#475569",
            hover_color="#334155",
            width=100,
            command=self.destroy
        )
        self.btn_close.pack(side="right")
        
        # Load initial history
        self._load_initial_data()
        
        # Register callback for live update
        self.heartbeat.register_callback(self._on_heartbeat_update)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _build_stat_card(self, parent, col, title, initial_val, color):
        card = ctk.CTkFrame(parent, corner_radius=10, border_width=1)
        card.grid(row=0, column=col, padx=3, pady=2, sticky="ew")
        
        lbl_t = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=9, weight="bold"), text_color="#94a3b8")
        lbl_t.pack(anchor="w", padx=8, pady=(8, 2))
        
        lbl_v = ctk.CTkLabel(card, text=initial_val, font=ctk.CTkFont(size=15, weight="bold"), text_color=color)
        lbl_v.pack(anchor="w", padx=8, pady=(0, 8))
        return lbl_v

    def _load_initial_data(self):
        for gw, wan in zip(self.heartbeat.gateway_history[-20:], self.heartbeat.wan_history[-20:]):
            self._append_log_entry(gw, wan)

    def _on_heartbeat_update(self, hb):
        self.after(0, lambda: self._update_ui(hb))

    def _update_ui(self, hb):
        if not self.winfo_exists():
            return
            
        gw_str = f"{hb.gateway_ms} ms" if hb.gateway_online else "OFFLINE 🔴"
        wan_str = f"{hb.wan_ms} ms" if hb.wan_online else "SIN INTERNET 🔴"
        
        self.val_gw.configure(text=gw_str)
        self.val_wan.configure(text=wan_str)
        self.val_health.configure(text=f"{hb.health_score}%")
        
        gw_hist = hb.gateway_history
        if gw_hist:
            lost = sum(1 for h in gw_hist if not h["online"])
            loss_pct = (lost / len(gw_hist)) * 100.0
            self.val_loss.configure(text=f"{loss_pct:.0f}%")
            
        if hb.health_score == 100:
            self.status_bar.configure(text="🟢 Enlace Local y Salida a Internet 100% Funcionales", text_color="#10b981")
            self.val_health.configure(text_color="#10b981")
        elif hb.health_score >= 70:
            self.status_bar.configure(text="🟨 Salida a Internet con Alta Latencia", text_color="#f59e0b")
            self.val_health.configure(text_color="#f59e0b")
        elif hb.health_score >= 40:
            self.status_bar.configure(text="🚨 ALERTA: Conectado a Router Local, pero SIN ACCESO A INTERNET (ISP Caído)", text_color="#ef4444")
            self.val_health.configure(text_color="#ef4444")
        else:
            self.status_bar.configure(text="🚨 ALERTA CRÍTICA: Desconectado de la Red Local (Router Inaccesible)", text_color="#ef4444")
            self.val_health.configure(text_color="#ef4444")
            
        if gw_hist and hb.wan_history:
            self._append_log_entry(gw_hist[-1], hb.wan_history[-1])

    def _append_log_entry(self, gw, wan):
        now_t = gw["time"]
        gw_t = f"{gw['ms']}ms" if gw["online"] else "OFF"
        wan_t = f"{wan['ms']}ms" if wan["online"] else "NO INTERNET"
        
        state_icon = "🟢 Excelente" if (gw["online"] and wan["online"] and wan["ms"] < 150) else ("🟨 Latencia Alta" if wan["online"] else "🔴 Caída")
        line = f"[{now_t}] Router ({self.heartbeat.gateway_ip}): {gw_t:<6} | Internet WAN ({self.heartbeat.wan_ip}): {wan_t:<11} | Estado: {state_icon}\n"
        
        self.log_box.insert("end", line)
        self.log_box.see("end")

    def export_log(self):
        raw_text = self.log_box.get("1.0", "end").strip()
        if not raw_text:
            messagebox.showwarning("Sin Datos", "No hay datos de heartbeat recolectados para exportar.")
            return
            
        now_dt = datetime.now()
        date_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""================================================================================
          REPORTE DE SALUD Y CONECTIVIDAD DE RED EN TIEMPO REAL (Heartbeat)
          IP_Scan_Tools - Sistema de Monitoreo, Cobertura & Diagnóstico de Red
                         Propiedad de Ezequiel Díaz
================================================================================

Fecha y Hora de Exportación : {date_str}
Router Gateway Local        : {self.heartbeat.gateway_ip}
Target Internet WAN         : {self.heartbeat.wan_ip} (Google DNS)
Puntaje Actual de Salud     : {self.heartbeat.health_score}%

--- HISTORIAL DE COMPROBACIÓN DE SALUD ---
{raw_text}

================================================================================
Fin del Reporte de Salud de Red - IP_Scan_Tools (Propiedad de Ezequiel Díaz)
"""
        filename = f"Reporte_Salud_Red_{now_dt.strftime('%Y%m%d_%H%M%S')}.txt"
        save_path = os.path.join(os.path.dirname(__file__), filename)
        
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(report)
            messagebox.showinfo(
                "Reporte Exportado",
                f"El reporte de Salud de Red fue guardado exitosamente en:\n\n{save_path}"
            )
        except Exception as e:
            messagebox.showerror("Error al Exportar", f"No se pudo guardar el reporte: {e}")


class AboutDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("ℹ️ Acerca de IP_Scan_Tools")
        self.geometry("500x420")
        self.resizable(False, False)
        self.grab_set()

        # Container Frame
        card = ctk.CTkFrame(self, corner_radius=16, fg_color="#1e293b", border_width=1, border_color="#334155")
        card.pack(fill="both", expand=True, padx=20, pady=20)

        lbl_logo = ctk.CTkLabel(card, text="📡", font=ctk.CTkFont(size=56))
        lbl_logo.pack(pady=(20, 5))

        lbl_app = ctk.CTkLabel(card, text="IP_Scan_Tools v2.0", font=ctk.CTkFont(size=24, weight="bold"), text_color="#38bdf8")
        lbl_app.pack(pady=2)

        lbl_sub = ctk.CTkLabel(card, text="Suite de Monitoreo de Red, Wi-Fi, Seguridad & Velocidad", font=ctk.CTkFont(size=12), text_color="#94a3b8")
        lbl_sub.pack(pady=(0, 15))

        # Ownership Card
        owner_frame = ctk.CTkFrame(card, corner_radius=10, fg_color="#0f172a", border_width=1, border_color="#1e293b")
        owner_frame.pack(fill="x", padx=25, pady=10)

        lbl_dev_title = ctk.CTkLabel(owner_frame, text="PROPIEDAD Y DESARROLLO", font=ctk.CTkFont(size=10, weight="bold"), text_color="#64748b")
        lbl_dev_title.pack(pady=(8, 2))

        lbl_dev_name = ctk.CTkLabel(owner_frame, text="Ezequiel Díaz", font=ctk.CTkFont(size=18, weight="bold"), text_color="#10b981")
        lbl_dev_name.pack(pady=(0, 2))

        lbl_rights = ctk.CTkLabel(owner_frame, text="Todos los derechos reservados © 2026", font=ctk.CTkFont(size=11), text_color="#94a3b8")
        lbl_rights.pack(pady=(0, 8))

        lbl_desc = ctk.CTkLabel(
            card,
            text="Diseñado para proporcionar monitoreo continuo de red local,\ncobertura Wi-Fi segundo a segundo, diagnóstico de salud,\nevaluación de seguridad y pruebas de velocidad.",
            font=ctk.CTkFont(size=11),
            text_color="#cbd5e1",
            justify="center"
        )
        lbl_desc.pack(pady=10)

        btn_close = ctk.CTkButton(
            card,
            text="Cerrar",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#6366f1",
            hover_color="#4f46e5",
            width=120,
            command=self.destroy
        )
        btn_close.pack(pady=(10, 15))


class SplashScreen(ctk.CTkToplevel):
    """Pantalla de inicio / bienvenida con imagen y barra de progreso al ejecutar la app."""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        
        # Center splash window on screen
        width, height = 680, 420
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = max(0, (screen_width - width) // 2)
        y = max(0, (screen_height - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.configure(fg_color="#0b0f19")
        
        # Main Frame with glowing cyan border
        frame = ctk.CTkFrame(self, corner_radius=16, fg_color="#0b0f19", border_width=2, border_color="#06b6d4")
        frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Load image if splash.jpg exists
        img_path = os.path.join(os.path.dirname(__file__), "splash.jpg")
        if os.path.exists(img_path):
            try:
                pil_img = Image.open(img_path)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(640, 300))
                lbl_img = ctk.CTkLabel(frame, image=ctk_img, text="")
                lbl_img.pack(padx=10, pady=(12, 5))
            except Exception:
                lbl_logo = ctk.CTkLabel(frame, text="📡 IP_Scan_Tools", font=ctk.CTkFont(size=26, weight="bold"), text_color="#06b6d4")
                lbl_logo.pack(pady=(40, 10))
        else:
            lbl_logo = ctk.CTkLabel(frame, text="📡 IP_Scan_Tools", font=ctk.CTkFont(size=26, weight="bold"), text_color="#06b6d4")
            lbl_logo.pack(pady=(40, 10))
            
        # Status text & Progress Bar
        self.lbl_status = ctk.CTkLabel(
            frame, 
            text="⚡ Cargando componentes de red...", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38bdf8"
        )
        self.lbl_status.pack(pady=(5, 2))
        
        self.progress = ctk.CTkProgressBar(frame, width=540, height=10, progress_color="#06b6d4")
        self.progress.pack(pady=(0, 15))
        self.progress.set(0.0)
        
        self.after(200, self._step_1)

    def _step_1(self):
        self.progress.set(0.35)
        self.lbl_status.configure(text="🔍 Inicializando Scapy & Tabla de Enrutamiento...")
        self.after(600, self._step_2)

    def _step_2(self):
        self.progress.set(0.70)
        self.lbl_status.configure(text="🌐 Verificando Gateway Local & Motor de Temas...")
        self.after(700, self._step_3)

    def _step_3(self):
        self.progress.set(1.0)
        self.lbl_status.configure(text="✨ ¡Bienvenido! Propiedad de Ezequiel Díaz", text_color="#10b981")
        self.after(500, self._finish)

    def _finish(self):
        self.destroy()
        if self.parent:
            self.parent.deiconify()


class DnsWhoisDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Herramienta de DNS y WHOIS")
        self.geometry("600x500")
        self.resizable(True, True)
        self.grab_set()

        lbl_title = ctk.CTkLabel(self, text="🌐 Consultas DNS y Registros WHOIS", font=ctk.CTkFont(size=16, weight="bold"))
        lbl_title.pack(padx=20, pady=(20, 10))

        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(padx=20, pady=5, fill="x")
        
        self.domain_entry = ctk.CTkEntry(search_frame, placeholder_text="Ejemplo: google.com", width=350)
        self.domain_entry.pack(side="left", padx=(0, 10))
        
        btn_search = ctk.CTkButton(search_frame, text="Consultar", width=100, command=self.perform_lookup)
        btn_search.pack(side="left")

        self.results_box = ctk.CTkTextbox(self, width=560, height=350)
        self.results_box.pack(padx=20, pady=10, fill="both", expand=True)
        self.results_box.insert("0.0", "Introduce un dominio para ver su resolución DNS e información WHOIS.")
        self.results_box.configure(state="disabled")

        btn_close = ctk.CTkButton(self, text="Cerrar", fg_color="#475569", command=self.destroy)
        btn_close.pack(padx=20, pady=(5, 15))

    def perform_lookup(self):
        domain = self.domain_entry.get().strip()
        if not domain:
            messagebox.showwarning("Advertencia", "Por favor ingresa un dominio.")
            return

        self.results_box.configure(state="normal")
        self.results_box.delete("0.0", "end")
        self.results_box.insert("0.0", f"Realizando consultas para '{domain}'...\nPor favor espera.\n")
        self.results_box.configure(state="disabled")

        threading.Thread(target=self._run_lookup, args=(domain,), daemon=True).start()

    def _run_lookup(self, domain):
        dns_res = get_dns_info(domain)
        whois_res = get_whois_info(domain)
        
        final_text = "=== RESULTADOS DNS ===\n" + dns_res + "\n\n"
        final_text += "=== RESULTADOS WHOIS ===\n" + whois_res
        
        self.after(0, lambda: self._update_results(final_text))

    def _update_results(self, text):
        self.results_box.configure(state="normal")
        self.results_box.delete("0.0", "end")
        self.results_box.insert("0.0", text)
        self.results_box.configure(state="disabled")


if __name__ == "__main__":
    app = ScanIPApp()
    app.mainloop()

