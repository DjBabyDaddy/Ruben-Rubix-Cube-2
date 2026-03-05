import sounddevice as sd

print("\n🎤 Scanning macOS for active microphones...\n")
devices = sd.query_devices()

for index, device in enumerate(devices):
    if device['max_input_channels'] > 0:
        print(f"ID [{index}] - {device['name']}")