import os
import scipy.io.wavfile

FS = 48000
WORKING_FOLDER = 'S2024_wavs'
TIMESTAMP_FILE = 'S2024_wavs/song_timestamps.txt'
LOOK_BEHIND = 0.6 # In seconds
LOOK_AHEAD = 1.2 # In seconds
OUTPUT_FOLDER = 'S2024_wavs/cut_wavs'

def read_timestamp(s):
    start_time, _ = s.split('-')
    mins, secs = start_time.split(':')
    return int(mins)*60 + float(secs)

MD_count = 1
FD_count = 1
with open(TIMESTAMP_FILE, 'r') as f:
    for l in f:
        folder, fname, timestamps, directedness = l.strip().split()
        wav_path = os.path.join(WORKING_FOLDER, folder, fname)
        fs, wav_data = scipy.io.wavfile.read(wav_path)
        wav_data_chann = wav_data[:,0]
        if fs != FS:
            raise ValueError(f'Sampling rate was expected to be {FS} Hz.')
        first_time = read_timestamp(timestamps)
        first_i = int(first_time * FS)
        start_i = first_i - int(FS*LOOK_BEHIND)
        if start_i < 0:
            continue
        end_i = first_i + int(FS*LOOK_AHEAD)
        cut_wav_data = wav_data_chann[start_i:end_i]
        if directedness == 'M':
            output_fname = f'cut_song_MD_{MD_count:03d}.wav'
            MD_count += 1
        elif directedness == 'F':
            output_fname = f'cut_song_FD_{FD_count:03d}.wav'
            FD_count += 1
        else:
            raise ValueError('Directedness was expected to either be M or F.')
        scipy.io.wavfile.write(os.path.join(OUTPUT_FOLDER, output_fname), FS, cut_wav_data)
