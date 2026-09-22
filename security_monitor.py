"""
================================================================================
IP_Scan_Tools - Suite de Monitoreo de Red, Wi-Fi, Seguridad & Velocidad
Propiedad y Desarrollo por: Ezequiel Díaz
Todos los derechos reservados © 2026 Ezequiel Díaz
================================================================================
"""

from notifications import notify


class SecurityMonitor:
    def __init__(self):
        self.gateway_mac = None
        self.gateway_ip = None
        self.security_threats = []

    def inspect_network(self, active_devices):
        """
        active_devices is a list of dicts: [{'ip': '...', 'mac': '...'}, ...]
        """
        threats = []
        ip_map = {}
        
        for dev in active_devices:
            ip = dev["ip"]
            mac = dev["mac"]
            
            # 1. IP Conflict Check
            if ip in ip_map and ip_map[ip] != mac:
                msg = f"⚠️ Conflicto de IP detectado: La IP {ip} es usada por 2 MACs distintas ({mac} y {ip_map[ip]})"
                threats.append({
                    "type": "ip_conflict",
                    "ip": ip,
                    "mac": mac,
                    "message": msg
                })
                notify("🚨 ALERTA DE SEGURIDAD: Conflicto de IP", msg)
            else:
                ip_map[ip] = mac
                
            # 2. ARP Spoofing Check (Gateway Impersonation)
            if self.gateway_ip and ip == self.gateway_ip:
                if self.gateway_mac is None:
                    self.gateway_mac = mac
                elif self.gateway_mac != mac:
                    msg = f"🚨 ALERTA CRÍTICA: Posible ataque ARP Spoofing. La MAC {mac} intenta suplantar al Router ({ip})"
                    threats.append({
                        "type": "arp_spoofing",
                        "ip": ip,
                        "mac": mac,
                        "message": msg
                    })
                    notify("🚨 ALERTA CRÍTICA: ARP Spoofing Detectado", msg)

        self.security_threats = threats
        return len(threats) == 0, threats
