import logging
import traceback

from mopidy import core

import pykka

from .main_menu import MainMenu
from .tts import TTS

logger = logging.getLogger(__name__)


class TtsGpio(pykka.ThreadingActor, core.CoreListener):

    def __init__(self, config, core):
        super(TtsGpio, self).__init__()
        self.tts = TTS(self, config)
        self.menu = False
        self.core = core
        self.main_menu = MainMenu(self)

        self.tts_enabled = config['ttsgpio']['tts'];
        self.playlist_1 = config['ttsgpio']['playlist_1'];
        self.debug_gpio_simulate = config['ttsgpio']['debug_gpio_simulate']
        if self.debug_gpio_simulate:
            from .gpio_simulator import GpioSimulator
            self.simulator = GpioSimulator(self)
        else:
            from .gpio_input_manager import GPIOManager
            self.gpio_manager = GPIOManager(self, config['ttsgpio'])

    def track_playback_started(self, tl_track):
        self.speak_current_song(tl_track)

    def playback_state_changed(self, old_state, new_state):
        if self.debug_gpio_simulate:
            if new_state == core.PlaybackState.PLAYING:
                self.simulator.playing_led.select()
            else:
                self.simulator.playing_led.deselect()
        else:
            if new_state == core.PlaybackState.PLAYING:
                self.gpio_manager.set_led(True)
            else:
                self.gpio_manager.set_led(False)

    def input(self, input_event):
        logger.debug("event:"+str(input_event))
        try:
            if input_event['key'] == 'volume_up':
                if input_event['long'] and self.tts_enabled:
                    self.repeat()
                else:
                    current = self.core.mixer.get_volume().get()
                    current += 5
                    if current > 100:   # do not use values over 100
                        current = 100
                    if (self.core.playback.get_mute().get()):
                        self.core.mixer.set_mute(False)
                        logger.debug("unmuted")
                        current = 10    # initial value after unmuted
                    self.core.mixer.set_volume(current);
                    logger.debug("volume:"+str(current))
            elif input_event['key'] == 'volume_down':
                current = self.core.mixer.get_volume().get()
                if input_event['long']:
                    self.core.mixer.set_mute(True)
                    logger.debug("muted")
                else:
                    current -= 5
                    if current < 0:   # do not use negative values
                        current = 0
                    self.core.mixer.set_volume(current);
                logger.debug("volume:"+str(current))
            elif input_event['key'] == 'main' and input_event['long'] \
                    and self.tts_enabled and self.menu:
                self.exit_menu()
            elif input_event['key'] == 'playlist_1':
                list_uris = []
                files = self.core.playlists.get_items(uri=self.playlist_1).get()
                for ref in files:
                    list_uris.append(ref.uri)
                logger.debug("playlist_1:"+self.playlist_1+" contains:"+str(files))
                self.core.tracklist.clear()
                self.core.tracklist.add(uris=list_uris)
                self.core.playback.play()
            else:
                if self.menu and self.tts_enabled:
                    self.main_menu.input(input_event)
                else:
                    self.manage_input(input_event)

        except Exception:
            traceback.print_exc()

    def manage_input(self, input_event):
        if input_event['key'] == 'next':
            self.core.playback.next()
        elif input_event['key'] == 'previous':
            self.core.playback.previous()
        elif input_event['key'] == 'main':
            if input_event['long'] and self.core.playback.state.get() == core.PlaybackState.PLAYING:
                self.core.playback.stop()
            elif input_event['long'] and self.tts_enabled:
                self.menu = True
                self.main_menu.reset()
            else:
                if self.core.playback.state.get() == \
                        core.PlaybackState.PLAYING:
                    self.core.playback.pause()
                else:
                    self.core.playback.play()
                logger.debug("play status:"+self.core.playback.state.get())

    def repeat(self):
        if self.menu:
            self.main_menu.repeat()
        else:
            self.speak_current_song(self.core.playback.current_tl_track.get())

    def speak_current_song(self, tl_track):
        if tl_track is not None:
            artists = ""
            for artist in tl_track.track.artists:
                artists += artist.name + ","
            self.tts.speak_text(tl_track.track.name + ' by ' + artists)

    def exit_menu(self):
        self.menu = False

    def playlists_loaded(self):
        self.main_menu.elements[0].reload_playlists()
        self.tts.speak_text("Playlists loaded")
