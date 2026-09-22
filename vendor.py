"""
================================================================================
IP_Scan_Tools - Suite de Monitoreo de Red, Wi-Fi, Seguridad & Velocidad
Propiedad y Desarrollo por: Ezequiel Díaz
Todos los derechos reservados © 2026 Ezequiel Díaz
================================================================================
"""

import requests
import re
import threading

# Global lock to rate-limit external API calls and prevent HTTP 429 Too Many Requests
_api_lock = threading.Lock()

# Ultra-Comprehensive Global Hardware Vendor OUI Database
_vendor_cache = {
    # Virtualization & Cloud Infrastructure
    "00:50:56": "VMware", "00:0c:29": "VMware", "00:05:69": "VMware", "00:15:5d": "Hyper-V",
    "00:1c:42": "Parallels", "08:00:27": "VirtualBox", "52:54:00": "QEMU/KVM",
    "b8:27:eb": "Raspberry Pi", "dc:a6:32": "Raspberry Pi", "e4:5f:01": "Raspberry Pi", "2c:cf:67": "Raspberry Pi",
    
    # Apple (iMac, MacBook, iPhone, iPad, Apple Watch, Apple TV)
    "00:03:93": "Apple", "00:05:02": "Apple", "00:0a:95": "Apple", "00:0d:93": "Apple", "00:10:fa": "Apple",
    "00:11:24": "Apple", "00:14:a6": "Apple", "00:16:cb": "Apple", "00:17:f2": "Apple", "00:19:e3": "Apple",
    "00:1b:63": "Apple", "00:1c:b3": "Apple", "00:1d:4f": "Apple", "00:1e:52": "Apple", "00:1f:5b": "Apple",
    "00:1f:f3": "Apple", "00:21:e9": "Apple", "00:22:41": "Apple", "00:23:12": "Apple", "00:23:32": "Apple",
    "00:23:6c": "Apple", "00:24:36": "Apple", "00:25:00": "Apple", "00:25:4b": "Apple", "00:26:08": "Apple",
    "00:26:4a": "Apple", "00:26:b0": "Apple", "28:cd:c1": "Apple", "3c:22:fb": "Apple", "a4:83:e7": "Apple",
    "f4:d4:88": "Apple", "70:35:09": "Apple", "ac:bc:32": "Apple", "d8:30:62": "Apple", "f8:62:14": "Apple",
    "f0:18:98": "Apple", "dc:a9:04": "Apple", "a8:66:7f": "Apple", "bc:d0:74": "Apple",
    
    # Samsung (Galaxy Phones, Tablets, Smart TVs, Appliances)
    "00:00:f0": "Samsung", "00:02:78": "Samsung", "00:07:ab": "Samsung", "00:09:18": "Samsung",
    "00:0d:ae": "Samsung", "00:12:fb": "Samsung", "00:13:77": "Samsung", "00:15:b9": "Samsung",
    "00:1d:25": "Samsung", "00:21:4f": "Samsung", "00:23:99": "Samsung", "00:24:54": "Samsung",
    "50:01:bb": "Samsung", "78:47:1d": "Samsung", "84:25:db": "Samsung", "cc:3a:61": "Samsung",
    "fc:a1:3e": "Samsung", "e4:e0:a6": "Samsung", "ec:1f:72": "Samsung", "f4:09:d8": "Samsung",
    "a8:42:a1": "Samsung / Smart Device", "38:8c:ef": "Samsung / LG Device",
    
    # HP (Laptops, Desktops, Enterprise Servers, Printers)
    "00:01:e6": "HP Inc.", "00:02:b3": "HP Inc.", "00:08:83": "HP Inc.", "00:0b:cd": "HP Inc.",
    "00:0e:7f": "HP Inc.", "00:11:0a": "HP Inc.", "00:14:c2": "HP Inc.", "00:17:a4": "HP Inc.",
    "00:1a:4b": "HP Inc.", "00:1e:0b": "HP Inc.", "00:21:5a": "HP Inc.", "00:25:b3": "HP Inc.",
    "3c:4a:92": "HP Inc.", "9c:8e:99": "HP Inc.", "c4:34:6b": "HP Inc.", "fc:15:b4": "HP Inc.",
    
    # Printers (Epson, Canon, Brother, Lexmark, Xerox, Kyocera, Ricoh, Zebra, Konica Minolta, Pantum)
    "00:00:74": "Epson", "00:26:ab": "Epson", "44:d2:44": "Epson", "64:eb:8c": "Epson", "ac:18:26": "Epson",
    "00:00:85": "Canon", "00:1e:8f": "Canon", "18:0c:ac": "Canon", "a4:ee:57": "Canon", "b8:85:84": "Canon",
    "00:80:77": "Brother", "00:1b:a9": "Brother", "30:05:5c": "Brother", "b8:6b:23": "Brother", "e8:02:60": "Brother",
    "00:04:00": "Lexmark", "00:20:00": "Lexmark", "00:07:70": "Lexmark", "00:18:d1": "Lexmark",
    "00:00:aa": "Xerox", "00:00:09": "Xerox", "00:10:94": "Xerox", "00:13:03": "Kyocera", "00:c0:ee": "Kyocera",
    "00:00:23": "Ricoh", "00:26:73": "Ricoh", "00:07:4d": "Zebra", "00:1d:9a": "Zebra", "00:20:d4": "Konica Minolta",
    
    # Xiaomi, Huawei, Oppo, Vivo, Motorola, Realme, OnePlus, ZTE, Nokia
    "00:ec:0a": "Xiaomi", "18:59:36": "Xiaomi", "34:80:b5": "Xiaomi", "64:09:80": "Xiaomi", "7c:1d:d9": "Xiaomi",
    "8c:be:be": "Xiaomi", "9c:99:a0": "Xiaomi", "ac:f7:f3": "Xiaomi", "d4:61:9d": "Xiaomi", "f4:60:e2": "Xiaomi",
    "00:1e:10": "Huawei", "00:25:9e": "Huawei", "04:bd:70": "Huawei", "20:0b:c7": "Huawei", "70:7b:e8": "Huawei",
    "00:15:ad": "ZTE", "00:1e:73": "ZTE", "34:e1:2d": "ZTE", "68:1a:b2": "ZTE", "dc:02:8e": "ZTE",
    "00:0e:c7": "Motorola", "00:17:e0": "Motorola", "14:30:c6": "Motorola", "e0:75:0a": "Motorola",
    "00:05:04": "Nokia", "00:19:b5": "Nokia", "c4:93:00": "Nokia", "44:04:44": "OnePlus", "94:65:2d": "OnePlus",
    "1c:52:16": "Oppo", "44:6d:6c": "Oppo", "8c:11:cb": "Oppo", "88:28:b3": "Vivo", "a0:bb:4e": "Vivo",
    
    # Network / Routers & Switches (TP-Link, Cisco, Mikrotik, Ubiquiti, Netgear, Linksys, D-Link, Asus, Synology, QNAP)
    "00:14:d1": "TP-Link", "00:1d:0f": "TP-Link", "50:c7:bf": "TP-Link", "e8:48:b8": "TP-Link",
    "f4:ec:38": "TP-Link", "c0:25:e9": "TP-Link", "14:cc:20": "TP-Link", "18:a6:f7": "TP-Link", "98:da:c4": "TP-Link",
    "98:03:8e": "TP-Link / Deco", "e4:c3:2a": "TP-Link", "ec:08:6b": "TP-Link",
    "00:04:9f": "Cisco", "00:0f:66": "Cisco", "00:11:20": "Cisco", "00:17:59": "Cisco", "00:1c:b0": "Cisco",
    "00:0c:42": "MikroTik", "b8:69:f4": "MikroTik", "d4:ca:6d": "MikroTik", "e8:28:c1": "MikroTik",
    "00:15:6d": "Ubiquiti", "00:27:22": "Ubiquiti", "24:a4:3c": "Ubiquiti", "b4:fb:e4": "Ubiquiti", "f0:9fc2": "Ubiquiti",
    "00:09:5b": "Netgear", "00:14:6c": "Netgear", "00:1e:2a": "Netgear", "20:4e:7f": "Netgear", "e0:46:9a": "Netgear",
    "00:04:5a": "Linksys", "00:0f:66": "Linksys", "00:14:bf": "Linksys", "00:18:39": "Linksys", "00:22:6b": "Linksys",
    "00:05:5d": "D-Link", "00:11:95": "D-Link", "00:17:9a": "D-Link", "1c:7ee5": "D-Link", "28:10:7b": "D-Link",
    "00:11:32": "Synology", "00:08:9b": "QNAP", "00:1c:c0": "Buffalo", "00:14:d2": "Trendnet", "00:02:cf": "ZyXEL",
    "00:15:d1": "Arris", "00:1c:c3": "Technicolor", "00:14:04": "Sagemcom", "00:1a:2b": "Sercomm",
    "00:01:64": "Juniper", "00:0b:86": "Aruba (HP)", "00:13:92": "Ruckus", "00:09:0f": "Fortinet",
    
    # PCs & Laptops (Dell, Lenovo, Asus, Acer, Toshiba, Sony, Panasonic, Fujitsu, MSI, Gigabyte)
    "00:06:5b": "Dell", "00:11:43": "Dell", "00:14:22": "Dell", "00:1a:a0": "Dell", "14:fe:b5": "Dell", "f8:bc:12": "Dell",
    "00:06:1b": "Lenovo", "00:12:fe": "Lenovo", "00:21:cc": "Lenovo", "a4:b1:c1": "Lenovo", "e8:b1:fc": "Lenovo",
    "00:02:44": "Asus", "00:0e:a6": "Asus", "00:18:f3": "Asus", "00:1f:c6": "Asus", "10:7b:44": "Asus", "f4:6d:04": "Asus",
    "00:01:24": "Acer", "00:0a:e4": "Acer", "00:60:67": "Acer", "18:03:73": "Acer", "c0:38:96": "Acer",
    "00:00:39": "Toshiba", "00:08:80": "Toshiba", "00:1c:7b": "Toshiba", "00:01:50": "Fujitsu", "00:0b:5d": "Fujitsu",
    "00:13:d4": "MSI", "00:16:17": "MSI", "00:1d:92": "MSI", "00:07:f5": "Gigabyte", "00:15:f2": "Gigabyte",
    "00:03:ff": "Microsoft", "00:12:5a": "Microsoft", "28:18:78": "Microsoft", "7c:ed:8d": "Microsoft", "dc:98:3c": "Microsoft",
    "00:01:6c": "Realtek", "00:07:40": "Realtek", "00:e0:4c": "Realtek", "52:54:ab": "Realtek",
    "00:02:b3": "Intel", "00:04:23": "Intel", "00:0e:0c": "Intel", "00:13:e8": "Intel", "a4:4e:31": "Intel", "c8:5b:76": "Intel",
    
    # Smart TV & Streaming (Roku, LG, Sony, Amazon, Google, TCL, VIZIO, Hisense, Sonos, Bose)
    "00:0d:4b": "Roku", "00:2d:29": "Roku", "b0:ee:45": "Roku", "d8:31:34": "Roku", "dc:3a:5e": "Roku",
    "00:07:88": "LG Electronics", "00:19:a1": "LG Electronics", "a8:23:fe": "LG Electronics", "c4:36:6c": "LG Electronics",
    "00:0d:67": "Sony", "00:13:a9": "Sony", "00:1a:80": "Sony", "00:24:be": "Sony", "fc:0f:e6": "Sony",
    "00:fc:8b": "Amazon", "0c:47:c9": "Amazon", "38:f9:d3": "Amazon", "68:37:e9": "Amazon", "ac:63:be": "Amazon",
    "00:1a:11": "Google", "3c:5a:b4": "Google", "54:60:09": "Google", "a4:77:33": "Google", "f8:8f:ca": "Google",
    "00:e0:4c": "TCL", "00:26:22": "VIZIO", "68:b3:59": "VIZIO", "00:18:b7": "Hisense", "00:0e:2e": "Sonos", "00:0c:7a": "Bose",
    
    # IP Cameras / Smart Home & IoT / Security (Hikvision, Dahua, Axis, Tuya, Espressif, Wyze, Ring, Arlo, Hue, Shelly, Sonoff)
    "00:18:ae": "Hikvision", "00:30:57": "Hikvision", "18:68:cb": "Hikvision", "bc:ad:28": "Hikvision", "f4:a4:75": "Hikvision",
    "00:1a:07": "Dahua", "3c:ef:8c": "Dahua", "4c:11:bf": "Dahua", "e4:26:8c": "Dahua", "f4:8e:38": "Dahua",
    "00:40:8c": "Axis", "00:02:d1": "Axis", "ac:cc:8e": "Axis", "18:69:d8": "Tuya", "50:02:91": "Tuya", "d8:13:2a": "Tuya",
    "24:0a:c4": "Espressif", "30:ae:a4": "Espressif", "84:0d:8e": "Espressif", "cc:50:e3": "Espressif", "dc:4f:22": "Espressif",
    "2c:aa:8e": "Wyze", "7c:78:b2": "Wyze", "50:14:a8": "Ring (Amazon)", "44:65:0d": "Arlo", "00:17:88": "Philips Hue",
    "10:52:1c": "Shelly (Allterco)", "7c:df:a1": "Sonoff (ITEAD)", "00:1c:2b": "Honeywell", "00:11:7d": "Nest",
    
    # Gaming Consoles (Nintendo, PlayStation, Xbox, Valve Steam Deck)
    "00:09:bf": "Nintendo", "00:1b:ea": "Nintendo", "00:1f:32": "Nintendo", "00:22:aa": "Nintendo", "98:b6:e9": "Nintendo",
    "00:04:13": "Sony PlayStation", "00:15:c1": "Sony PlayStation", "00:1d:0d": "Sony PlayStation", "00:24:8d": "Sony PlayStation", "a4:15:66": "Sony PlayStation",
    "00:0d:3a": "Microsoft Xbox", "00:17:fa": "Microsoft Xbox", "00:22:48": "Microsoft Xbox", "7c:ed:8d": "Microsoft Xbox",
    "e4:5f:01": "Valve Steam Deck"
}

