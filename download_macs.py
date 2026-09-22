import json
from mac_vendor_lookup import MacLookup

def build_json():
    mac = MacLookup()
    mac.update_vendors()
    # Ensure it's populated
    vendors = {}
    for k, v in mac.prefixes.items():
        # mac_vendor_lookup stores prefix as string or bytes, let's normalize
        key = k.decode('utf-8') if isinstance(k, bytes) else k
        val = v[0].decode('utf-8') if isinstance(v[0], bytes) else v[0] # mac.prefixes has values as tuple/list depending on version
        # Let's check exactly how it's stored. Usually it's just dict[str, list/str]
        
        # let's format key (it might be like '000000', convert to '00:00:00')
        if len(key) == 6:
            key = f"{key[0:2]}:{key[2:4]}:{key[4:6]}"
        
        # if val is a list/tuple, get first item
        if isinstance(v, (list, tuple)):
            vendor = v[0]
            if isinstance(vendor, bytes):
                vendor = vendor.decode('utf-8')
        else:
            vendor = v
            if isinstance(vendor, bytes):
                vendor = vendor.decode('utf-8')
                
        vendors[key.lower()] = vendor

    with open('mac_vendors.json', 'w', encoding='utf-8') as f:
        json.dump(vendors, f, indent=4)
    print(f"Saved {len(vendors)} vendors to mac_vendors.json")

if __name__ == '__main__':
    build_json()
