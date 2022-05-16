import random

from kivy import platform
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import Clock, StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget


Builder.load_file("Stage1.kv")


class BoatWidget(Widget):
    pass


class CloudWidget(Widget):
    pass


class DropWidget(Widget):
    pass


class ScoreWidget(BoxLayout):
    pass


class Stage1(RelativeLayout):

    game_fps = 1/60
    game_start = False

    boat = None
    boat_stop = dp(0)
    boat_speed_x = dp(0)
    boat_speed_y = dp(0)
    boat_speed_inc = dp(1/150)

    cloud = None
    counter = 0
    cloud_speed = 120  # 60 = 2 times faster
    cloud_alt = 0.75  # * self.height

    drop = None
    drop_speed = dp(1/175)
    drop_list = []

    points = 0
    scoretext = StringProperty("Score : " + str(points))

    game_start_sound = None
    stage_song = ObjectProperty(None)
    game_over_sound = None
    change_speed_sound = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.init_audio()

        # Keyboard binding
        if self.is_desktop():
            self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self.keyboard.bind(on_key_down=self.on_key_down)
            self.keyboard.bind(on_key_up=self.on_key_up)

        Clock.schedule_interval(self.update, self.game_fps)

    # To prevent a keyboard appears on mobile
    def is_desktop(self):
        if platform in ("linux", "win", "macosx"):
            return True
        return False

    # If Virtual Keyboard > unbind physical keyboard
    def keyboard_closed(self):
        self.keyboard.unbind(on_key_down=self.on_key_down)
        self.keyboard.unbind(on_key_up=self.on_key_up)
        self.keyboard = None

    # Increment the boat speed
    def on_key_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == "right" or text == "d":
            self.boat_speed_x = self.boat_speed_inc
        if keycode[1] == "left" or text == "a":
            self.boat_speed_x = -self.boat_speed_inc
        if keycode[1] == "up" or text == "w":
            self.boat_speed_y = self.boat_speed_inc
        if keycode[1] == "down" or text == "s":
            self.boat_speed_y = -self.boat_speed_inc

    # Stop the boat
    def on_key_up(self, keyboard, keycode):
        self.boat_speed_x = self.boat_stop
        self.boat_speed_y = self.boat_stop

    # Check boat collides wall
    def check_boat_collides_wall(self):
        boat_pos_x, boat_pos_y = self.boat.pos
        boat_size_x, boat_size_y = self.boat.size

        if boat_pos_x + boat_size_x > self.width:
            boat_pos_x = self.width - boat_size_x
        if boat_pos_x < 0:
            boat_pos_x = 0
        if boat_pos_y + boat_size_y > self.height / 3:
            boat_pos_y = self.height / 3 - boat_size_y
        if boat_pos_y < self.height * 0.075:
            boat_pos_y = self.height * 0.075

        self.boat.pos = boat_pos_x, boat_pos_y

    def create_a_boat(self):
        self.boat = BoatWidget()
        self.boat.pos = self.center_x - self.boat.width / 2, self.height * 0.075
        self.add_widget(self.boat)

    def create_a_cloud(self):
        self.cloud = CloudWidget()
        self.cloud.pos = self.center_x - self.cloud.width / 2, self.height * self.cloud_alt
        self.add_widget(self.cloud)

    def update_cloud_and_create_drop(self):
        # Random cloud_x
        cloud_size_x, cloud_size_y = self.cloud.size
        cloud_x = random.randint(0, int(self.width - cloud_size_x))
        cloud_y = self.height * self.cloud_alt
        self.cloud.pos = cloud_x, cloud_y
        # Creat a drop widget
        self.drop = DropWidget()
        self.drop_list.append(self.drop)
        self.drop.pos = cloud_x + cloud_size_x / 2, cloud_y
        self.add_widget(self.drop)

    def new_game(self):
        self.create_a_boat()
        self.create_a_cloud()
        self.points = 0
        self.game_start = True
        self.game_start_sound.play()
        self.delete_all_widgets()

    def on_press_startbutton(self):
        self.new_game()
        # hide and disabled the startbutton
        self.ids.startbutton.opacity = 0
        self.ids.startbutton.disabled = True
        # reset the scorelabel size and pos
        self.ids.scorelabel.pos = self.width - self.ids.scorelabel.width, self.height - self.ids.scorelabel.height
        self.ids.scorelabel.font_size = dp(15)
        self.ids.scorelabel.text = "Score : " + str(self.points)

    def delete_all_widgets(self):
        if self.boat is not None and self.cloud is not None and len(self.drop_list) != 0:
            self.remove_widget(self.boat)
            self.remove_widget(self.cloud)
            self.remove_widget(self.drop)
            for i in self.drop_list:
                self.remove_widget(i)
            self.drop_list = []

    # Game over > Show score and start button for restart
    def game_over(self):
        self.game_start = False
        # Show score in window center
        self.ids.scorelabel.font_size = dp(50)
        self.ids.scorelabel.pos = self.center_x - self.ids.scorelabel.width / 2, \
                                  self.center_y + self.ids.scorelabel.height
        # Appear and active startbutton
        self.ids.startbutton.opacity = 1
        self.ids.startbutton.disabled = False
        # Delete all widgets
        self.delete_all_widgets()
        # Reset cloud speed
        self.cloud_speed = 120
        self.game_over_sound.play()

    # Play the game !
    def update(self, dt):

        time_factor = dt * 60  # almost 1 when 1/60 fps.
        # If cpu 2 times slower, dt == 2, so we have to refresh 2 times faster = 120.
        # This only for the boat and the rain speed.

        if self.game_start:

            # Move the boat
            speed_x = self.boat_speed_x * self.width    # to adjust speed x by window size
            speed_y = self.boat_speed_y * self.height   # to adjust speed y by window size
            boat_pos_x, boat_pos_y = self.boat.pos
            boat_pos_x += speed_x * time_factor
            boat_pos_y += speed_y * time_factor
            self.boat.pos = boat_pos_x, boat_pos_y

            # Increment the counter
            self.counter += 1

            # Default cloud_speed == 120.
            if self.counter == self.cloud_speed:
                # Reser coutner, random cloud pos x and create a drop
                self.counter = 0
                self.update_cloud_and_create_drop()

            # Increment the cloud speed by score
            if self.points > 5:
                self.cloud_speed = 90
            if self.points > 10:
                self.cloud_speed = 60
            if self.points > 15:
                self.cloud_speed = 50
            if self.points > 20:
                self.cloud_speed = 40
            if self.points > 25:
                self.cloud_speed = 30
            if self.points > 30:
                self.cloud_speed = 20

            # Reset counter if counter > cloud speed
            if self.counter > self.cloud_speed:
                self.counter = 0

            # Fall the drops in list
            speed = self.drop_speed * self.height   # to adjust speed by window size
            if len(self.drop_list) > 0:
                for i in self.drop_list:
                    x, y = i.pos
                    y -= speed * time_factor
                    # When a Drop at the bottom of the window
                    if y < 0:
                        # remove last drop from list and last drop widget
                        self.drop_list.remove(i)
                        self.remove_widget(i)
                        # update score
                        self.points += 1
                        self.scoretext = "Score : " + str(self.points)
                    else:
                        i.pos = x, y

            # Play the change speed sound every 5 points
            if self.points % 5 == 0 and self.points != 0:
                self.change_speed_sound.play()

            # Maj sizes if window changes > Check .kv files for values.
            self.boat.size_hint = .10, .10
            self.cloud.size_hint = .15, .2

            # Check boat collides wall
            self.check_boat_collides_wall()

            # Check boat collides drop > game over !
            if len(self.drop_list) > 0:
                for i in self.drop_list:
                    if self.boat.collide_widget(i):
                        self.game_over()

    def init_audio(self):
        # Songs from https://mixkit.co/
        self.game_start_sound = SoundLoader.load("songs/game_start.wav")
        self.game_start_sound.volume = .1
        self.game_over_sound = SoundLoader.load("songs/game_over.wav")
        self.game_over_sound.volume = .1
        self.change_speed_sound = SoundLoader.load("songs/change_speed.wav")
        self.change_speed_sound.volume = .1




