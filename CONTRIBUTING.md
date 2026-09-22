# Guía de Contribución para IP_Scan_Tools 🤝

¡Gracias por tu interés en contribuir a **IP_Scan_Tools**! Este proyecto es de código abierto y agradecemos sugerencias, correcciones de errores, mejoras de rendimiento y nuevas características.

---

## 🛠️ Entorno de Desarrollo Local

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/tu-usuario/IP_Scan_Tools.git
   cd IP_Scan_Tools
   ```

2. **Crear y activar un entorno virtual**:
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Ejecutar en modo desarrollo**:
   ```bash
   python gui_app.py
   ```

---

## 📌 Guía de Estilo y Código

- Respeta la arquitectura modular del proyecto: mantén la lógica de red (ARP, ICMP, DNS) desacoplada de la interfaz gráfica (`CustomTkinter`).
- Los métodos y procesos que realicen operaciones de red bloqueantes (sockets, subprocess, peticiones HTTP) **siempre** deben ejecutarse en hilos secundarios (`threading.Thread(daemon=True)`) y actualizar la interfaz gráfica usando `self.after(0, ...)`.
- Escribe código limpio, documentado y tipado cuando sea posible.
- Si agregas una nueva dependencia externa, agrégala en `requirements.txt`.

---

## 🚀 Flujo de Trabajo para Pull Requests (PR)

1. Haz un **Fork** del proyecto.
2. Crea una rama para tu función o corrección:
   ```bash
   git checkout -b feature/nueva-herramienta-o-fix
   ```
3. Realiza tus cambios y verifica que no existan errores de sintaxis ni de ejecución:
   ```bash
   python -m py_compile gui_app.py scanner.py
   ```
4. Haz commit de tus cambios con mensajes claros y descriptivos:
   ```bash
   git commit -m "feat: agregar exportación de resultados a CSV"
   ```
5. Sube tus cambios a tu repositorio:
   ```bash
   git push origin feature/nueva-herramienta-o-fix
   ```
6. Abre un **Pull Request** detallando tus cambios y el problema que resuelven.

---

## 🐛 Reportar Problemas (Issues)

Si encuentras un bug o un comportamiento inesperado:
1. Revisa si ya existe un Issue abierto reportando lo mismo.
2. Si no existe, abre un nuevo Issue indicando:
   - Sistema Operativo y versión (ej. Windows 11 Pro 23H2).
   - Versión de Python (`python --version`).
   - Descripción detallada del error y traza de error completa (traceback).
   - Pasos exactos para reproducirlo.
