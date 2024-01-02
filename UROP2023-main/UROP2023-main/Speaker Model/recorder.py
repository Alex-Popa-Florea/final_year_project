import sounddevice as sd
import wave
import time
import os

def record_audio(filename, duration, samplerate=44100):
    print(f"Recording {filename} for {duration} seconds...")
    audio_data = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=2, dtype='int16')
    sd.wait()
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())

if __name__ == "__main__":
    counter = 1
    while True:
        filename = f"recording_{counter}.wav"
        record_audio(filename, 20)
        counter += 1
        time.sleep(20)