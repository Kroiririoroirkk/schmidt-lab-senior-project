from collections import namedtuple
import matplotlib.pyplot as plt
import numpy as np
import os
import scipy.io.wavfile
import scipy.signal
import scipy.stats

FS = 48000
NOTE_ANNOTATION_FILE = 'S2024_wavs/note_annotations.txt'
WAV_FILE_FOLDER = 'S2024_wavs/cut_wavs'

Annotation = namedtuple('Annotation',
                        ['fname',
                         'NC0N1S',
                         'NC0N1E',
                         'NC1N1S',
                         'NC1N1E',
                         'NC1N2S',
                         'NC1N2E',
                         'directed'
])

annotations = []
with open(NOTE_ANNOTATION_FILE, 'r') as f:
    for line in f:
        fname, NC0N1S, NC0N1E, NC1N1S, NC1N1E, NC1N2S, NC1N2E, directed = line.split()
        annotations.append(Annotation(
            fname,
            float(NC0N1S),
            float(NC0N1E),
            float(NC1N1S),
            float(NC1N1E),
            float(NC1N2S),
            float(NC1N2E),
            directed
        ))

plt.hist([[a.NC0N1E-a.NC0N1S for a in annotations if a.directed == 'M'],
          [a.NC0N1E-a.NC0N1S for a in annotations if a.directed == 'F']],
         label=['MD', 'FD'])
plt.xlabel('Duration of NC0 N1')
plt.ylabel('Song count')
plt.title('Duration of NC0 N1 across MD and FD song')
plt.legend()
plt.show()

plt.hist([[a.NC1N1E-a.NC1N1S for a in annotations if a.directed == 'M'],
          [a.NC1N1E-a.NC1N1S for a in annotations if a.directed == 'F']],
         label=['MD', 'FD'])
plt.xlabel('Duration of NC1 N1')
plt.ylabel('Song count')
plt.title('Duration of NC1 N1 across MD and FD song')
plt.legend()
plt.show()

plt.hist([[a.NC1N2E-a.NC1N2S for a in annotations if a.directed == 'M'],
          [a.NC1N2E-a.NC1N2S for a in annotations if a.directed == 'F']],
         label=['MD', 'FD'])
plt.xlabel('Duration of NC1 N2')
plt.ylabel('Song count')
plt.title('Duration of NC1 N2 across MD and FD song')
plt.legend()
plt.show()

plt.hist([[a.NC1N2S-a.NC1N1E for a in annotations if a.directed == 'M'],
          [a.NC1N2S-a.NC1N1E for a in annotations if a.directed == 'F']],
         label=['MD', 'FD'])
plt.xlabel('Overlap between NC1 N1 and N2')
plt.ylabel('Song count')
plt.title('Overlap between NC1 N1 and N2 across MD and FD song')
plt.legend()
plt.show()

def wiener_entropy(x):
    _, Pxx = scipy.signal.welch(x)
    return scipy.stats.gmean(Pxx)/np.mean(Pxx)

nc0n1_entropies_md = []
nc0n1_entropies_fd = []
nc1n1_entropies_md = []
nc1n1_entropies_fd = []
for a in annotations:
    fs, wav_data = scipy.io.wavfile.read(os.path.join(WAV_FILE_FOLDER, a.fname))
    if fs != FS:
        raise ValueError(f'Expected sampling rate of {FS} Hz.')
    nc0n1_e = wiener_entropy(wav_data[int(a.NC0N1S*FS):int(a.NC0N1E*FS)])
    nc1n1_e = wiener_entropy(wav_data[int(a.NC1N1S*FS):int(a.NC1N1E*FS)])
    if a.directed == 'M':
        nc0n1_entropies_md.append(nc0n1_e)
        nc1n1_entropies_md.append(nc1n1_e)
    elif a.directed == 'F':
        nc0n1_entropies_fd.append(nc0n1_e)
        nc1n1_entropies_fd.append(nc1n1_e)

plt.hist([nc0n1_entropies_md, nc0n1_entropies_fd], label=['MD', 'FD'])
plt.xlabel('Wiener entropy of NC0 N1')
plt.ylabel('Song count')
plt.title('Wiener entropy of NC0 N1 across MD and FD song')
plt.legend()
plt.show()

plt.hist([nc1n1_entropies_md, nc1n1_entropies_fd], label=['MD', 'FD'])
plt.xlabel('Wiener entropy of NC1 N1')
plt.ylabel('Song count')
plt.title('Wiener entropy of NC1 N1 across MD and FD song')
plt.legend()
plt.show()
