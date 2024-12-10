import RPi.GPIO as GPIO
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
ON = False
OFF = True
PUMP_PINS = [26, 16, 21, 19]
for pin in PUMP_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, OFF)

# Portion Sizes (in seconds for pump activation)
PORTION_SIZES = {
    "1.5oz": 7,  # Time in seconds for 1.5oz
    "2.5oz": 12,
    "4oz": 15
}

# Mixed Drink Recipes
MIXED_DRINKS = {
    "Drink A": [(0, "1.5oz"), (1, "2.5oz")],
    "Drink B": [(2, "4oz"), (3, "1.5oz")],
    "Drink C": [(0, "2.5oz"), (2, "1.5oz")],
    "Drink D": [(1, "4oz"), (3, "2.5oz")],
}

# WASH Cycle Duration (in seconds)
WASH_DURATION = 5

# Set the screen size for 480x320
Window.size = (480, 320)
Window.fullscreen = True


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_layout()

    def create_layout(self):
        layout = GridLayout(rows=2, cols=3, spacing=5, padding=10)
        self.add_widget(layout)

        self.yellow_button = Button(text="Yellow", font_size=20)
        self.green_button = Button(text="Green", font_size=20)
        self.red_button = Button(text="Red", font_size=20)
        self.clear_button = Button(text="Clear", font_size=20)
        self.oz_button = Button(text="1.5oz", font_size=20)
        self.menu_button = Button(text="Menu", font_size=20)

        self.yellow_button.bind(on_press=lambda x: self.pour(0))
        self.green_button.bind(on_press=lambda x: self.pour(1))
        self.red_button.bind(on_press=lambda x: self.pour(2))
        self.clear_button.bind(on_press=lambda x: self.pour(3))
        self.oz_button.bind(on_press=self.change_oz)
        self.menu_button.bind(on_press=self.go_to_menu)

        layout.add_widget(self.yellow_button)
        layout.add_widget(self.green_button)
        layout.add_widget(self.red_button)
        layout.add_widget(self.clear_button)
        layout.add_widget(self.oz_button)
        layout.add_widget(self.menu_button)

        self.oz_states = list(PORTION_SIZES.keys())
        self.oz_index = 0

    def pour(self, pump_index):
        portion_size = self.oz_states[self.oz_index]
        duration = PORTION_SIZES[portion_size]
        self.manager.get_screen("pour").set_message(f"Pouring {portion_size} from Pump {pump_index + 1}")
        self.manager.current = "pour"
        Clock.schedule_once(lambda dt: self.activate_pump(pump_index, duration), 1)
        Clock.schedule_once(self.return_to_main, duration + 2)

    def activate_pump(self, pump_index, duration):
        GPIO.output(PUMP_PINS[pump_index], ON)
        Clock.schedule_once(lambda dt: GPIO.output(PUMP_PINS[pump_index], OFF), duration)

    def change_oz(self, instance):
        self.oz_index = (self.oz_index + 1) % len(self.oz_states)
        self.oz_button.text = self.oz_states[self.oz_index]

    def go_to_menu(self, instance):
        self.manager.current = "menu"

    def return_to_main(self, dt):
        self.manager.current = "main"


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_layout()

    def create_layout(self):
        layout = GridLayout(rows=2, cols=3, spacing=5, padding=10)
        self.add_widget(layout)

        self.drink_a_button = Button(text="Drink A", font_size=20)
        self.drink_b_button = Button(text="Drink B", font_size=20)
        self.drink_c_button = Button(text="Drink C", font_size=20)
        self.drink_d_button = Button(text="Drink D", font_size=20)
        self.wash_button = Button(text="WASH", font_size=20)
        self.back_button = Button(text="Back", font_size=20)

        self.drink_a_button.bind(on_press=lambda x: self.make_drink("Drink A"))
        self.drink_b_button.bind(on_press=lambda x: self.make_drink("Drink B"))
        self.drink_c_button.bind(on_press=lambda x: self.make_drink("Drink C"))
        self.drink_d_button.bind(on_press=lambda x: self.make_drink("Drink D"))
        self.wash_button.bind(on_press=self.wash)
        self.back_button.bind(on_press=self.go_back)

        layout.add_widget(self.drink_a_button)
        layout.add_widget(self.drink_b_button)
        layout.add_widget(self.drink_c_button)
        layout.add_widget(self.drink_d_button)
        layout.add_widget(self.wash_button)
        layout.add_widget(self.back_button)

    def make_drink(self, drink_name):
        self.manager.get_screen("pour").set_message(f"Making {drink_name}")
        self.manager.current = "pour"
        recipe = MIXED_DRINKS[drink_name]
        delay = 1
        for pump_index, portion in recipe:
            duration = PORTION_SIZES[portion]
            Clock.schedule_once(lambda dt, p=pump_index, d=duration: self.activate_pump(p, d), delay)
            delay += duration
        Clock.schedule_once(self.return_to_main, delay + 2)

    def activate_pump(self, pump_index, duration):
        GPIO.output(PUMP_PINS[pump_index], ON)
        Clock.schedule_once(lambda dt: GPIO.output(PUMP_PINS[pump_index], OFF), duration)

    def wash(self, instance):
        self.manager.get_screen("pour").set_message("Running WASH cycle")
        self.manager.current = "pour"
        for pin in PUMP_PINS:
            GPIO.output(pin, ON)
        Clock.schedule_once(lambda dt: [GPIO.output(pin, OFF) for pin in PUMP_PINS], WASH_DURATION)
        Clock.schedule_once(self.return_to_main, WASH_DURATION + 2)

    def go_back(self, instance):
        self.manager.current = "main"

    def return_to_main(self, dt):
        self.manager.current = "main"


class PourScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = GridLayout(rows=1, cols=1, padding=10)
        self.message_button = Button(text="", font_size=20)
        self.layout.add_widget(self.message_button)
        self.add_widget(self.layout)

    def set_message(self, message):
        self.message_button.text = message


class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(PourScreen(name="pour"))
        return sm

    def on_stop(self):
        GPIO.cleanup()


if __name__ == "__main__":
    MyApp().run()
