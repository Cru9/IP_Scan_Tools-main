"""
================================================================================
IP_Scan_Tools - Suite de Monitoreo de Red, Wi-Fi, Seguridad & Velocidad
Propiedad y Desarrollo por: Ezequiel Díaz
Todos los derechos reservados © 2026 Ezequiel Díaz
================================================================================
"""

import subprocess
import re


def scan_wifi_networks():
    """
    Executes Windows native netsh command to scan surrounding Wi-Fi Access Points (SSIDs & BSSIDs).
    Returns list of dicts: [{'ssid': '...', 'bssid': '...', 'signal': 85, 'auth': 'WPA2-Personal', 'channel': 6, 'band': '2.4 GHz'}, ...]
    """
    networks = []
    try:
        raw_bytes = subprocess.check_output(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            shell=True,
            stderr=subprocess.DEVNULL
        )
        try:
            output = raw_bytes.decode("oem", errors="replace")
        except Exception:
            output = raw_bytes.decode("utf-8", errors="ignore")

        current_ssid = "Red Oculta"
        current_auth = "Desconocido"
        current_item = None

        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue

            # 1. BSSID check MUST come before SSID check because "BSSID" contains "SSID"
            if ("BSSID" in line or "bssid" in line) and ":" in line:
                if current_item and current_item.get("bssid"):
                    networks.append(current_item)

                parts = line.split(":", 1)
                bssid_val = parts[1].strip().lower() if len(parts) > 1 else ""
                current_item = {
                    "ssid": current_ssid,
                    "bssid": bssid_val,
                    "signal": 0,
                    "auth": current_auth,
                    "channel": 0,
                    "band": "Desconocido"
                }

            # 2. SSID check
            elif ("SSID" in line or "ssid" in line) and ":" in line:
                if current_item and current_item.get("bssid"):
                    networks.append(current_item)
                    current_item = None

                parts = line.split(":", 1)
                val = parts[1].strip()
                current_ssid = val if val else "Red Oculta"

            # 3. Authentication check
            elif ("Autentica" in line or "Authentication" in line) and ":" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    current_auth = parts[1].strip()

            elif current_item:
                # 4. Signal %
                if "%" in line:
                    match = re.search(r"(\d+)\s*%", line)
                    if match and current_item["signal"] == 0:
                        current_item["signal"] = int(match.group(1))

                # 5. Channel
                elif ("Canal" in line or "Channel" in line) and ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        try:
                            ch = int(parts[1].strip())
                            current_item["channel"] = ch
                            if current_item["band"] == "Desconocido":
                                if 1 <= ch <= 14:
                                    current_item["band"] = "2.4 GHz"
                                elif 32 <= ch <= 177:
                                    current_item["band"] = "5 GHz"
                                elif ch >= 180:
                                    current_item["band"] = "6 GHz"
                        except ValueError:
                            pass

                # 6. Band
                elif ("Banda" in line or "Band" in line) and ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        raw_b = parts[1].strip()
                        if "5" in raw_b:
                            current_item["band"] = "5 GHz"
                        elif "6" in raw_b:
                            current_item["band"] = "6 GHz"
                        elif "2" in raw_b:
                            current_item["band"] = "2.4 GHz"
                        else:
                            current_item["band"] = raw_b

        if current_item and current_item.get("bssid"):
            networks.append(current_item)

    except Exception as e:
        print(f"[WiFi Scanner Error] {e}")

    return networks

def get_single_network_signal(target_bssid=None, target_ssid=None):
    """
    Returns current signal info for a target BSSID or SSID, or None if out of range.
    """
    networks = scan_wifi_networks()
    if target_bssid:
        tb = target_bssid.lower().strip()
        for net in networks:
            if net["bssid"].lower() == tb:
                return net
    if target_ssid:
        ts = target_ssid.strip()
        for net in networks:
            if net["ssid"] == ts:
                return net
    return None



