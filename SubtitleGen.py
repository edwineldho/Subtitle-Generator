import pyaudio
import speech_recognition as sr
import re
import time
import threading
import tkinter as tk
from tkinter import scrolledtext

# Step 1: Record Audio in real-time chunks
def record_audio_stream(chunk_duration=2, format=pyaudio.paInt16, channels=1, rate=44100, chunk=1024, device_index=0):
    """Record audio in chunks of specified duration and yield raw audio data in real-time from the Microsoft Sound Mapper."""
    audio = pyaudio.PyAudio()

    # Open stream for recording using the device index (Microsoft Sound Mapper is typically index 0)
    stream = audio.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        input_device_index=device_index,
                        frames_per_buffer=chunk)
     
    try:
        while True:
            frames = []
            # Record the audio in chunks
            for _ in range(int(rate / chunk * chunk_duration)):
                data = stream.read(chunk)
                frames.append(data)
            
            audio_data = b''.join(frames)
            yield audio_data, rate
    
    except KeyboardInterrupt:
        print("Stopping recording...")
    
    finally:
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        audio.terminate()

# Step 2: Recognize Speech
def recognize_speech(audio_data, rate):
    """Uses Google Speech Recognition to transcribe the audio data."""
    recognizer = sr.Recognizer()
    audio_file = sr.AudioData(audio_data, rate, 2)  # The 2 is for 16-bit samples
    
    try:
        text = recognizer.recognize_google(audio_file)
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None

# Step 3: Process Text for Subtitles
def process_text_for_subtitles(transcript, max_words_per_subtitle=5):
    """Processes recognized text into subtitle chunks."""
    def add_punctuation(text):
        # Simple heuristic for adding punctuation
        text = re.sub(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\w)\s', '. ', text)
        return text

    transcript = add_punctuation(transcript)
    words = transcript.split()
    
    # Group the words into subtitle chunks
    subtitle_text = " ".join(words[:max_words_per_subtitle])
    return subtitle_text

# Step 4: Display Subtitles in the GUI (No timestamp)
def display_subtitles_in_gui(subtitle_text, text_widget):
    """Updates the GUI to display the subtitle without a timestamp."""
    text_widget.config(state=tk.NORMAL)
    text_widget.delete(1.0, tk.END)  # Clear the previous subtitle
    text_widget.insert(tk.END, f"{subtitle_text}\n")
    text_widget.see(tk.END)  # Scroll to the latest subtitle
    text_widget.config(state=tk.DISABLED)

# Threading function to handle audio recording and subtitle display
def subtitle_generator(chunk_duration, text_widget):
    # Start recording audio stream in real-time chunks using Microsoft Sound Mapper (index 0)
    audio_generator = record_audio_stream(chunk_duration=chunk_duration, device_index=0)

    for audio_data, rate in audio_generator:
        # Recognize speech from the current audio chunk
        transcript = recognize_speech(audio_data, rate)

        if transcript:
            # Process the transcript into a subtitle-friendly format
            subtitle_text = process_text_for_subtitles(transcript)

            # Display the generated subtitle
            display_subtitles_in_gui(subtitle_text, text_widget)

# Step 5: Initialize and Run the GUI
def run_gui():
    # Create the root window
    root = tk.Tk()
    root.title("Real-Time Subtitles")
    root.geometry("800x300")

    # Customize font style and size
    subtitle_font = ("Helvetica", 24, "bold")  # Choose a bigger, nicer font

    # Create a scrolled text widget to display subtitles, using the custom font
    subtitle_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, 
                                                 font=subtitle_font, bg="#282c34", fg="white")
    subtitle_display.pack(expand=True, fill=tk.BOTH)

    # Center the text in the display
    subtitle_display.tag_configure("center", justify="center")

    # Start the subtitle generation in a separate thread to avoid blocking the GUI
    thread = threading.Thread(target=subtitle_generator, args=(2, subtitle_display))
    thread.daemon = True
    thread.start()

    # Run the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    run_gui()
