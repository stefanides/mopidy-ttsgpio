****************************
Mopidy-TtsGpio
****************************

Control mopidy without screen using GPIO and TTS

For example if you play "Rather Be - Clean Bandit" you will hear:

http://translate.google.com/translate_tts?tl=en&q=rather%20be%20by%20clean%20bandit

TTS changed to `Festival <http://www.cstr.ed.ac.uk/projects/festival/>`_. Install it before using TTSGPIO::

    sudo apt-get install festival


The idea is to develop with GPIO buttons something similar to `3rd generation Ipod shuffle control <http://youtu.be/TfZUcL700wQ?t=2m40s>`_

Features
========

- Led to see if it is playing
- Play/Pause
- Next/Previous track
- Select playlist
- Hear the song name (Text To Speech)
- Exit mopidy
- Shutdown
- Restart
- Check IP


Installation
============

To use this extension you need an internet conection for the tts.

Install by running::

    pip install Mopidy-TtsGpio

To access the GPIO pins in the raspberry pi you have to run mopidy with sudo::
	
	sudo mopidy



Configuration
=============

Before starting Mopidy, you must add configuration for
Mopidy-TtsGpio to your Mopidy configuration file::

    [ttsgpio]
    # Set to false to disable TTS
    tts = true
    # Set true to emulate GPIO buttons with on screen buttons
    debug_gpio_simulate = false 
    pin_button_main = 17
    pin_button_next = 22
    pin_button_previous = 23
    pin_button_vol_up = 24
    pin_button_vol_down = 25
    pin_play_led = 18
    
You can set the pins you would like to use. The numbers are in BCM mode. You can check `here <http://raspberrypi.stackexchange.com/a/12967>`_ to see the numbers for your board.
The buttons must be connected to GROUND.

Example:

[pin 17] - [Button] - [Ground]

Controls with TTS
=================

- main: play/pause. In menu select item
- main longpress: enter/exit menu
- vol_up longpress: repeat last sentence
- vol_down longpress: mutes volume
- next: in menu navigate to next item
- previous: in menu navigate to next item

Controls without TTS
=================

- main: play/pause
- vol_up
- vol_down longpress: mutes volume
- next
- previous

Project resources
=================

- `Source code <https://github.com/stefanides/mopidy-ttsgpio>`_
- `Original release <https://github.com/9and3r/mopidy-ttsgpio>`_

Changelog
=========

v1.1.0
----------------------------------------

- forked original https://github.com/9and3r/mopidy-ttsgpio
- allows configurable TTS support, skip menu if TSS disabled
- debugging logs for GPIO events

v1.0.2
----------------------------------------

- TTS changed to `Festival <http://www.cstr.ed.ac.uk/projects/festival/>`_
- Remove unused import

v1.0.1
----------------------------------------

- GPIO will be disabled if not enough permission

v1.0.0
----------------------------------------

- First working version
