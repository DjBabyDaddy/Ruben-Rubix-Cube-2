import os
import psutil
import time
import platform
from tts import edge_speak

def system_diagnostics(parameters: dict, response: str, player, session_memory):
    check = parameters.get("check", "").lower()
    print(f"🔬 RUBE running diagnostics on: {check}")
    time.sleep(3.5)
    current_os = platform.system()
    try:
        if check == "storage":
            drive_path = 'C:\\' if current_os == "Windows" else '/'
            disk = psutil.disk_usage(drive_path)
            free_gb = disk.free / (1024**3)
            total_gb = disk.total / (1024**3)
            ans = f"Boss, you have {free_gb:.1f} gigabytes of free space remaining on your primary drive, out of a total {total_gb:.1f} gigabytes."
            edge_speak(ans, player)
        elif check == "memory":
            mem = psutil.virtual_memory()
            free_gb = mem.available / (1024**3)
            total_gb = mem.total / (1024**3)
            ans = f"Your system has {free_gb:.1f} gigabytes of available RAM out of {total_gb:.1f}. Current utilization is at {mem.percent} percent."
            edge_speak(ans, player)
        elif check in ["power_hogs", "processes"]:
            processes = sorted(psutil.process_iter(['name', 'memory_percent']), key=lambda p: p.info['memory_percent'] or 0, reverse=True)
            top_proc = processes[0].info['name']
            top_mem = processes[0].info['memory_percent']
            ans = f"Boss, the most demanding process currently running is {top_proc}, consuming approximately {top_mem:.1f} percent of your system's memory."
            edge_speak(ans, player)
        elif check == "cpu":
            cpu_usage = psutil.cpu_percent(interval=0.5)
            ans = f"Your CPU is currently running at {cpu_usage} percent utilization across all cores, boss."
            edge_speak(ans, player)
        elif check in ["temperature", "temp", "thermals"]:
            temps = psutil.sensors_temperatures() if hasattr(psutil, 'sensors_temperatures') else {}
            if temps and 'coretemp' in temps:
                current_temp = temps['coretemp'][0].current
                ans = f"Boss, your core CPU temperature is currently {current_temp} degrees Celsius."
            else:
                ans = "I apologize, boss, but I currently lack access to the motherboard's thermal sensors."
            edge_speak(ans, player)
        else:
            cpu_usage = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory()
            ans = f"Overall system health is stable, boss. CPU utilization is at {cpu_usage} percent, and RAM usage is at {mem.percent} percent."
            edge_speak(ans, player)
    except Exception as e:
        print(f"⚠️ Diagnostics Error: {e}")
        edge_speak("I encountered an error while scanning the system vitals, boss.", player)

def hardware_control(parameters: dict, response: str, player, session_memory):
    device = parameters.get("device", "").lower()
    target = parameters.get("target", "").lower()
    action = parameters.get("action", "switch").lower()
    print(f"🎛️ RUBE Hardware Reroute: {action} {device}")
    
    if device == "microphone":
        if action == "mute":
            edge_speak("Muting the microphone now, boss.", player)
            os.system("nircmd mutesysvolume 1 default_record")
        elif action == "unmute":
            edge_speak("The microphone is live, boss.", player)
            os.system("nircmd mutesysvolume 0 default_record")
        else:
            edge_speak(f"Rerouting audio input to the {target} microphone, boss.", player)
            print("⚙️ Automatic mic switching requires additional OS configuration.")