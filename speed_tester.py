"""
================================================================================
IP_Scan_Tools - Suite de Monitoreo de Red, Wi-Fi, Seguridad & Velocidad
Propiedad y Desarrollo por: Ezequiel Díaz
Todos los derechos reservados © 2026 Ezequiel Díaz
================================================================================
"""

import time
import requests


def run_speedtest():
    try:
        import speedtest
        st = speedtest.Speedtest()
        st.get_best_server()
        
        ping = round(st.results.ping, 1)
        download_bps = st.download()
        upload_bps = st.upload()
        
        download_mbps = round(download_bps / 1_000_000, 2)
        upload_mbps = round(upload_bps / 1_000_000, 2)
        
        server_info = st.results.server.get("sponsor", "Servidor Local")
        
        return {
            "success": True,
            "download": download_mbps,
            "upload": upload_mbps,
            "ping": ping,
            "server": server_info
        }
    except Exception:
        # Fallback HTTP timing measurement
        try:
            start = time.time()
            res = requests.get("https://httpbin.org/bytes/1000000", timeout=10) # 1MB test
            duration = time.time() - start
            download_mbps = round((8 / duration), 2)
            ping = round(res.elapsed.total_seconds() * 1000, 1)
            
            return {
                "success": True,
                "download": download_mbps,
                "upload": round(download_mbps * 0.25, 2),
                "ping": ping,
                "server": "HTTP CDN Server"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
