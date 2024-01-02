import os
import time

def check_new_files(directory, extension):
    existing_files = set()
    while True:
        current_files = set(os.listdir(directory))
        new_files = current_files - existing_files
        new_wav_files = [file for file in new_files if file.endswith(extension)]
        if new_wav_files:
            print(f"Found new {extension} files:", ", ".join(new_wav_files))
        existing_files = current_files
        time.sleep(10)  # checks every 10 seconds

if __name__ == "__main__":
    check_new_files('.', '.wav')