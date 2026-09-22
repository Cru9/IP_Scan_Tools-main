"""
================================================================================
IP_Scan_Tools - Suite de Monitoreo de Red, Wi-Fi, Seguridad & Velocidad
Propiedad y Desarrollo por: Ezequiel Díaz
Todos los derechos reservados © 2026 Ezequiel Díaz
================================================================================
"""

import socket

_hostname_cache = {}

def resolve_netbios_name(ip, timeout=0.25):
    """
    Queries target IP via NetBIOS Name Service (UDP port 137) to get the real Windows/Samba computer name.
    """
    try:
        # NetBIOS Node Status Request packet
        pkt = (
            b"\x80\x94\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00"
            b"\x20\x43\x4b\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41"
            b"\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x00\x00\x21\x00\x01"
        )
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.settimeout(timeout)
            sock.sendto(pkt, (ip, 137))
            data, _ = sock.recvfrom(1024)
            
            if len(data) > 57:
                num_names = data[56]
                offset = 57
                for _ in range(num_names):
                    if offset + 18 <= len(data):
                        name_bytes = data[offset:offset + 15]
                        name_type = data[offset + 15]
                        offset += 18
                        if name_type in (0x00, 0x20):
                            name = name_bytes.decode("ascii", errors="ignore").strip()
                            if name and not name.startswith("IS~") and not name.startswith("__MSBROWSE__"):
                                return name
        finally:
            try:
                sock.close()
            except Exception:
                pass
    except Exception:
        pass
    return ""


def resolve_hostname(ip, timeout=0.4):
    """
    Resolves hostname using NetBIOS first, then DNS PTR lookup.
    """
    if ip in _hostname_cache and _hostname_cache[ip]:
        return _hostname_cache[ip]
        
    # 1. Try NetBIOS (UDP 137) - Ultra-fast for Windows PCs & LAN devices
    nb_name = resolve_netbios_name(ip, timeout=0.25)
    if nb_name:
        _hostname_cache[ip] = nb_name
        return nb_name

    # 2. Try DNS Reverse Lookup (PTR)
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        if hostname:
            clean_name = hostname.split('.')[0].strip()
            _hostname_cache[ip] = clean_name
            return clean_name
    except Exception:
        pass
        
    _hostname_cache[ip] = ""
    return ""

