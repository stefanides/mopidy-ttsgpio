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
        self.down_time_previous = -1
        self.down_time_next = -1
        self.down_time_main = -1
        self.down_time_vol_up = -1
        self.down_time_vol_down = -1

        # Play Led
        self.led_pin = pins['pin_play_led']

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

            self.correctlyLoaded = True

        except RuntimeError:
            logger.error("TTSGPIO: Not enough permission " +
                         "to use GPIO. GPIO input will not work")

    def set_led(self, led_state):
        logger.debug("LED:"+str(led_state))
        if self.correctlyLoaded:
            GPIO.output(self.led_pin, led_state)

    def handle_event(self, channel, event):
        gpio = GPIO.input(channel)
        logger.debug(event+":"+str(gpio))
        if gpio == 1:
            if self.down_time_next >= 0:
                if self.down_time_next + longpress_time > time.time():
                    self.frontend.input({'key': event, 'long': False})
                else:
                    self.frontend.input({'key': event, 'long': True})
            self.down_time_next = -1
        else:
            self.down_time_next = time.time()

    def previous(self, channel):
        self.handle_event(channel, 'previous')

    def next(self, channel):
        self.handle_event(channel, 'next')

    def main(self, channel):
        self.handle_event(channel, 'main')

    def vol_up(self, channel):
        self.handle_event(channel, 'volume_up')

    def vol_down(self, channel):
        self.handle_event(channel, 'volume_down')

    def playlist_1(self, channel):
        self.handle_event(channel, 'playlist_1')
