#!/usr/bin/env python3
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

keyboard.on_press(key_press)

# ode to joy freq  (middle C)
def musicalSequence():
    # these are the recorded freq from the piano
    G = 185
    A = 208
    B = 234
    C = 248
    D = 278
    return [
    [B,B,C,D, D,C,B,A, G,G,A,B, B,A,A],
    [B,B,C,D, D,C,B,A, G,G,A,B, A,G,G],
    [A,A,B,G, A,B,C,B, G,A,B,C,B, A,G,A,D],
    [B,B,C,D, D,C,B,A, G,G,A,B, A,G,G]
    ]

def main():
    global cycleNoteFreq
    # Misc variables for program controls
    volume=0       # volume level
    min_vol = 15   # zero is loudest possible input level
    min_freq = 200  # ignore anything under 200Hz
    match_freq = 1  # number of loops to match freq before analyzing

    seq = musicalSequence()
    bar_colours = [hue.green, hue.red, hue.blue, hue.yellow]
    err = 4
    bar = 0
    note = 0
    match = 0

    # turn off all the lights first
    hue.lightOff(hue.lamp1_id)
    hue.lightOff(hue.lamp2_id)
    hue.lightOff(hue.lamp3_id)
    hue.lightOff(hue.lamp4_id)

    SR=freq.SoundRecorder()
    while True:
        SR.getAudio()  #### raw_data_signal is the input signal data
        volume = SR.volume()  #### find the volume from the audio sample
        f = SR.freq_from_autocorr()
        #print ("{} volume {}".format(f, volume))

        # for testing notes with keyboard 'c'
        if cycleNoteFreq != 0:
            cycleNoteFreq = 0

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
        else:
            # only process signal above certain volume
            # (lower is louder)
            if volume > min_vol:
                continue
            if f < min_freq:
                continue

        print ("freq {} volume {}".format(f, volume))

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
            #match = 0
            #note = 0
            #bar = 0
        else:
            # the note is out of sequence - start over
            print ("note is out of sequence {}".format(f))
            #match = 0
            #note = 0
            #bar = 0
        if match >= match_freq:
            # if we get a match <match_freq> times in a row, move to next note
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
