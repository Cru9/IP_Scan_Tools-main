"""
================================================================================
IP_Scan_Tools - Suite de Monitoreo de Red, Wi-Fi, Seguridad & Velocidad
Propiedad y Desarrollo por: Ezequiel Díaz
Todos los derechos reservados © 2026 Ezequiel Díaz
================================================================================
"""

import subprocess
import threading
import time
import platform
import re
from datetime import datetime


class NetworkHeartbeat:
    def __init__(self, check_interval=3):
        self.check_interval = check_interval
        self.gateway_ip = self._detect_gateway_ip()
        self.wan_ip = "8.8.8.8"
        self.is_running = False
        
        # State metrics
        self.gateway_online = False
        self.gateway_ms = 0
        self.wan_online = False
        self.wan_ms = 0
        self.health_score = 100  # 0 to 100%
        
        self.gateway_history = []
        self.wan_history = []
        self.callbacks = []
        
    def _detect_gateway_ip(self):
        try:
            cmd = ["netsh", "interface", "ip", "show", "config"]
            out = subprocess.check_output(cmd, text=True, errors="ignore")
            match = re.search(r"Gateway[^\:]*\:\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", out, re.IGNORECASE)
            if match:
                return match.group(1)
            # Fallback IP route check
            out_route = subprocess.check_output(["route", "print", "0.0.0.0"], text=True, errors="ignore")
            match_r = re.search(r"0\.0\.0\.0\s+0\.0\.0\.0\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", out_route)
            if match_r:
                return match_r.group(1)
        except Exception:
            pass
        return "192.168.1.1"

    def register_callback(self, cb):
        self.callbacks.append(cb)

    def start(self):
        if not self.is_running:
            self.is_running = True
            threading.Thread(target=self._monitor_loop, daemon=True).start()

    def stop(self):
        self.is_running = False

    def _ping_target(self, ip, timeout_ms=1000):
        is_win = platform.system().lower() == "windows"
        cmd = ["ping", "-n", "1", "-w", str(timeout_ms), ip] if is_win else ["ping", "-c", "1", "-W", "1", ip]
        
        try:
            t0 = time.time()
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=2.0)
            dt = (time.time() - t0) * 1000.0
            
            if proc.returncode == 0:
                match = re.search(r"(?:tiempo|time)[=<](\d+)ms", proc.stdout, re.IGNORECASE)
                if match:
                    return True, int(match.group(1))
                elif "<1ms" in proc.stdout or "<1" in proc.stdout:
                    return True, 1
                return True, int(dt)
        except Exception:
            pass
        return False, 0

    def _monitor_loop(self):
        while self.is_running:
            gw_ok, gw_ms = self._ping_target(self.gateway_ip)
            wan_ok, wan_ms = self._ping_target(self.wan_ip)
            
            self.gateway_online = gw_ok
            self.gateway_ms = gw_ms if gw_ok else 0
            
            self.wan_online = wan_ok
            self.wan_ms = wan_ms if wan_ok else 0
            
            # Calculate health score
            if not gw_ok and not wan_ok:
                self.health_score = 0
            elif gw_ok and not wan_ok:
                self.health_score = 40
            elif gw_ok and wan_ok:
                if wan_ms > 150:
                    self.health_score = 75
                else:
                    self.health_score = 100
                    
            now_str = datetime.now().strftime("%H:%M:%S")
            self.gateway_history.append({"time": now_str, "online": gw_ok, "ms": gw_ms})
            self.wan_history.append({"time": now_str, "online": wan_ok, "ms": wan_ms})
            
            # Notify callbacks
            for cb in self.callbacks:
                try:
                    cb(self)
                except Exception:
                    pass
                    
            time.sleep(self.check_interval)
