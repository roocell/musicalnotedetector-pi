import pyaudio
import os
import math
import sys
import random
import time
import numpy
from numpy import argmax, sqrt, mean, diff, log
from scipy import signal
from scipy.signal import blackmanharris, fftconvolve

import hue
import keyboard

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
    [B,B,C,D,D,C,B,A,G,G,A,B,B,A,A],
    [B,B,C,D,D,C,B,A,G,G,A,B,A,G,G],
    [A,A,B,G,A,B,C,B,G,A,B,C,B,A,G,A,D],
    [B,B,C,D,D,C,B,A,G,G,A,B,A,G,G]
    ]

# audio
def find(condition):
    res, = numpy.nonzero(numpy.ravel(condition))
    return res

# See http://www.swharden.com/blog/2013-05-09-realtime-fft-audio-visualization-with-python/
class SoundRecorder:

    def __init__(self):
        self.RATE=32000 # for logtech webcam
        #self.RATE=44100 # for usb microphone
        self.BUFFERSIZE=3072 #1024 is a good buffer size 3072 works for Pi
        self.secToRecord=.05
        self.threadsDieNow=False
        self.newAudio=False

    def setup(self):
        self.buffersToRecord=int(self.RATE*self.secToRecord/self.BUFFERSIZE)
        if self.buffersToRecord==0: self.buffersToRecord=1
        self.samplesToRecord=int(self.BUFFERSIZE*self.buffersToRecord)
        self.chunksToRecord=int(self.samplesToRecord/self.BUFFERSIZE)
        self.secPerPoint=1.0/self.RATE
        self.p = pyaudio.PyAudio()
        self.inStream = self.p.open(format=pyaudio.paInt16,channels=1,rate=self.RATE,input=True,frames_per_buffer=self.BUFFERSIZE)
        self.xsBuffer=numpy.arange(self.BUFFERSIZE)*self.secPerPoint
        self.xs=numpy.arange(self.chunksToRecord*self.BUFFERSIZE)*self.secPerPoint
        self.audio=numpy.empty((self.chunksToRecord*self.BUFFERSIZE),dtype=numpy.int16)

    def close(self):
        self.p.close(self.inStream)

    def getAudio(self):
        audioString=self.inStream.read(self.BUFFERSIZE)
        self.newAudio=True
        return numpy.fromstring(audioString,dtype=numpy.int16)

# See https://github.com/endolith/waveform-analyzer/blob/master/frequency_estimator.py
def parabolic(f, x):
    xv = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
    yv = f[x] - 1/4. * (f[x-1] - f[x+1]) * (xv - x)
    return (xv, yv)

# See https://github.com/endolith/waveform-analyzer/blob/master/frequency_estimator.py
def freq_from_autocorr(raw_data_signal, fs):
    corr = fftconvolve(raw_data_signal, raw_data_signal[::-1], mode='full')
    corr = corr[int(len(corr)/2):]
    d = diff(corr)
    start = find(d > 0)[0]
    peak = argmax(corr[start:]) + start -1
    px, py = parabolic(corr, peak)
    return fs / px

def loudness(chunk):
    data = numpy.array(chunk, dtype=float) / 32768.0
    ms = math.sqrt(numpy.sum(data ** 2.0) / len(data))
    if ms < 10e-8: ms = 10e-8
    return 10.0 * math.log(ms, 10.0)

def find_nearest(array, value):
    index = (numpy.abs(array - value)).argmin()
    return array[index]

def closest_value_index(array, guessValue):
    # Find closest element in the array, value wise
    closestValue = find_nearest(array, guessValue)
    # Find indices of closestValue
    indexArray = numpy.where(array==closestValue)
    # Numpys 'where' returns a 2D array with the element index as the value
    return indexArray[0][0]

def build_default_tuner_range():
    return {65.41:'C2',
            69.30:'C2#',
            73.42:'D2',
            77.78:'E2b',
            82.41:'E2',
            87.31:'F2',
            92.50:'F2#',
            98.00:'G2',
            103.80:'G2#',
            110.00:'A2',
            116.50:'B2b',
            123.50:'B2',
            130.80:'C3',
            138.60:'C3#',
            146.80:'D3',
            155.60:'E3b',
            164.80:'E3',
            174.60:'F3',
            185.00:'F3#',
            196.00:'G3',
            207.70:'G3#',
            220.00:'A3',
            233.10:'B3b',
            246.90:'B3',
            261.60:'C4',
            277.20:'C4#',
            293.70:'D4',
            311.10:'E4b',
            329.60:'E4',
            349.20:'F4',
            370.00:'F4#',
            392.00:'G4',
            415.30:'G4#',
            440.00:'A4',
            466.20:'B4b',
            493.90:'B4',
            523.30:'C5',
            554.40:'C5#',
            587.30:'D5',
            622.30:'E5b',
            659.30:'E5',
            698.50:'F5',
            740.00:'F5#',
            784.00:'G5',
            830.60:'G5#',
            880.00:'A5',
            932.30:'B5b',
            987.80:'B5',
            1047.00:'C6',
            1109.0:'C6#',
            1175.0:'D6',
            1245.0:'E6b',
            1319.0:'E6',
            1397.0:'F6',
            1480.0:'F6#',
            1568.0:'G6',
            1661.0:'G6#',
            1760.0:'A6',
            1865.0:'B6b',
            1976.0:'B6',
            2093.0:'C7'
            }


