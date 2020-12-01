#!/usr/bin/python3
import os, sys
import time

import hue
import keyboard
import freq

cycleNoteFreq = 0

def key_press(key):
  print("key: {}".format(key.name))
  if key.name == 'b':
      print("blue")
      hue.lightSet(hue.lamp4_id, 254, hue.blue)
  if key.name == 'r':
      print("red")
      hue.lightSet(hue.lamp4_id, 254, hue.red)
  if key.name == 'y':
      hue.lightSet(hue.lamp4_id, 254, hue.yellow)
  if key.name == 'g':
      hue.lightSet(hue.lamp4_id, 254, hue.green)
  if key.name == 'space':
      print("off")
      hue.lightToggle(hue.lamp4_id)
  if key.name == 'c':
      # cycle through notes
      global cycleNoteFreq
      cycleNoteFreq = 1
  if key.name == 'q':
      quit()

keyboard.on_press(key_press)

# ode to joy freq  (middle C)
G = 185
A = 208
B = 234
C = 248
D = 278
def musicalSequence():
    global A,B,C,D,G
    # these are the recorded freq from the piano
    return [
        [B,B,C,D, D,C,B,A, G,G,A,B, B,A,A],
        [B,B,C,D, D,C,B,A, G,G,A,B, A,G,G],
        [A,A,B,G, A,B,C,B, G,A,B,C,B, A,G,A,D],
        [B,B,C,D, D,C,B,A, G,G,A,B, A,G,G]
        ]

def freqToNote(freq):
    global A,B,C,D,G
    freqs = [
    [A,"A"],
    [B,"B"],
    [C,"C"],
    [D,"D"],
    [G,"G"]
    ]
    for f in freqs:
        if f[0] == freq:
            return f[1]
    return "unknown"


def main():
    global cycleNoteFreq
    # Misc variables for program controls
    volume = -1       # volume level
    min_vol = 4   # zero is loudest possible input level
    min_freq = 170  # ignore anything under this Hz
    max_freq = 1000  # ignore anything above this Hz

    seq = musicalSequence()
    bar_colours = [hue.green, hue.red, hue.blue, hue.yellow]
    err = 6
    bar = 0
    note = 0
    match = 0
    edge_detected_cnt = 0
    force_edge = False

    # turn off all the lights first
    hue.lightOff(hue.lamp1_id)
    hue.lightOff(hue.lamp2_id)
    hue.lightOff(hue.lamp3_id)
    hue.lightOff(hue.lamp4_id)

    SR=freq.SoundRecorder()
    while True:
        #try:
        SR.getAudio()  #### raw_data_signal is the input signal data
        #except:
        #    print("SOMETHING WRONG WITH getAudio")
        #    continue
        try:
            f = SR.freq_from_autocorr()
        except:
            print("SOMETHING WRONG WITH freq_from_autocorr")
            continue

        # need to detect the edge
        # if the volume has gone up significantly, it's
        # probably a new note being pressed
        edge_delta = 3

        # sometimes the volume oscillates (up to 3 units of volume in some
        # cases). This doesn't happen across one sample though. so the
        # edge detection should not pick this up.
        # regardless, having an edge_delta that's larger than this oscillation
        # will guarentee we don't falsely detect an edge in this case.
        # typical edge from quiet to a key press is on the range of 15.0->0.5

        last_volume = volume
        volume = SR.volume()  #### find the volume from the audio sample

        edge_detected = False
        if volume != -1:
            if volume < (last_volume - edge_delta) or force_edge==True:
                edge_detected = True
                edge_detected_cnt += 1

        # if the edge occurs in the middle of a buffer we can detect an edge
        # but the volume and freq will be wrong.
        # ignore the first edge, take the second
        if edge_detected_cnt == 1:
            edge_detected = False
            force_edge = True
            # the next loop will detect an edge with a full buffer
            continue

        # it's a edge with valid readings
        # reset the count so we can detect another edge
        edge_detected_cnt = 0
        force_edge = False

        # for testing notes with keyboard 'c'
        if cycleNoteFreq != 0:
            cycleNoteFreq = 0

            # make cycling work
            volume = min_vol + 1
            edge_detected = True

            # cycling may want to start over
            if bar >= len(seq) and note >= len(seq[newbar]):
                print("cycling starting over")
                bar = 0
                note = 0
                hue.lightOff(hue.lamp1_id)
                hue.lightOff(hue.lamp2_id)
                hue.lightOff(hue.lamp3_id)
                hue.lightOff(hue.lamp4_id)

            newbar = bar
            if note >= len(seq[newbar]):
                newbar = bar + 1
                note = 0
            f = seq[newbar][note]
            print ("cycle note {}".format(f))
        else: # not in 'testing' mode
            # only process signal above certain volume
            # (lower is louder)
            if volume > min_vol:
                continue
            if f < min_freq:
                # ignore some frequencies
                continue
            if f > max_freq:
                # ignore some frequencies
                # sometimes high harmonics are picked up
                continue
            if edge_detected == False:
                continue

        print ("freq {} volume {} last_volume {} edge {}".format(f, volume, last_volume, edge_detected))

        min_note = min(map(min, seq)) - err*2
        max_note = max(map(max, seq)) + err*2
        #print ("min_note {} max_note {}".format(min_note, max_note))

        # determine where we are in the sequence and set the lights appropriately
        if f >= (seq[bar][note]-err) and f <= (seq[bar][note]+err):
            match += 1
            print("------------------")
            print ("matched {} note {} in bar {} for {} times".format(f, note, bar, match))
        elif f < min_note or f > max_note:
            # the note is outside of our valid notes - start over
            print ("note is outside of range {}".format(f))
            match = 0
            note = 0
            bar = 0
        else:
            # the note is out of sequence - start over
            print ("note {} is out of sequence, expecting {},{} {} {}".format(f, bar, note, seq[bar][note], freqToNote(seq[bar][note])))
            match = 0
            note = 0
            bar = 0
        if match:
            # if we get a match,
            # flash light, go brighter, then move to next note
            note += 1
            match = 0
            hue.lightOff(hue.lamp4_id)
            #time.sleep(0.25) # CAUSES PULSE AUDIO TO ASSERT
            if note >= len(seq[bar]):
                # we've reached the end of the bar, move to next bar
                bar += 1
                note = 0
            if bar < len(seq):
                hue.lightSet(hue.lamp4_id, int(254*note/len(seq[bar])), bar_colours[bar])

        if bar >= len(seq):
            # we're done the song
            # flash the 4 light in the 4 colours
            hue.lightAlert(hue.lamp4_id, 254, hue.green)
            hue.lightAlert(hue.lamp1_id, 254, hue.blue)
            hue.lightAlert(hue.lamp2_id, 254, hue.red)
            hue.lightAlert(hue.lamp3_id, 254, hue.yellow)

        elif bar == 0 and note == 0:
            # they messed up - turn off the light
            hue.lightOff(hue.lamp4_id)

        # end while
    SR.close()

def destroy():
    hue.lightOff(hue.lamp1_id)
    hue.lightOff(hue.lamp2_id)
    hue.lightOff(hue.lamp3_id)
    hue.lightOff(hue.lamp4_id)
    #SR.close()

if __name__ == '__main__':     # Program entrance
    try:
        main()
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        destroy()
