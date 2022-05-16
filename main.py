
from kivy.config import Config
from kivy.properties import ObjectProperty

Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '700')

from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager


class MainGame(ScreenManager):

    app_start_sound = None
    game_sound = ObjectProperty(None)
    stage_sound = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.init_audio()
        self.app_start_sound.play()
        self.game_sound.play()

    def init_audio(self):
        # Songs from https://mixkit.co/
        self.app_start_sound = SoundLoader.load("songs/app_start.wav")
        self.app_start_sound.volume = .25
        self.game_sound = SoundLoader.load("songs/game_song.mp3")
        self.game_sound.volume = .1
        self.game_sound.loop = True
        self.stage_sound = SoundLoader.load("songs/stage_song.mp3")
        self.stage_sound.volume = .1
        self.stage_sound.loop = True


class Game(App):
    pass


Game().run()
