import pyaudio

p = pyaudio.PyAudio()

if __name__ == "__main__":
   for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:  # Filter to show only input devices
            print(f"Device {i}: {device_info['name']}")

    # stereo_mix_index = None
    # for i in range(p.get_device_count()):
    #     device_info = p.get_device_info_by_index(i)
    #     if "Stereo Mix" in device_info['name']:  # Search by name
    #         stereo_mix_index = i
    #         print(f"Found 'Stereo Mix' at device index {stereo_mix_index}")
        