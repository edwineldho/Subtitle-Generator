import pyaudio
import wave
import os

def list_audio_devices():
    """List all audio input devices, check which ones work, and return the list of working devices."""
    audio = pyaudio.PyAudio()
    working_devices = []

    print("Checking available audio input devices...\n")
    
    # Loop through each device and check if it can be opened for input
    for i in range(audio.get_device_count()):
        device_info = audio.get_device_info_by_index(i)
        device_name = device_info.get('name')
        device_index = device_info.get('index')
        max_input_channels = device_info.get('maxInputChannels')

        if max_input_channels > 0:
            print(f"Testing device {device_index}: {device_name} (Max Input Channels: {max_input_channels})")

            # Try to open the device as an input stream
            try:
                stream = audio.open(format=pyaudio.paInt16,  # 16-bit resolution
                                    channels=1,             # Mono channel
                                    rate=44100,             # Sampling rate: 44.1kHz
                                    input=True,             # Open as input device
                                    input_device_index=device_index,
                                    frames_per_buffer=1024) # Buffer size

                # If the stream opens successfully, it's a working device
                print(f"Device {device_index}: {device_name} is working!")
                working_devices.append((device_index, device_name))  # Save working device info
                stream.close()  # Close the stream

            except Exception as e:
                print(f"Device {device_index}: {device_name} does NOT work. Error: {e}")
        else:
            print(f"Device {device_index}: {device_name} is not an input device.")
    
    audio.terminate()
    
    return working_devices

def record_test_audio(device_index, device_name, record_seconds=5, format=pyaudio.paInt16, channels=1, rate=44100, chunk=1024):
    """Records a 5-second test audio from a given device and saves it to a file."""
    audio = pyaudio.PyAudio()

    print(f"\nRecording 5 seconds of audio from device {device_index}: {device_name}...")

    # Open stream for recording
    stream = audio.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        input_device_index=device_index,
                        frames_per_buffer=chunk)

    frames = []

    # Record audio in chunks
    for _ in range(0, int(rate / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)

    print(f"Finished recording from device {device_index}: {device_name}")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Create filename based on device name and index
    sanitized_device_name = device_name.replace(" ", "_").replace("/", "_")
    filename = f"test_audio_device_{device_index}_{sanitized_device_name}.wav"

    # Save the audio to a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(audio.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"Saved test audio to {filename}")

def main():
    # Step 1: List all audio devices and find the working ones
    working_devices = list_audio_devices()

    if working_devices:
        print("\nWorking Devices:")
        for device_index, device_name in working_devices:
            print(f"Device {device_index}: {device_name}")

        # Step 2: Record a 5-second test for each working device and save the file
        for device_index, device_name in working_devices:
            record_test_audio(device_index, device_name)
    else:
        print("No working devices found.")

if __name__ == "__main__":
    main()