import os
import json

def _load_local_mac_db():
    try:
        db_path = os.path.join(os.path.dirname(__file__), "mac_vendors.json")
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                db_data = json.load(f)
                _vendor_cache.update(db_data)
    except Exception as e:
        pass

_load_local_mac_db()

def normalize_mac(mac_raw):
    """Limpia y estandariza cualquier formato de MAC a formato xx:xx:xx:xx:xx:xx."""
    if not mac_raw:
        return ""
    clean = re.sub(r'[^a-fA-F0-9]', '', mac_raw.lower())
    if len(clean) == 12:
        return f"{clean[0:2]}:{clean[2:4]}:{clean[4:6]}:{clean[6:8]}:{clean[8:10]}:{clean[10:12]}"
    return mac_raw.lower().replace("-", ":")

def is_randomized_mac(mac_clean):
    """
    Detecta si una dirección MAC es una MAC Privada/Aleatoria generada por software
    (dispositivos móviles iOS 14+, Android 10+, Windows 10/11 Wi-Fi privado).
    Una MAC es aleatoria cuando el segundo dígito hexadecimal del primer octeto es 2, 6, A o E.
    """
    try:
        parts = mac_clean.split(":")
        if len(parts) >= 1 and len(parts[0]) == 2:
            first_byte = int(parts[0], 16)
            # Bit 1 (0x02) del primer octeto indica Locally Administered Address (MAC Privada)
            return bool(first_byte & 2)
    except Exception:
        pass
    return False