class MusicalNoteDetector(object):

    def main(self):
        global cycleNoteFreq
        # Build frequency, noteName dictionary
        tunerNotes = build_default_tuner_range()

        # Sort the keys and turn into a numpy array for logical indexing
        frequencies = numpy.array(sorted(tunerNotes.keys()))

        # Misc variables for program controls
        signal_level=0                              # volume level
        targetnote=0
        soundgate = 24                            # zero is loudest possible input level
        SR=SoundRecorder()                          # recording device (usb mic)

        seq = musicalSequence()
        bar_colours = [hue.green, hue.red, hue.blue, hue.yellow]
        err = 4
        bar = 0
        note = 0
        match = 0

        while 1:
            SR.setup()
            raw_data_signal = SR.getAudio()                                         #### raw_data_signal is the input signal data
            signal_level = round(abs(loudness(raw_data_signal)),2)                  #### find the volume from the audio sample
            inputnote = round(freq_from_autocorr(raw_data_signal,SR.RATE),2)    #### find the freq from the audio sample
            SR.close()
            #print ("{} signal_level {}".format(inputnote, signal_level))

            if inputnote > frequencies[len(tunerNotes)-1]:                        #### not interested in notes above the notes list
                continue
            if inputnote < frequencies[0]:                                     #### not interested in notes below the notes list
                continue
            if signal_level > soundgate:                                        #### basic noise gate to stop it guessing ambient noises
                continue


            targetnote = closest_value_index(frequencies, round(inputnote, 2))      #### find the closest note in the keyed array

            # for testing notes with keyboard 'c'
            if cycleNoteFreq != 0:
                cycleNoteFreq = 0

                newbar = bar
                if note >= len(seq[bar])-1:
                    newbar = bar + 1
                    note = 0
                inputnote = seq[newbar][note]
                print ("cycle note {}".format(inputnote))

            print ("freq {} level {} index {} note {}".format(inputnote, signal_level, targetnote, tunerNotes[frequencies[targetnote]]))

            min_note = min(map(min, seq)) - err*2
            max_note = max(map(max, seq)) + err*2
            #print ("min_note {} max_note {}".format(min_note, max_note))

            # determine where we are in the sequence and set the lights appropriately
            if inputnote >= (seq[bar][note]-err) and inputnote <= (seq[bar][note]+err):
                match += 1
                print ("matched {} note {} in bar {} for {} times".format(inputnote, note, bar, match))
            elif inputnote < min_note or inputnote > max_note:
                # the note is outside of our valid notes - start over
                print ("note is outside of range {}".format(inputnote))
                #match = 0
                #note = 0
                #bar = 0
            else:
                # the note is out of sequence - start over
                print ("note is out of sequence {}".format(inputnote))
                #match = 0
                #note = 0
                #bar = 0
            if match >= 1:
                # if we get a match three times in a row, move to next note
                note += 1
                match = 0
                hue.lightSet(hue.lamp4_id, int(254*note/len(seq[bar])), bar_colours[bar])
            if note >= len(seq[bar])-1):
                # we've reached the end of the bar, move to next bar
                bar += 1
                note = 0
                if bar < len(seq);
                  hue.lightSet(hue.lamp4_id, int(254*note/len(seq[bar])), bar_colours[bar])

            if bar >= len(seq):
                # we're done the song
                # flash the 4 light in the 4 colours
                hue.lightAlert(hue.lamp4_id, 254, green)
                hue.lightAlert(hue.lamp1_id, 254, blue)
                hue.lightAlert(hue.lamp2_id, 254, red)
                hue.lightAlert(hue.lamp3_id, 254, yellow)

            elif bar == 0 and note == 0:
                # they messed up - turn off the light
                hue.lightOff(hue.lamp4_id)

if __name__ == '__main__':
    MusicalNoteDetector().main()
