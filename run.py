import matplotlib.pyplot as plt
# from scipy.fftpack import fft
# import numpy as np

import midi

# rate, data = wav.read('bells.wav')
# fft_out = fft(data)

# plt.plot(data, np.abs(fft_out))
# plt.show()

pattern = midi.read_midifile("strings.mid")
pattern.make_ticks_abs()

tracks = []
tempos = []
tempo_timestamps = []  # List[[sec, tick, seconds per tick]]
for track in pattern:
    # Different tracks should definitely not have different tempos at once
    track_tempos = [[note.get_bpm(), note.tick] for note in track if note.name == 'Set Tempo']
    if len(track_tempos) > 0:
        tempos = track_tempos
        for change in tempos:
            microseconds_per_beat = 60 * 1000000 / change[0]
            seconds_per_tick = microseconds_per_beat / pattern.resolution / 1000000.0
            try:
                pt = tempo_timestamps[-1]
                tempo_timestamps.append([pt[0] + (change[1] - pt[1]) * pt[2], change[1], seconds_per_tick])
            except IndexError:
                tempo_timestamps.append([0, 0, seconds_per_tick])

    notes = [note for note in track if note.name == 'Note On']
    pitch = [note.pitch for note in notes]
    time = []
    for note in notes:
        last_tempo_change = 0
        for i, t in enumerate([t[0] for t in tempo_timestamps]):
            if t < note.tick:
                last_tempo_change = i
                break

        pt = tempo_timestamps[last_tempo_change]
        time.append(pt[0] + (note.tick - pt[1]) * pt[2])
    tracks += [time, pitch]
plt.plot(*tracks)
plt.show()