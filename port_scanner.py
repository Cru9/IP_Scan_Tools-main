"""
================================================================================
IP_Scan_Tools - Suite de Monitoreo de Red, Wi-Fi, Seguridad & Velocidad
Propiedad y Desarrollo por: Ezequiel Díaz
Todos los derechos reservados © 2026 Ezequiel Díaz
================================================================================
"""

import socket
from concurrent.futures import ThreadPoolExecutor


COMMON_PORTS = {
    21: "FTP (Transferencia de Archivos)",
    22: "SSH (Administración Remota)",
    23: "Telnet (Consola No Segura)",
    53: "DNS (Servidor de Nombres)",
    80: "HTTP (Servidor Web)",
    443: "HTTPS (Servidor Web Seguro)",
    445: "SMB (Archivos Compartidos Windows)",
    3389: "RDP (Escritorio Remoto Windows)",
    5900: "VNC (Control Remoto Gráfico)",
    8080: "HTTP Alt (Panel/Proxy Web)",
    8443: "HTTPS Alt (Panel Seguro)",
    9100: "Impresora (RAW Port)"
}

def check_port(ip, port, timeout=1.0):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((ip, port))
        
        if result == 0:
            banner = ""
            try:
                # Intentar banner grabbing dependiendo del puerto
                if port in [80, 443, 8080, 8443]:
                    s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
                    banner_data = s.recv(1024).decode('utf-8', errors='ignore')
                    for line in banner_data.split('\n'):
                        if line.lower().startswith('server:'):
                            banner = line.strip()
                            break
                    if not banner:
                        banner = "Servicio HTTP (No Banner)"
                else:
                    banner_data = s.recv(1024).decode('utf-8', errors='ignore')
                    banner = banner_data.strip()
            except Exception:
                banner = "Sin Banner"
                
            s.close()
            
            # Limpiar banner
            if len(banner) > 50:
                banner = banner[:47] + "..."
            elif not banner:
                banner = "Sin Banner"
                
            # Limpiar saltos de linea
            banner = banner.replace('\r', '').replace('\n', ' ')
            
            return (port, COMMON_PORTS.get(port, "Servicio Desconocido"), banner)
            
        s.close()
    except Exception:
        pass
    return None

def scan_target_ports(ip, ports=None, max_threads=50):
    if ports is None:
        ports = list(COMMON_PORTS.keys())
        
    open_ports = []
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(check_port, ip, port) for port in ports]
        for future in futures:
            res = future.result()
            if res:
                open_ports.append(res)
                
    return sorted(open_ports, key=lambda x: x[0])
