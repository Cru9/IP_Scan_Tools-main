import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

ips = ['192.168.1.'+str(i) for i in range(1, 255)]
t=time.time()

def check(ip):
    try:
        res = subprocess.run(['ping', '-n', '1', '-w', '200', ip], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return res.returncode == 0
    except Exception:
        return False

with ThreadPoolExecutor(254) as ex:
    results = list(ex.map(check, ips))

print('Took:', time.time()-t)
