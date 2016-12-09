import os
import logging
from threading import Thread

music_level = 30
logger = logging.getLogger(__name__)

class TTS():

    def __init__(self, frontend, config):
        self.frontend = frontend
        self.enabled = config['ttsgpio']['tts']
        logger.debug("tts enabled:"+ str(config['ttsgpio']['tts']))

    def speak_text(self, text):
        if (self.enabled):
            t = Thread(target=self.speak_text_thread, args=(text,))
            t.start()

    def speak_text_thread(self, text):
        os.system(' echo "' + text + '" | festival --tts')

