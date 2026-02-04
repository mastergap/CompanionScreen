import json
import time

from system_utils import SystemUtils

system_utils = SystemUtils()

def main():
    while True:
        try: 
            stats = {
                "type": "data",
                "cpu": system_utils.get_cpu(),
                "memory": system_utils.get_memory(),
                "disk":system_utils.get_disk(),
                "gpu": system_utils.get_gpu_usage(),
                "ip_address": system_utils.get_local_ip(),
                "os":system_utils.get_os(),
                "volume": system_utils.get_volume()
            }

            print((json.dumps(stats) + "\n").encode('utf-8'))
            time.sleep(5)
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            continue

if __name__ == "__main__":
    main()
