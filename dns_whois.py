"""
================================================================================
IP_Scan_Tools - Herramienta de DNS y WHOIS
Propiedad y Desarrollo por: Ezequiel Díaz
Todos los derechos reservados © 2026 Ezequiel Díaz
================================================================================
"""

import socket
try:
    import whois
except ImportError:
    whois = None

def get_dns_info(domain):
    """
    Realiza una consulta DNS para obtener las direcciones IP de un dominio.
    """
    domain = domain.replace("http://", "").replace("https://", "").split("/")[0]
    try:
        hostname, aliaslist, ipaddrlist = socket.gethostbyname_ex(domain)
        
        result = f"Hostname: {hostname}\n"
        if aliaslist:
            result += f"Aliases: {', '.join(aliaslist)}\n"
        if ipaddrlist:
            result += f"Direcciones IP:\n"
            for ip in ipaddrlist:
                result += f"  - {ip}\n"
        return result
    except Exception as e:
        return f"Error en resolución DNS: {str(e)}"

def get_whois_info(domain):
    """
    Realiza una consulta WHOIS para el dominio especificado.
    """
    if whois is None:
        return "Error: el módulo 'python-whois' no está instalado."
        
    domain = domain.replace("http://", "").replace("https://", "").split("/")[0]
    try:
        w = whois.whois(domain)
        # Formatear la salida de manera legible
        result = ""
        for key, value in w.items():
            if value:
                # Si el valor es una lista, unirla
                if isinstance(value, list):
                    value = ", ".join([str(v) for v in value])
                result += f"{key.capitalize()}: {value}\n"
        return result if result else "No se encontró información WHOIS."
    except Exception as e:
        return f"Error en consulta WHOIS: {str(e)}"
