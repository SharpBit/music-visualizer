import sys

import matplotlib.pyplot as plt

import midi

try:
    filepath = sys.argv[1]
except IndexError:
    print("Enter path to midi file as argument\nExample: python run.py sample.mid")
else:
    pattern = midi.read_midifile(filepath)
# Use absolute ticks instead of relative ticks to make everything easier to work with
pattern.make_ticks_abs()

# with open("22.txt", "w+") as f:
#     f.write(str(pattern))

tracks = []
tempos = []
tempo_timestamps = []  # List[[seconds since beginning, tick, seconds per tick]]
for track in pattern:
    # Different tracks should definitely not have different tempos at once
    track_tempos = [[note.get_bpm(), note.tick] for note in track if note.name == "Set Tempo"]
    if len(track_tempos) > 0:
        tempos = track_tempos
        for change in tempos:
            microseconds_per_beat = 60 * 1000000 / change[0]
            seconds_per_tick = microseconds_per_beat / pattern.resolution / 1000000.0
            try:
                pt = tempo_timestamps[-1]
                tempo_timestamps.append([pt[0] + (change[1] - pt[1]) * pt[2], change[1], seconds_per_tick])
            except IndexError:
                # First tempo change: 0 seconds since track started, tick 0
                tempo_timestamps.append([0, 0, seconds_per_tick])

    # Get all the notes where velocity != 0; if velocity = 0, it is the equivalent of NoteOff
    notes = [note for note in track if note.name == "Note On" and note.velocity != 0]
    freq = [2 ** ((note.pitch - 69) / 12) * 440 for note in notes]  # Midi number converted to Frequency (Hz)

    #  A list of the time, in seconds, since the beginning of the track, of all the notes in the track
    time = []
    for note in notes:
        last_tempo_change = 0
        for i, t in enumerate([t[0] for t in tempo_timestamps]):
            # Find the last tempo change before the note's tick
            if t < note.tick:
                last_tempo_change = i
                break

        pt = tempo_timestamps[last_tempo_change]
        # The time, in seconds, of the note based on the current tempo
        time.append(pt[0] + (note.tick - pt[1]) * pt[2])
    tracks += [time, freq]

plt.plot(*tracks)  # Each track gets separated into a different line on the graph
plt.show()
