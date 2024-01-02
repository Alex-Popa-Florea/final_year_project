import pyaudio
import wave


def record_audio(record_sec=10):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    RECORD_SECONDS = record_sec
    WAVE_OUTPUT_FILENAME = "output.wav"

    audio = pyaudio.PyAudio()

    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=0
    )

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

# convert to text
def transcribe_audio():
    model = whisper.load_model("base")
    f = open("transcript.txt", "w")
    
    while True:
        record_audio()
        # read wav file into whisper file
        audio = whisper.pad_or_trim(whisper.load_audio("output.wav"))
        transcription = whisper.transcribe(model, audio, task="translate")["text"]
        
        f.write(transcription + "\n")