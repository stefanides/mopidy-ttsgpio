import logging
import time

import RPi.GPIO as GPIO

logger = logging.getLogger(__name__)
longpress_time = 0.3 # [seconds]
bounce_time = 20     # [miliseconds]

class GPIOManager():

    def __init__(self, frontend, pins):

        self.frontend = frontend

        self.correctlyLoaded = False

        # Variables to control if it is a longpress
        self.down_time = {}

        # Play Led
        self.led_pin = pins['pin_play_led']

        # store pins
        self.pins = pins 

        try:
            # GPIO Mode
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.led_pin, GPIO.OUT)

            # Next Button
            GPIO.setup(pins['pin_button_next'], GPIO.IN,
                       pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pins['pin_button_next'],
                                  GPIO.BOTH, callback=self.next, bouncetime=bounce_time)

            # Previous Button
            GPIO.setup(pins['pin_button_previous'], GPIO.IN,
                       pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pins['pin_button_previous'], GPIO.BOTH,
                                  callback=self.previous, bouncetime=bounce_time)

            # Volume Up Button
            GPIO.setup(pins['pin_button_vol_up'], GPIO.IN,
                       pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pins['pin_button_vol_up'], GPIO.BOTH,
                                  callback=self.vol_up, bouncetime=bounce_time)

            # Volume Down Button
            GPIO.setup(pins['pin_button_vol_down'], GPIO.IN,
                       pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pins['pin_button_vol_down'],
                                  GPIO.BOTH, callback=self.vol_down,
                                  bouncetime=bounce_time)

            # Main Button
            GPIO.setup(pins['pin_button_main'], GPIO.IN,
                       pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pins['pin_button_main'],
                                  GPIO.BOTH, callback=self.main, bouncetime=bounce_time)

            # playlist 1, only GPIO.FALLING
            GPIO.setup(pins['pin_button_playlist_1'], GPIO.IN,
                       pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pins['pin_button_playlist_1'],
                                  GPIO.FALLING, callback=self.playlist_1, bouncetime=bounce_time)

            # rotary defaults
            rotary = {}
            rotary['channel1'] = -1
            rotary['channel2'] = -1
            rotary['last_time'] = -1
            rotary['last_state'] = -1
            self.rotary = {}

            # rotary encoder volume, two pins, no bounce_time
            GPIO.setup(pins['pin_button_rotary_vol_1'], GPIO.IN,
                       pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pins['pin_button_rotary_vol_1'],
                                  GPIO.RISING, callback=self.rotary_vol)
            GPIO.setup(pins['pin_button_rotary_vol_2'], GPIO.IN,
                       pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pins['pin_button_rotary_vol_2'],
                                  GPIO.RISING, callback=self.rotary_vol)
            # rotary store value as event1
            self.rotary['volume_up'] = rotary

            # rotary encoder prev/next, two pins, no bounce_time
            GPIO.setup(pins['pin_button_rotary_prev_next_1'], GPIO.IN,
                       pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pins['pin_button_rotary_prev_next_1'],
                                  GPIO.RISING, callback=self.rotary_prev_next)
            GPIO.setup(pins['pin_button_rotary_prev_next_2'], GPIO.IN,
                       pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pins['pin_button_rotary_prev_next_2'],
                                  GPIO.RISING, callback=self.rotary_prev_next)
            # rotary store value as event1
            self.rotary['next'] = rotary

            self.correctlyLoaded = True

        except RuntimeError:
            logger.error("TTSGPIO: Not enough permission " +
                         "to use GPIO. GPIO input will not work")

    def set_led(self, led_state):
        logger.debug("LED:"+str(led_state))
        if self.correctlyLoaded:
            GPIO.output(self.led_pin, led_state)

    def handle_event_long(self, channel, event):
        gpio = GPIO.input(channel)
        logger.debug(event+":"+str(gpio))
        if gpio == 1:
            if self.down_time[event] >= 0:
                if self.down_time[event] + longpress_time > time.time():
                    self.frontend.input({'key': event, 'long': False})
                else:
                    self.frontend.input({'key': event, 'long': True})
            self.down_time[event] = -1
        else:
            self.down_time[event] = time.time()

    def handle_event(self, channel, event):
        gpio = GPIO.input(channel)
        logger.debug(event+":gpio:"+str(channel)+":"+str(gpio))
        if gpio == 0:
            self.frontend.input({'key': event, 'long': False})

    def handle_rotary_event(self, channel, channel1, channel2, event1, event2):
        rotary_status = self.rotary[event1]
        # based on the code from https://www.raspberrypi.org/forums/viewtopic.php?f=37&t=140250
        gpio1 = GPIO.input(channel1)
        gpio2 = GPIO.input(channel2)

        if gpio1 == rotary_status['channel1'] and gpio2 == rotary_status['channel2']:
           # Same interrupt as before (Bouncing)? ignore interrupt
           return 

        # remember new for next bouncing check
        self.rotary[event1]['channel1'] = gpio1
        self.rotary[event1]['channel2'] = gpio2

        if (gpio1 == 1 and gpio2 == 1) or (gpio1 == 0 and gpio2 == 0):
           if (channel == channel1 and gpio1 == 1) or (channel == channel2 and gpio1 == 0):
               # cannot change direction too fast - bouncing?
               if rotary_status['last_time'] + longpress_time < time.time() \
                   or rotary_status['last_state'] == 1:   
                       self.rotary[event1]['last_state'] = 1
                       self.rotary[event1]['last_time'] = time.time()
                       logger.debug("rotary "+event1+":gpio1:"+str(channel1)+":"+\
                           str(gpio1)+", gpio2:"+str(channel2)+":"+str(gpio2))
                       self.frontend.input({'key': event1, 'long': False})
           else:
               # cannot change direction too fast - bouncing?
               if rotary_status['last_time'] + longpress_time < time.time() \
                   or rotary_status['last_state'] == -1:
                       self.rotary[event1]['last_state'] = -1
                       self.rotary[event1]['last_time'] = time.time()
                       logger.debug("rotary "+event2+":gpio1:"+str(channel1)+":"+\
                           str(gpio1)+", gpio2:"+str(channel2)+":"+str(gpio2))
                       self.frontend.input({'key': event2, 'long': False})

    def previous(self, channel):
        self.handle_event(channel, 'previous')

    def next(self, channel):
        self.handle_event(channel, 'next')

    def main(self, channel):
        self.handle_event_long(channel, 'main')

    def vol_up(self, channel):
        self.handle_event(channel, 'volume_up')

    def vol_down(self, channel):
        self.handle_event_long(channel, 'volume_down')

    def playlist_1(self, channel):
        self.handle_event(channel, 'playlist_1')

    def rotary_vol(self, channel):
        self.handle_rotary_event(channel,
                                 self.pins['pin_button_rotary_vol_1'],
                                 self.pins['pin_button_rotary_vol_2'],
                                 'volume_up', 'volume_down')

    def rotary_prev_next(self, channel):
        self.handle_rotary_event(channel,
                                 self.pins['pin_button_rotary_prev_next_1'],
                                 self.pins['pin_button_rotary_prev_next_2'],
                                 'next', 'previous')
