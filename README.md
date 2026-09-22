# 📡 IP_Scan_Tools v2.0

> **Suite de Monitoreo de Red, Wi-Fi, Seguridad & Velocidad**  
> **Propiedad y Desarrollo Exclusivo de:** Ezequiel Díaz  
> **Copyright © 2026 Ezequiel Díaz. Todos los derechos reservados.**

---

## 🌟 Descripción General

**IP_Scan_Tools** es una aplicación de escritorio nativa de alto rendimiento desarrollada en Python y CustomTkinter. Proporciona una suite completa para el descubrimiento de dispositivos en red local, análisis de cobertura Wi-Fi segundo a segundo, monitoreo de salud de la conexión (*Heartbeat*), escaneo de puertos de seguridad y pruebas de velocidad.

---

## 🚀 Características Principales

1. **💻 Descubrimiento de Red & Dispositivos**:
   - Escaneo de subred por ARP de alta velocidad.
   - Identificación automática del fabricante por dirección MAC (OUI global).
   - Clasificación por categorías de hardware (PC, Móvil, TV, Impresora, Cámara, Router, Servidor/IoT).
   - Asignación de nombres personalizados y procesamiento 100% en tiempo real en memoria (sin archivos de base de datos).

2. **📶 Monitoreo de Cobertura Wi-Fi Segundo a Segundo**:
   - Detección de todas las redes Wi-Fi al alcance con SSIDs, BSSIDs, canales (1 a 177) y bandas de frecuencia (`2.4 GHz`, `5 GHz`, `6 GHz`).
   - Mapa de cobertura térmica dinámico (barras de potencia con indicadores de zona Verde/Amarillo/Naranja/Rojo).
   - Monitoreo gráfico continuo a 1 segundo de intervalo con cálculo de estabilidad y exportación de reportes detallados.

3. **🛡️ Monitor Heartbeat de Salud de Red & Internet**:
   - Monitoreo en tiempo real cada 3 segundos hacia el Router local y la WAN de Internet (`8.8.8.8`).
   - Cálculo automático del *Health Score* (0% a 100%) e identificación instantánea de caídas de servicio del ISP o desconexión local.
   - Indicadores interactivos en el encabezado superior de la aplicación.

4. **⚡ Herramientas Integradas de Diagnóstico**:
   - **Ping Continuo (`ping -t`)**: Gráfica en tiempo real, latencias mín/máx/prom y tasa de pérdida de paquetes.
   - **Escáner de Puertos**: Comprobación rápida de puertos comunes (21, 22, 23, 80, 443, 3389, etc.).
   - **SpeedTest**: Medición de latencia ping, velocidad de descarga y carga.
   - **Traceroute**: Trazado de ruta salto por salto.

---

## 🛠️ Requisitos e Instalación

### Requisitos del Sistema
- **Sistema Operativo**: Windows 10 / Windows 11.
- **Python**: Versión 3.10 o superior.

### Instalación de Dependencias

Abre una consola o PowerShell en el directorio de `IP_Scan_Tools` y ejecuta:

```bash
pip install -r requirements.txt
```

---

## 💻 Instrucciones de Uso

Para iniciar la aplicación gráfica **IP_Scan_Tools**:

- **Opción A (Fácil)**: Haz doble clic en el archivo `run_app.bat`.
- **Opción B (Consola)**: Ejecuta el siguiente comando en la terminal:

```bash
python gui_app.py
```

---

## ⚖️ Licencia y Propiedad Intelectual

Este software y su código fuente son **Propiedad Intelectual de Ezequiel Díaz**. Queda reservado todo derecho de reproducción, modificación y distribución sin el consentimiento expreso del autor.
