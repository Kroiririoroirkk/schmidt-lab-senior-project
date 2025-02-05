import os
import random
import shutil

INPUT_FOLDER = 'S2024_wavs/cut_wavs/orange_none_song_type_1'
OUTPUT_FOLDER = 'S2024_wavs/cut_wavs/orange_none_song_type_1_blind'

fnames = list(os.listdir(INPUT_FOLDER))
random.shuffle(fnames)
with open(os.path.join(OUTPUT_FOLDER, 'randomization_key.txt'), 'w') as f:
    filetext = ''
    for i, fname in enumerate(fnames):
        filetext += f'song{i+1:04d}.wav {fname}\n'
    f.write(filetext)

for i, fname in enumerate(fnames):
    new_fname = f'song{i+1:04d}.wav'
    shutil.copy2(os.path.join(INPUT_FOLDER, fname),
                 os.path.join(OUTPUT_FOLDER, new_fname))
