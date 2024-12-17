import RPi.GPIO as GPIO 
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock
import os

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
ON = False
OFF = True
PUMP_PINS = [26, 16, 21, 19]
BEVERAGE_LABELS = ["Lemonade", "Sweet Tea", "Orange Juice", "Cranberry Juice"]
DRINK_LABELS = ["Sunset Refresher", "Arnold Palmer", "Cranberry Citrus Cooler", "Tropical Tea Blend"]

for pin in PUMP_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, OFF)

# Portion Sizes (seconds)
PORTION_SIZES = {
    "1.5oz": 22,
    "2.5oz": 36,
    "4oz": 60
}

# Recipes
RECIPES = {
    DRINK_LABELS[0]: [(2, "4oz"), (3, "4oz"), (0, "4oz")],
    DRINK_LABELS[1]: [(1, "4oz"), (0, "4oz")],
    DRINK_LABELS[2]: [(3, "4oz"), (2, "4oz"), (0, "1.5oz")],
    DRINK_LABELS[3]: [(1, "2.5oz"), (2, "2.5oz"), (0, "2.5oz"), (3, "2.5oz")]
}

WASH_TIME = 30  # Wash cycle duration
PRIME_TIME = 5  # Prime cycle duration

# Set window size
Window.size = (480, 320)
Window.fullscreen = True

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = GridLayout(rows=1, cols=1, padding=10)
        start_button = Button(
            text="Hello! Welcome to your personal drink machine!\nClick here to begin",
            font_size=20,
            halign="center",
            valign="middle",
            background_color=(0, 0.5, 1, 1),
            color=(1, 1, 1, 1)
        )
        start_button.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(start_button)
        self.add_widget(layout)

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = GridLayout(rows=2, cols=4, spacing=5, padding=10)
        self.add_widget(layout)

        self.buttons = [Button(text=label, font_size=15, background_color=(0.5, 0.5, 0.5, 1)) for label in BEVERAGE_LABELS]
        self.oz_button = Button(text="1.5oz", font_size=20, background_color=(0, 0.8, 0, 1))
        self.menu_button = Button(text="Menu", font_size=20, background_color=(0.8, 0.8, 0, 1))
        self.prime_button = Button(text="Prime", font_size=20, background_color=(1, 0.5, 0, 1))
        self.shutdown_button = Button(text="Shutdown", font_size=20, background_color=(1, 0, 0, 1))

        for i, button in enumerate(self.buttons):
            button.bind(on_press=lambda x, idx=i: self.pour(idx))
            layout.add_widget(button)

        layout.add_widget(self.oz_button)
        layout.add_widget(self.menu_button)
        layout.add_widget(self.prime_button)
        layout.add_widget(self.shutdown_button)

        self.oz_states = list(PORTION_SIZES.keys())
        self.oz_index = 0

        self.oz_button.bind(on_press=self.change_oz)
        self.menu_button.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        self.prime_button.bind(on_press=self.run_prime_cycle)
        self.shutdown_button.bind(on_press=self.shutdown_machine)

    def pour(self, pump_index):
        portion_size = self.oz_states[self.oz_index]
        duration = PORTION_SIZES[portion_size]
        self.activate_pump(pump_index, duration)

    def activate_pump(self, pump_index, duration):
        GPIO.output(PUMP_PINS[pump_index], ON)
        Clock.schedule_once(lambda dt: GPIO.output(PUMP_PINS[pump_index], OFF), duration)

    def change_oz(self, instance):
        self.oz_index = (self.oz_index + 1) % len(self.oz_states)
        self.oz_button.text = self.oz_states[self.oz_index]

    def run_prime_cycle(self, instance):
        for pin in PUMP_PINS:
            GPIO.output(pin, ON)
        Clock.schedule_once(lambda dt: [GPIO.output(pin, OFF) for pin in PUMP_PINS], PRIME_TIME)

    def shutdown_machine(self, instance):
        os.system("sudo shutdown -h now")

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = GridLayout(rows=2, cols=3, spacing=5, padding=10)
        self.add_widget(layout)

        self.buttons = [Button(text=label, font_size=15, background_color=(0.3, 0.6, 0.9, 1)) for label in DRINK_LABELS]
        self.wash_button = Button(text="WASH", font_size=20, background_color=(0.5, 0.5, 1, 1))
        self.back_button = Button(text="Back", font_size=20, background_color=(0.7, 0.7, 0.7, 1))

        for i, button in enumerate(self.buttons):
            button.bind(on_press=lambda x, idx=i: self.make_drink(DRINK_LABELS[idx]))
            layout.add_widget(button)

        layout.add_widget(self.wash_button)
        layout.add_widget(self.back_button)

        self.wash_button.bind(on_press=self.run_wash_cycle)
        self.back_button.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))

    def make_drink(self, drink_name):
        recipe = RECIPES[drink_name]
        for pump_index, portion in recipe:
            duration = PORTION_SIZES[portion]
            GPIO.output(PUMP_PINS[pump_index], ON)
            Clock.schedule_once(lambda dt: GPIO.output(PUMP_PINS[pump_index], OFF), duration)

    def run_wash_cycle(self, instance):
        for pin in PUMP_PINS:
            GPIO.output(pin, ON)
        Clock.schedule_once(lambda dt: [GPIO.output(pin, OFF) for pin in PUMP_PINS], WASH_TIME)

class CombineScreens(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(StartScreen(name="start"))
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(MenuScreen(name="menu"))
        return sm

if __name__ == "__main__":
    try:
        CombineScreens().run()
    except KeyboardInterrupt:
        GPIO.cleanup()
    except Exception as e:
        print(f"An error occurred: {e}")
        GPIO.cleanup()

GPIO.cleanup()
