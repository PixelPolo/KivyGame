import random

from kivy import platform
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import Clock, StringProperty
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
    cloud_speed = 1
    cloud_alt = 0.75  # * self.height

    drop = None
    drop_speed = dp(1/150)
    drop_list = []

    points = 0
    scoretext = StringProperty("Score : " + str(points))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Keyboard binding
        if self.is_desktop():
            self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self.keyboard.bind(on_key_down=self.on_key_down)
            self.keyboard.bind(on_key_up=self.on_key_up)

        Clock.schedule_interval(self.update, self.game_fps)
        Clock.schedule_interval(self.cloud_update, self.cloud_speed)

    # pour éviter que le clavier apparaisse sur mobile
    def is_desktop(self):
        if platform in ("linux", "win", "macosx"):
            return True
        return False

    # If Virtual Keyboard
    def keyboard_closed(self):
        self.keyboard.unbind(on_key_down=self.on_key_down)
        self.keyboard.unbind(on_key_up=self.on_key_up)
        self.keyboard = None

    def create_a_boat(self):
        self.boat = BoatWidget()
        self.boat.pos = self.center_x - self.boat.width / 2, self.height * 0.075
        self.add_widget(self.boat)

    def create_a_cloud(self):
        # Create a cloud
        self.cloud = CloudWidget()
        self.cloud.pos = self.center_x - self.cloud.width / 2, self.height * self.cloud_alt
        self.add_widget(self.cloud)

    def new_game(self):
        self.create_a_boat()
        self.create_a_cloud()
        self.points = 0
        self.game_start = True

    def on_press_startbutton(self):
        self.new_game()
        # hide and disabled the startbutton
        self.ids.startbutton.opacity = 0
        self.ids.startbutton.disabled = True
        # reset the scorelabel size and pos
        self.ids.scorelabel.pos = self.width - self.ids.scorelabel.width, self.height - self.ids.scorelabel.height
        self.ids.scorelabel.font_size = dp(15)
        self.ids.scorelabel.text = "Score : " + str(self.points)

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

    # Check collisions
    def check_collides_boat_drop(self):
        if len(self.drop_list) > 0:
            for i in self.drop_list:
                if self.boat.collide_widget(i):
                    return True
                return False

    # Delete all Widget
    def delete_all_widgets(self):
        self.remove_widget(self.boat)
        self.remove_widget(self.cloud)
        self.remove_widget(self.drop)
        for i in self.drop_list:
            self.remove_widget(i)
        self.drop_list = []

    # Game over -> Show score and start button for restart
    def game_over(self):
        self.game_start = False
        # Show score in window center
        self.ids.scorelabel.font_size = dp(50)
        self.ids.scorelabel.pos = self.center_x - self.ids.scorelabel.width / 2, \
                                  self.center_y + self.ids.scorelabel.height
        # Appear and active startbutton
        self.ids.startbutton.opacity = 1
        self.ids.startbutton.disabled = False
        self.delete_all_widgets()

    def cloud_update(self, dt):
        if self.game_start:
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

    def update(self, dt):

        time_factor = dt * 60  # almost 1 when 1/60 fps.
        # if cpu is 2 times slower, dt == 2, so we have to refresh 2 times faster = 120.
        # this only for boat and rain speed

        if self.game_start:

            # Move the boat
            speed_x = self.boat_speed_x * self.width    # to adjust speed by window size
            speed_y = self.boat_speed_y * self.height   # to adjust speed by window size
            boat_pos_x, boat_pos_y = self.boat.pos
            boat_pos_x += speed_x * time_factor
            boat_pos_y += speed_y * time_factor
            self.boat.pos = boat_pos_x, boat_pos_y

            # Fall the drops in list
            speed = self.drop_speed * self.height       # to adjust speed by window size
            if len(self.drop_list) > 0:
                for i in self.drop_list:
                    x, y = i.pos
                    y -= speed * time_factor
                    # When a Drop is at the bottom of the window
                    if y < 0:
                        # remove last drop in list and last drop widget
                        self.drop_list.remove(i)
                        self.remove_widget(i)
                        # update score
                        self.points += 1
                        self.scoretext = "Score : " + str(self.points)
                    else:
                        i.pos = x, y

            # maj sizes if window changes -> Check .kv files for values
            self.boat.size_hint = .15, .15
            self.cloud.size_hint = .15, .2

            # Check collides
            self.check_collides_boat_drop()
            self.check_boat_collides_wall()

            if self.check_collides_boat_drop():
                self.game_over()
