import matplotlib.pyplot as plt
import mpl_point_clicker
import numpy as np
import os
import scipy.io.wavfile
import scipy.signal
import sys

FS = 48000
WAV_FOLDER = 'S2024_wavs/cut_wavs/song_type_1_blind'
OUTPUT_FILE = 'S2024_wavs/note_annotations.txt'
LO_FREQ = 200
HI_FREQ = 7000
START_TIME = 0.1
END_TIME = 0.9
START_I = int(FS*START_TIME)
END_I = int(FS*END_TIME)
NFFT = 512
HOP = 32
FILTER_ORDER = 2
BANDPASS_FREQS = [(335, 270, 400, 40), (420, 360, 480, 30), (1600, 1400, 1800, 15)] # Middle, low, high, noise power
DEFAULT_FREQ_I = 0
Y_SCALE = 5
CUTOFF_CATEGORY_NAME = 'cutoff'
MARKER_CATEGORY_NAME = 'note_boundary'

def calc_closest(f):
    closest_i = 0
    closest_d = abs(f-BANDPASS_FREQS[0][0])
    for i, tup in enumerate(BANDPASS_FREQS):
        d = abs(f-tup[0])
        if d < closest_d:
            closest_i = i
            closest_d = d
    return closest_i

def annotate_wavfile(fname):
    fs, wav_data = scipy.io.wavfile.read(fname)
    if fs != FS:
        raise ValueError(f'Sampling rate was expected to be {FS} Hz.')

    def butter_bandpass_filter(x, lo, hi, fs, order):
        b, a = scipy.signal.butter(order, [lo, hi], fs=fs, btype='band')
        return scipy.signal.filtfilt(b, a, x)

    fig, axes = plt.subplots(nrows=2, ncols=1, constrained_layout=True)

    SFT = scipy.signal.ShortTimeFFT(scipy.signal.windows.hann(NFFT, False), HOP, FS)
    spectro = np.log(SFT.spectrogram(wav_data))
    axes[0].imshow(spectro,
                cmap='cividis',
                origin='lower',
                extent=(0, wav_data.shape[0]/FS, 0, FS/2),
                aspect='auto')
    axes[0].set_xlim((START_TIME, END_TIME))
    axes[0].set_ylim((LO_FREQ, HI_FREQ))

    lo_freq_line = False
    hi_freq_line = False
    vert_lines = []
    def calculate_bandpasses(freq_i):
        nonlocal lo_freq_line, hi_freq_line, vert_lines
        _, lo_cutoff_freq, hi_cutoff_freq, noise_power = BANDPASS_FREQS[freq_i]

        if lo_freq_line:
            lo_freq_line.remove()
        lo_freq_line = axes[0].axhline(lo_cutoff_freq, linestyle='--', c='navy')
        if hi_freq_line:
            hi_freq_line.remove()
        hi_freq_line = axes[0].axhline(hi_cutoff_freq, linestyle='--', c='navy')

        t_axis = np.linspace(0, wav_data.shape[0]/FS, wav_data.shape[0])
        bandpassed_wav_data = butter_bandpass_filter(wav_data,
                                                     lo_cutoff_freq,
                                                     hi_cutoff_freq,
                                                     FS,
                                                     FILTER_ORDER)
        wav_envelope = np.abs(scipy.signal.hilbert(bandpassed_wav_data))
        axes[1].clear()
        axes[1].plot(t_axis, bandpassed_wav_data, c='royalblue')
        axes[1].plot(t_axis, wav_envelope, c='red')
        axes[1].axhline(noise_power, linestyle='--', c='red')
        axes[1].set_xlim((START_TIME, END_TIME))
        axes[1].set_ylim((-1*Y_SCALE*noise_power, Y_SCALE*noise_power))

        for (line0, line1) in vert_lines:
            axes[1].add_line(line1)

        fig.canvas.draw()
        fig.canvas.flush_events()

    calculate_bandpasses(DEFAULT_FREQ_I)

    klicker_ax0 = mpl_point_clicker.clicker(
        axes[0],
        [CUTOFF_CATEGORY_NAME],
        markers=['']
    )
    klicker_ax1 = mpl_point_clicker.clicker(
        axes[1],
        [MARKER_CATEGORY_NAME],
        markers=['']
    )
    notes = []

    def process_point_added0(click_pos, click_type):
        freq_i = calc_closest(click_pos[1])
        calculate_bandpasses(freq_i)
        klicker_ax0.clear_positions()
    def process_point_added1(click_pos, click_type):
        x_val = click_pos[0]
        notes.append(x_val)
        klicker_ax1.set_positions({MARKER_CATEGORY_NAME: [(x,0) for x in notes]})
        line0 = axes[0].axvline(x_val, c='navy')
        line1 = axes[1].axvline(x_val, c='navy')
        vert_lines.append((line0, line1))
        fig.canvas.draw()
        fig.canvas.flush_events()
    klicker_ax0.on_point_added(process_point_added0)
    klicker_ax1.on_point_added(process_point_added1)

    def process_point_removed1(click_pos, click_type, click_order):
        for line in vert_lines[click_order]:
            line.remove()
        del notes[click_order]
        del vert_lines[click_order]
        fig.canvas.draw()
        fig.canvas.flush_events()
    klicker_ax1.on_point_removed(process_point_removed1)

    for ax in axes:
        ax.get_legend().remove()
    fig.suptitle(fname)
    plt.show()

    notes = np.array(notes)
    if notes.shape[0] % 2 != 0:
        raise ValueError('Number of points needs to be divisible by two.')
    notes = np.reshape(notes, shape=(-1,2))
    notes = notes[notes[:,0].argsort()]
    return notes

if __name__ == '__main__':
    try:
        arg = None
        fnames = sorted(os.listdir(WAV_FOLDER))
        if len(sys.argv) > 1:
            arg = sys.argv[1]
            try:
                fnames = fnames[fnames.index(arg):]
            except ValueError:
                raise ValueError(f'File "{arg}" not found.')
        print('Starting song annotation program... press Ctrl+C to terminate.')
        for fname in fnames:
            if not fname.lower().endswith('.wav'):
                print(f'Skipping {fname} since it is not a .wav file.')
                continue
            print(f'Now annotating {fname}...')
            def annotate():
                try:
                    notes = annotate_wavfile(os.path.join(WAV_FOLDER, fname))
                    if notes.size == 0:
                        raise ValueError('No points labeled.')
                    return notes
                except ValueError as e:
                    print(f'Error while processing {fname}:', e)
                    return annotate()
            notes = annotate()

            with open(OUTPUT_FILE, 'a') as f:
                datastring = ' '.join(str(x) for x in notes.flatten())
                f.write(fname + ' ' + datastring + '\n')
                print(f'Notes annotated for {fname} saved:\n{notes}')
    except ValueError as e:
        print('Error:', e)
    except KeyboardInterrupt:
        print('Program terminated.')
