import os
import json
import shutil
from mac_vendor_lookup import MacLookup

def download_and_create_json():
    print("Descargando/Actualizando base de datos de fabricantes MAC...")
    mac = MacLookup()
    mac.update_vendors()  # Esto descarga la última versión desde IEEE/mirror a ~/.cache/mac-vendors.txt
    
    cache_file = mac.cache_path
    
    if not os.path.exists(cache_file):
        print(f"Error: No se encontró el archivo {cache_file}")
        return
        
    vendors = {}
    with open(cache_file, 'r', encoding='utf-8') as f:
        for line in f:
            if ':' in line:
                parts = line.strip().split(':', 1)
                if len(parts) == 2:
                    prefix, vendor = parts
                    # Formatear el prefijo '286FB9' -> '28:6f:b9'
                    if len(prefix) == 6:
                        prefix_formatted = f"{prefix[0:2]}:{prefix[2:4]}:{prefix[4:6]}".lower()
                        vendors[prefix_formatted] = vendor
    
    output_file = 'mac_vendors.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(vendors, f, indent=4)
        
    print(f"Éxito: Se guardaron {len(vendors)} registros en {output_file}")

if __name__ == '__main__':
    download_and_create_json()
