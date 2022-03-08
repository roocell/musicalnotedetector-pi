# musicalnotedetector-pi
raspi project to use audio input to detect musical notes on a piano.

# Hardware
Logitech Webcam (for mic)

Adafruit Adafruit Voice Bonnet for Raspberry Pi -Two Speakers + Two Mics
https://www.adafruit.com/product/4757#technical-details

Keystudio Mic Hat (similar to Adafruit's)
https://wiki.keyestudio.com/Ks0314_keyestudio_ReSpeaker_2-Mic_Pi_HAT_V1.0

speaker via audio jack to verify microphone recording works

# test recording and sound
arecord --device=hw:1,0 --format S16_LE --rate 44100 -c 2 test.wav
aplay --device=plughw:0,0 test.wav    # to test raspi jack
aplay --device=plughw:1,0 test.wav    # to test mic hat jack

# or you can just plug in some headphones into the jack and listen to mic directly
arecord -f cd -Dhw:1 | aplay -Dhw:1

# Setup (start with buster)
sudo apt-get remove libportaudio2
sudo apt-get install libasound2-dev
git clone -b alsapatch https://github.com/gglockner/portaudio
cd portaudio
./configure && make
sudo make install
sudo ldconfig
cd ..
sudo pip3 install pyaudio
sudo pip3 install scipy

sudo pip3 install pynput

arecord -l
**** List of CAPTURE Hardware Devices ****
card 1: U0x46d0x821 [USB Device 0x46d:0x821], device 0: USB Audio [USB Audio]
 Subdevices: 1/1
 Subdevice #0: subdevice #0

configure .asound.rc per above

# some other links
https://zedic.com/raspberry-pi-usb-webcam-built-in-microphone/
https://makersportal.com/blog/2018/9/17/audio-processing-in-python-part-ii-exploring-windowing-sound-pressure-levels-and-a-weighting-using-an-iphone-x
https://github.com/Virtualan/musical-note-trainer/blob/master/NoteTrainer.py
https://towardsdatascience.com/understanding-audio-data-fourier-transform-fft-spectrogram-and-speech-recognition-a4072d228520

# hue
http://jheyman.github.io/blog/pages/HueRaspberryControl/

# neopixels
https://learn.adafruit.com/adafruit-neopixel-uberguide
https://learn.adafruit.com/adafruit-neopixel-uberguide/best-practices
https://learn.adafruit.com/neopixels-on-raspberry-pi

# Notes
I wrote this as part of a Christmas treasure hunt I set up for my kids every year.
This will detect the sound of a song played on a piano.
After each bar is played correctly it will flash a Hue bulb a particular colour.
If there are any mistakes the bulb will turn off.
After 3 bars are played correctly it will output a recording for the next clue.