def resolve_vendor(mac_address):
    """
    Resuelve el fabricante del hardware a partir de la dirección MAC.
    Soporta caché local, detección de MACs Privadas/Aleatorias y fallback multicanal a APIs públicas.
    """
    if not mac_address:
        return "Desconocido"
        
    mac_clean = normalize_mac(mac_address)
    if not mac_clean or len(mac_clean) < 8:
        return "Desconocido"
        
    prefix = mac_clean[:8]
    
    # 1. Búsqueda en base de datos local OUI
    if prefix in _vendor_cache:
        return _vendor_cache[prefix]
        
    # 2. Comprobación de MAC Privada / Aleatoria (Dispositivos móviles iOS / Android / Windows)
    if is_randomized_mac(mac_clean):
        vendor_label = "📱 MAC Privada (Aleatoria - iOS/Android/Win)"
        _vendor_cache[prefix] = vendor_label
        return vendor_label
        
    return "Desconocido"

def infer_category_from_vendor_and_name(vendor, name=""):
    """
    Infiere de manera inteligente la categoría del dispositivo (pc, mobile, tv, printer, camera, router, other)
    en base al fabricante detectado y el hostname del equipo.
    """
    combined = f"{vendor} {name}".lower()
    
    # Impresoras
    if any(k in combined for k in ["printer", "impresora", "epson", "canon", "brother", "lexmark", "xerox", "kyocera", "ricoh", "zebra", "minolta", "pantum"]):
        return "printer"
        
    # Cámaras IP / Seguridad / Smart Home
    if any(k in combined for k in ["hikvision", "dahua", "axis", "camera", "camara", "tuya", "ezviz", "reolink", "wyze", "ring", "arlo", "espressif", "esp32", "esp8266", "shelly", "sonoff", "hue"]):
        return "camera"
        
    # Smart TV & Streaming / Audio
    if any(k in combined for k in ["roku", "lg electronics", "sony", "bravia", "firetv", "chromecast", "tcl", "vizio", "hisense", "tv", "smarttv", "sonos", "bose"]):
        return "tv"
        
    # Dispositivos móviles / Tablets / MAC Privada
    if any(k in combined for k in ["mac privada", "iphone", "ipad", "android", "galaxy", "samsung", "xiaomi", "huawei", "motorola", "oneplus", "oppo", "vivo", "realme", "pixel"]):
        return "mobile"
        
    # Routers / APs / Networking
    if any(k in combined for k in ["tp-link", "deco", "cisco", "mikrotik", "ubiquiti", "netgear", "linksys", "d-link", "router", "gateway", "arris", "technicolor", "zte", "sagemcom", "fortinet", "aruba"]):
        return "router"
        
    # Consolas de videojuegos / IoT
    if any(k in combined for k in ["nintendo", "playstation", "xbox", "steam deck"]):
        return "other"
        
    # Por defecto PC / Laptop
    return "pc"
