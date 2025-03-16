import pvleopard
import sounddevice as sd
import numpy as np

# Picovoice Leopard Access key
ACCESS_KEY = "+m8fc6ADaXGrBFjP2UEOpS9HZ+YxwEf80KobBbRfSytCwNELN6iOIw=="

# Initialize Leopard
leopard = pvleopard.create(ACCESS_KEY)

# Audio settings
SAMPLE_RATE = 16000  # Leopard requires 16kHz
CHANNELS = 1  # Mono input
DURATION = 3  # Recording duration in seconds

def record_audio():
    print("Speak now...")
    
    # Record audio using sounddevice
    audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=np.int16)
    sd.wait()  # Wait for recording to finish

    return audio.flatten()  # Convert to 1D array

def transcribe_and_detect():
    audio_data = record_audio()
    
    # Convert audio to text
    transcript, _ = leopard.process(audio_data)

    # Print what was spoken
    print("You said:", transcript)

    # Check if "red" was spoken
    if "red" in transcript.lower():
        print("Yes (RED detected)")
    else:
        print("No (Different word detected)")

if __name__ == "__main__":
    while True:
        transcribe_and_detect()

