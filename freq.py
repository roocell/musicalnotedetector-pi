#!/usr/bin/env python3
import pyaudio
import numpy
import time
import math

# for freq_from_autocorr()
from scipy import signal
from scipy.signal import blackmanharris, fftconvolve

class SoundRecorder:

    def open(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,channels=1,rate=self.fs,input=True,frames_per_buffer=self.BUFFERSIZE)

    def close(self):
        self.p.close(self.stream)

    def __init__(self):
        self.fs = 32000
        self.BUFFERSIZE = 1024*4
        self.data = 0
        self.open()

    def getAudio(self):
        audioString=self.stream.read(self.BUFFERSIZE)
        x = numpy.fromstring(audioString,dtype=numpy.int16)
        self.data = x
        return x

    def freq(self):
        # Calculate the Fourier transform of the recorded signal
        fourier = numpy.fft.fft(self.data.ravel())
        # Extrat the fundamental frequency from it
        f_max_index = numpy.argmax(abs(fourier[:int(fourier.size/2)]))
        # Get the scale of frequencies corresponding to the numpy Fourier transforms definition
        freqs = numpy.fft.fftfreq(len(fourier))
        # And so the actual fundamental frequency detected is
        f_detected = freqs[f_max_index]*self.fs
        return f_detected

    def find(self, condition):
        res, = numpy.nonzero(numpy.ravel(condition))
        return res
    # See https://github.com/endolith/waveform-analyzer/blob/master/frequency_estimator.py
    def parabolic(self, f, x):
        xv = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
        yv = f[x] - 1/4. * (f[x-1] - f[x+1]) * (xv - x)
        return (xv, yv)

    # See https://github.com/endolith/waveform-analyzer/blob/master/frequency_estimator.py
    def freq_from_autocorr(self):
        corr = fftconvolve(self.data, self.data[::-1], mode='full')
        corr = corr[int(len(corr)/2):]
        d = numpy.diff(corr)
        try:
          start = self.find(d > 0)[0]
        except:
          start = 0
        peak = numpy.argmax(corr[start:]) + start -1
        px, py = self.parabolic(corr, peak)
        return self.fs / px

    def loudness(self, chunk):
        data = numpy.array(chunk, dtype=float) / 32768.0
        ms = numpy.sqrt(numpy.sum(data ** 2.0) / len(data))
        if ms < 10e-8: ms = 10e-8
        return 10.0 * math.log(ms, 10.0)

    # lower is louder
    def volume(self):
        return round(abs(self.loudness(self.data)),2)

def setup():
    return

def main():
    SR=SoundRecorder()
    while True:
        SR.getAudio()
        print("freq: {} level: {}".format(SR.freq(), SR.volume()))

def destroy():
    return

if __name__ == '__main__':     # Program entrance
    setup()
    try:
        main()
    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        destroy()
