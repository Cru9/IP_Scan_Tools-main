"""
================================================================================
IP_Scan_Tools - Suite de Monitoreo de Red, Wi-Fi, Seguridad & Velocidad
Propiedad y Desarrollo por: Ezequiel Díaz
Todos los derechos reservados © 2026 Ezequiel Díaz
================================================================================
"""

import threading
try:
    from plyer import notification
except ImportError:
    notification = None

def notify(title, message):
    def _send():
        if notification:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="IP_Scan_Tools",
                    timeout=5
                )
            except Exception as e:
                print(f"[Notificación Error] {e}")
        else:
            print(f"[{title}] {message}")

    threading.Thread(target=_send, daemon=True).start()
