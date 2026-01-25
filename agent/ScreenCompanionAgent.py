import serial
import serial.tools.list_ports
import json
import psutil
import time
import threading

def find_device():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        try:
            with serial.Serial(port.device, 115200, timeout=2) as ser:
                time.sleep(2)  # Wait for device to initialize
                ping = {"cmd": "DISCOVER","token": "COMPANION_SCREEN_V1"}
                ser.write(json.dumps(ping).encode('utf-8'))
                line = ser.readline().decode('utf-8').strip()
                if line:
                    resp = json.loads(line)
                    if resp.get("status") == "READY":
                        print(f"[Agent]: {resp.get('device')} READY.")
                        return port.device
        except:
            print(f"[ERROR] Error reading data from device")
            continue
    return None

def read_logs_from_device(ser, stop_event=None):
    while not stop_event.is_set() and ser.is_open:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    data = json.loads(line)
                    if data.get("type") == "log":
                        print(f"[CompanionScreen LOG] {data.get('msg')}")
            time.sleep(0.1)
        except:
            print(f"[ERROR] Error reading logs from device")
            continue

def main():
    while True:
        port_name = find_device()

        if port_name is not None:
            print(f"[Agent] Device found at {port_name}")
        else:
            print(f"[Agent] No device found. Retrying in 5 seconds...")
            time.sleep(5)
            continue

        with serial.Serial(port_name, 115200, timeout=1) as ser:
            print(f"[Agent] Connected to device at {port_name}")
            print(f"[Agent] Starting device monitoring on port {port_name}...")
            stop_event = threading.Event()
            thread = threading.Thread(target=read_logs_from_device, args=(ser, stop_event))
            thread.start()

            while True:
                try: 
                    stats = {
                        "type": "data",
                        "cpu": int(psutil.cpu_percent()),
                        "memory": int(psutil.virtual_memory().percent),
                        "disk": int(psutil.disk_usage('/').percent),
                        "gpu": 0  # Placeholder for GPU usage
                    }

                    ser.write((json.dumps(stats) + "\n").encode('utf-8'))
                    time.sleep(2)
                except serial.SerialException:
                    print(f"[ERROR] Lost connection to device at {port_name}")
                    break
                except Exception as e:
                    print(f"[ERROR] {str(e)}")
                    continue

            stop_event.set()
            thread.join(timeout=5)  # Timeout di 5 secondi per sicurezza
            if thread.is_alive():
                print("[WARNING] Log-reading thread did not terminate in time.")
            else:
                print("[INFO] Log-reading thread terminated successfully.")

if __name__ == "__main__":
    main()
