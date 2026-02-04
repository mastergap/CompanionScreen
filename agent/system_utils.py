import platform
from socket import socket
import subprocess
import psutil
import socket
import GPUtil

if platform.system() == "Windows":
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    except ImportError:
        print("Import error" + ImportError.msg.__str__())

class SystemUtils:

    def __init__(self):
            self.os_type = platform.system()

    def get_cpu(self):
        return int(psutil.cpu_percent())

    def get_memory(self):
        return int(psutil.virtual_memory().percent)

    def get_disk(self):
        return int(psutil.disk_usage('/').percent)

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 1)) # Non invia dati, serve solo a trovare l'IP locale
            local_ip = s.getsockname()[0]
        except:
            local_ip = "127.0.0.1"
        finally:
            s.close()

        return local_ip

    def get_os(self):
        return self.os_type

    def get_gpu_usage(self):
        """
        Gets GPU usage percentage.
        Supports NVIDIA GPUs via GPUtil.
        For other GPUs or systems, attempts platform-specific fallbacks.
        """
        try:
            # 1. Tries with GPUtil (NVIDIA GPUs)
            if GPUtil is not None:
                gpus = GPUtil.getGPUs()
                if gpus:
                    return int(gpus[0].load * 100)

            # 2. Windows fallback (Intel / AMD / Nvidia without GPUtil)
            # Use Windows Performance Counters via typeperf
            if self.os_type == "Windows":
                try:
                    cmd = 'typeperf "\\GPU Engine(*)\\Utilization" -sc 1'
                    output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode()
                    import re
                    matches = re.findall(r'"(\d+\.\d+)"', output)
                    if matches:
                        return int(float(matches[-1]))
                except:
                    pass

            # 3. MacOS fallback (Apple Silicon)
            if platform.system() == "Darwin":
                try:
                    # Utilizziamo powermetrics (richiede privilegi elevati o configurazione specifica)
                    # In alternativa, un metodo più "soft" per monitorare l'attività
                    cmd = ["sysctl", "-n", "machdep.cpu.brand_string"] # Esempio segnaposto
                    # macOS non espone facilmente la % GPU via CLI senza sudo
                    return 0 
                except:
                    pass

        except Exception as e:
            # In caso di qualsiasi errore (come quello di distutils), ritorna 0 
            # e stampa l'errore per debugging senza bloccare l'agente
            print(f"DEBUG: Error retrieving GPU: {e}")
            return 0

        return 0

    def get_volume(self):
        if self.os_type == "Windows":
            # get windows volume
            device_enumerator = AudioUtilities.GetDeviceEnumerator()
            
            devices = device_enumerator.GetDefaultAudioEndpoint(0, 0)
            
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            
            current_volume = volume.GetMasterVolumeLevelScalar()
            
            return round(current_volume * 100)
        elif self.os_type == "Linux":
             # get linux volume
            try:
                # Try PulseAudio first
                result = subprocess.run(['pactl', 'get-sink-volume', '@DEFAULT_SINK@'], capture_output=True, text=True)
                if result.returncode == 0:
                    import re
                    match = re.search(r'/ (\d+)%', result.stdout)
                    if match:
                        return int(match.group(1))
                # Fallback to ALSA
                result = subprocess.run(['amixer', 'get', 'Master'], capture_output=True, text=True)
                if result.returncode == 0:
                    match = re.search(r'\[(\d+)%\]', result.stdout)
                    if match:
                        return int(match.group(1))
            except Exception as e:
                print(f"DEBUG: Error retrieving volume: {e}")
                pass
            return 0
        elif self.os_type == "Darwin":
             # get MacOS volume
            try:
                result = subprocess.run(['osascript', '-e', 'output volume of (get volume settings)'], capture_output=True, text=True)
                if result.returncode == 0:
                    return int(result.stdout.strip())
            except Exception as e:
                print(f"DEBUG: Error retrieving volume: {e}")
                pass
            return 0
        else:
            return 0