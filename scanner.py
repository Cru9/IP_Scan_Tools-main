"""
================================================================================
IP_Scan_Tools - Suite de Monitoreo de Red, Wi-Fi, Seguridad & Velocidad
Propiedad y Desarrollo por: Ezequiel Díaz
Todos los derechos reservados © 2026 Ezequiel Díaz
================================================================================
"""

import socket
import threading
import time
import ipaddress
from concurrent.futures import ThreadPoolExecutor
import subprocess
import re
from vendor import resolve_vendor, infer_category_from_vendor_and_name
from hostname_resolver import resolve_hostname
from notifications import notify
from security_monitor import SecurityMonitor

class NetworkScanner:
    def __init__(self, interval=15):
        self.interval = interval
        self.running = False
        self.thread = None
        self.last_scan_time = None
        self.is_scanning = False
        self.custom_subnet = None
        self.security_monitor = SecurityMonitor()
        self.hosts = []
        self.seen_macs = set()

    def get_local_subnet_and_gateway(self):
        gateway_ip = None
        
        # 1. Scapy OS routing table lookup
        try:
            from scapy.all import conf
            gw = conf.route.route("8.8.8.8")[2]
            if gw and gw != "0.0.0.0":
                gateway_ip = gw
        except Exception:
            pass

        # 2. Command line fallback (route print 0.0.0.0 / netsh)
        if not gateway_ip:
            try:
                import subprocess, re
                out = subprocess.check_output(["route", "print", "0.0.0.0"], text=True, errors="ignore")
                match = re.search(r"0\.0\.0\.0\s+0\.0\.0\.0\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", out)
                if match:
                    gateway_ip = match.group(1)
            except Exception:
                pass

        # 3. Local IP fallback
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            ip_parts = local_ip.split('.')
            if not gateway_ip:
                gateway_ip = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.1"
            subnet = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
            return subnet, gateway_ip
        except Exception:
            return "192.168.1.0/24", gateway_ip or "192.168.1.1"

    def set_custom_subnet(self, subnet_str):
        if not subnet_str or subnet_str.strip() in ["", "Auto (Local)", "Auto"]:
            self.custom_subnet = None
            return True, "Modo de detección automática activado."
            
        subnet_clean = subnet_str.strip()
        try:
            net = ipaddress.ip_network(subnet_clean, strict=False)
            if net.num_addresses > 1024:
                return False, f"La subred '{subnet_str}' contiene {net.num_addresses} direcciones. Por seguridad y rendimiento, use un prefijo /22 o menor (máximo 1024 hosts)."
            self.custom_subnet = str(net)
            return True, f"Subred personalizada configurada: {net}"
        except ValueError:
            return False, f"La subred '{subnet_str}' no es una notación CIDR válida (ejemplo: 192.168.1.0/24)."

    def measure_ping(self, ip):
        # Chequeo rápido en puertos comunes con timeout reducido
        for port in (80, 445, 139, 443):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                start = time.time()
                s.settimeout(0.08)
                res = s.connect_ex((ip, port))
                if res == 0:
                    return max(1, int((time.time() - start) * 1000))
            except Exception:
                pass
            finally:
                try:
                    s.close()
                except Exception:
                    pass
        return 3

    def _process_single_host(self, ip, mac, now_str, latency=None):
        vendor = resolve_vendor(mac)
        hostname = resolve_hostname(ip)
        if latency is None or latency <= 0:
            latency = self.measure_ping(ip)
        category = infer_category_from_vendor_and_name(vendor, hostname)
        
        self.seen_macs.add(mac)

        return {
            "ip": ip,
            "mac": mac,
            "name": hostname,
            "vendor": vendor,
            "category": category,
            "latency": latency,
            "last_seen": now_str,
            "status": "online"
        }

    def perform_scan(self, target_subnet=None):
        if self.is_scanning:
            return
            
        self.is_scanning = True
        auto_subnet, gateway_ip = self.get_local_subnet_and_gateway()
        self.security_monitor.gateway_ip = gateway_ip
        
        active_target = target_subnet or self.custom_subnet or auto_subnet
            
        try:
            # Generar todas las IPs de la subred
            network = ipaddress.ip_network(active_target, strict=False)
            all_ips = [str(ip) for ip in network.hosts()]
            
            # Función auxiliar para comprobar IP y capturar latencia real
            def ping_host(ip_str):
                latency = 0
                is_alive = False
                try:
                    res = subprocess.run(
                        ['ping', '-n', '1', '-w', '250', ip_str],
                        capture_output=True,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                    )
                    if res.returncode == 0:
                        is_alive = True
                        match = re.search(r'(?:tiempo|time)[=<](\d+)ms', res.stdout, re.IGNORECASE)
                        if match:
                            latency = int(match.group(1))
                        elif '<1ms' in res.stdout or '<1' in res.stdout:
                            latency = 1
                        else:
                            latency = 2
                except Exception:
                    pass
                
                # Ping UDP al puerto NetBIOS (137) para forzar actualización de tabla ARP
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.sendto(b'', (ip_str, 137))
                    s.close()
                except Exception:
                    pass
                    
                return (ip_str, latency) if is_alive else None
            
            # 1. Barrido ping concurrente
            workers = min(256, max(32, len(all_ips)))
            with ThreadPoolExecutor(max_workers=workers) as executor:
                ping_results = list(executor.map(ping_host, all_ips))
            
            alive_map = {res[0]: res[1] for res in ping_results if res}
            alive_ips = set(alive_map.keys())
                
            # 2. Lectura de la caché ARP nativa del sistema
            arp_out = subprocess.check_output(
                ["arp", "-a"],
                text=True,
                errors="ignore",
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            now_str = time.strftime("%Y-%m-%d %H:%M:%S")
            active_devices = []
            discovered_pairs = []
            
            # Detectar IP y MAC de la máquina local
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                if ipaddress.ip_address(local_ip) in network:
                    local_mac = "00:00:00:00:00:00"
                    import uuid
                    mac_num = hex(uuid.getnode()).replace('0x', '').upper()
                    if len(mac_num) == 12:
                        local_mac = ':'.join(mac_num[i:i+2] for i in range(0, 12, 2)).lower()
                    active_devices.append({'ip': local_ip, 'mac': local_mac})
                    discovered_pairs.append((local_ip, local_mac))
                    if local_ip in alive_ips:
                        alive_ips.remove(local_ip)
            except Exception:
                pass
            
            # Parsear salida de la tabla ARP
            for line in arp_out.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    ip = parts[0]
                    mac = parts[1].replace('-', ':').lower()
                    
                    try:
                        ip_obj = ipaddress.ip_address(ip)
                        if ip_obj in network and mac not in ("ff:ff:ff:ff:ff:ff", "00:00:00:00:00:00"):
                            if not any(d['ip'] == ip for d in active_devices):
                                active_devices.append({'ip': ip, 'mac': mac})
                                discovered_pairs.append((ip, mac))
                                if ip in alive_ips:
                                    alive_ips.remove(ip)
                    except ValueError:
                        continue
                        
            # Dispositivos que respondieron a ping pero no tienen entrada ARP (subredes remotas/enrutadas)
            for ip in alive_ips:
                if not any(d['ip'] == ip for d in active_devices):
                    mac = "00:00:00:00:00:00"
                    active_devices.append({'ip': ip, 'mac': mac})
                    discovered_pairs.append((ip, mac))
                
            # 3. Procesamiento en paralelo de los hosts descubiertos
            scanned_hosts = []
            if discovered_pairs:
                with ThreadPoolExecutor(max_workers=50) as executor:
                    futures = [
                        executor.submit(self._process_single_host, ip, mac, now_str, alive_map.get(ip))
                        for ip, mac in discovered_pairs
                    ]
                    for f in futures:
                        try:
                            scanned_hosts.append(f.result())
                        except Exception:
                            pass

            # 4. Agregar IPs no ocupadas dentro del rango
            found_ips = {d['ip'] for d in active_devices}
            for ip in all_ips:
                if ip not in found_ips:
                    scanned_hosts.append({
                        "ip": ip,
                        "mac": "—",
                        "name": "Libre / Sin Uso",
                        "vendor": "—",
                        "os": "—",
                        "category": "other",
                        "latency": 0,
                        "last_seen": "—",
                        "status": "offline"
                    })

            # Ordenar numéricamente por dirección IP
            scanned_hosts.sort(key=lambda x: [int(part) for part in x["ip"].split(".") if part.isdigit()])

            # Security inspection
            self.security_monitor.inspect_network(active_devices)
            
            self.hosts = scanned_hosts
            self.last_scan_time = now_str
        except Exception as e:
            print(f"[Scanner Error] {e}")
        finally:
            self.is_scanning = False

    def _loop(self):
        while self.running:
            self.perform_scan()
            time.sleep(self.interval)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
