from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader  # For sound effects
from random import randint, choice
from kivy.core.window import Window

# Set window size for testing (Android will use the phone screen)
Window.size = (360, 640)

class Basket(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image = Image(source='basket.png', size=(100, 100))
        self.add_widget(self.image)
        self.image.pos = (self.center_x - 50, 50)

    def on_touch_move(self, touch):
        if touch.y < 200:  # Limit movement to the bottom part of the screen
            self.x = touch.x - self.width / 2
            self.image.x = self.x  # Move basket image with touch

class FallingObject(Image):
    speed = NumericProperty(10)

    def move(self):
        self.y -= self.speed  # Move object downwards

class CatchGame(Widget):
    score = NumericProperty(0)
    level = NumericProperty(1)
    level_threshold = NumericProperty(10)  # Points needed to level up
    game_speed = NumericProperty(1)
    missed_objects = NumericProperty(0)  # Track missed objects

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.basket = Basket()
        self.add_widget(self.basket)
        self.objects = []
        self.spawn_rate = 1.5  # Time between object spawns
        self.game_over = False  # Track if the game is over

        # Score, level, and missed objects labels
        self.score_label = Label(text=f"Score: {self.score}", pos=(10, Window.height - 30), font_size='20sp')
        self.level_label = Label(text=f"Level: {self.level}", pos=(Window.width - 100, Window.height - 30), font_size='20sp')
        self.missed_label = Label(text=f"Missed: {self.missed_objects}/3", pos=(Window.width / 2 - 50, Window.height - 30), font_size='20sp')
        self.add_widget(self.score_label)
        self.add_widget(self.level_label)
        self.add_widget(self.missed_label)

        # Load sound effects
        self.catch_sound = SoundLoader.load('catch_sound.wav')
        self.miss_sound = SoundLoader.load('miss_sound.wav')

        # Schedule updates
        Clock.schedule_interval(self.update, 1/60)  # 60 FPS
        Clock.schedule_interval(self.spawn_object, self.spawn_rate)

    def spawn_object(self, dt):
        if self.game_over:
            return

        # Randomly choose between a good object (fruit) or bad object (rock)
        object_type = choice(["fruit", "rock"])
        if object_type == "fruit":
            new_object = FallingObject(source="fruit.png", size=(50, 50))  # Good object
            new_object.is_good = True  # Mark as a good object
        else:
            new_object = FallingObject(source="rock.png", size=(50, 50))  # Bad object
            new_object.is_good = False  # Mark as a bad object

        new_object.x = randint(0, self.width - new_object.width)
        new_object.y = self.height
        new_object.speed = self.game_speed * 5
        self.add_widget(new_object)
        self.objects.append(new_object)

    def update(self, dt):
        if self.game_over:
            return

        # Move objects and check for collisions
        for obj in self.objects[:]:
            obj.move()
            if obj.collide_widget(self.basket.image):
                if obj.is_good:
                    self.score += 1  # Good object increases score
                    if self.catch_sound:
                        self.catch_sound.play()
                else:
                    self.score -= 1  # Bad object decreases score
                    if self.miss_sound:
                        self.miss_sound.play()

                self.remove_widget(obj)
                self.objects.remove(obj)

            elif obj.y < 0:  # Missed object
                if obj.is_good:
                    self.missed_objects += 1
                    if self.miss_sound:
                        self.miss_sound.play()

                self.remove_widget(obj)
                self.objects.remove(obj)

        # Update labels
        self.score_label.text = f"Score: {self.score}"
        self.level_label.text = f"Level: {self.level}"
        self.missed_label.text = f"Missed: {self.missed_objects}/3"

        # Check if player has reached the level-up threshold
        if self.score >= self.level_threshold * self.level:
            self.level_up()

        # Game over if too many objects are missed
        if self.missed_objects >= 3:
            self.end_game()

    def level_up(self):
        self.level += 1
        self.game_speed += 0.5  # Increase falling speed
        self.spawn_rate -= 0.1  # Increase object spawn rate
        Clock.unschedule(self.spawn_object)
        Clock.schedule_interval(self.spawn_object, self.spawn_rate)

    def end_game(self):
        self.game_over = True
        self.clear_widgets()
        game_over_label = Label(text=f"Game Over!\nFinal Score: {self.score}", font_size='30sp', pos=(Window.width / 2 - 100, Window.height / 2))
        self.add_widget(game_over_label)

        restart_label = Label(text="Tap to restart", font_size='20sp', pos=(Window.width / 2 - 50, Window.height / 2 - 50))
        self.add_widget(restart_label)

        # Restart game on touch
        self.bind(on_touch_down=self.restart_game)

    def restart_game(self, *args):
        # Reset game state
        self.clear_widgets()
        self.__init__()

class CatchApp(App):
    def build(self):
        return CatchGame()

if __name__ == '__main__':
    CatchApp().run()
