import RPi.GPIO as GPIO
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock
import os  # Import os to run system commands

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
ON = False
OFF = True
PUMP_PINS = [26, 16, 21, 19]
BEVERAGE_LABELS = ["Lemonade", "Sweet Tea", "Orange Juice", "Cranberry Juice"]  # Updated Beverage labels
DRINK_LABELS = ["Sunset Refresher", "Arnold Palmer", "Cranberry Citrus Cooler", "Tropical Tea Blend"]  # Updated Drink labels
for pin in PUMP_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, OFF)

# Portion Sizes (in seconds for pump activation)
PORTION_SIZES = {
    "1.5oz": 22,  # Updated times for portion sizes
    "2.5oz": 36,
    "4oz": 60
}

# Mixed Drink Recipes
MIXED_DRINKS = {
    DRINK_LABELS[0]: [(2, "4oz"), (3, "4oz"), (0, "4oz")],  # Sunset Refresher
    DRINK_LABELS[1]: [(1, "4oz"), (0, "4oz"), (3, "1.5oz")],  # Arnold Palmer
    DRINK_LABELS[2]: [(3, "4oz"), (2, "4oz"), (0, "1.5oz")],  # Cranberry Citrus Cooler
    DRINK_LABELS[3]: [(1, "4oz"), (2, "4oz"), (0, "1.5oz"), (3, "1.5oz")]  # Tropical Tea Blend
}

# WASH Cycle Duration (in seconds)
WASH_DURATION = 30

# PRIME Cycle Duration (in seconds)
PRIME_DURATION = 5

# Set the screen size for 480x320
Window.size = (480, 320)
Window.fullscreen = True


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_layout()

    def create_layout(self):
        layout = GridLayout(rows=2, cols=4, spacing=5, padding=10)  # Adjusted to 2x4 layout
        self.add_widget(layout)

        self.buttons = [
            Button(text=label, font_size=15, text_size=(None, None), halign='center', valign='middle') for label in BEVERAGE_LABELS
        ]
        self.oz_button = Button(text="1.5oz", font_size=20)
        self.menu_button = Button(text="Menu", font_size=20)
        self.prime_button = Button(text="Prime", font_size=20)  # Prime button
        self.shutdown_button = Button(text="Shutdown", font_size=20)  # Shutdown button

        for i, button in enumerate(self.buttons):
            button.bind(on_press=lambda x, idx=i: self.pour(idx))
            button.bind(size=self.update_text_size)  # Adjust size dynamically
            layout.add_widget(button)

        self.oz_button.bind(on_press=self.change_oz)
        self.menu_button.bind(on_press=self.go_to_menu)
        self.prime_button.bind(on_press=self.run_prime_cycle)  # Bind prime cycle function
        self.shutdown_button.bind(on_press=self.shutdown_machine)  # Bind shutdown function

        layout.add_widget(self.oz_button)
        layout.add_widget(self.menu_button)
        layout.add_widget(self.prime_button)  # Add prime button to layout
        layout.add_widget(self.shutdown_button)  # Add shutdown button to layout

        self.oz_states = list(PORTION_SIZES.keys())
        self.oz_index = 0

    def pour(self, pump_index):
        portion_size = self.oz_states[self.oz_index]
        duration = PORTION_SIZES[portion_size]
        beverage_label = BEVERAGE_LABELS[pump_index]
        self.manager.get_screen("pour").set_message(f"Pouring {portion_size} of {beverage_label}")
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

    def run_prime_cycle(self, instance):
        self.manager.get_screen("pour").set_message("Running PRIME cycle")
        self.manager.current = "pour"
        for pin in PUMP_PINS:
            GPIO.output(pin, ON)
        Clock.schedule_once(lambda dt: [GPIO.output(pin, OFF) for pin in PUMP_PINS], PRIME_DURATION)
        Clock.schedule_once(self.return_to_main, PRIME_DURATION + 2)

    def shutdown_machine(self, instance):
        os.system("sudo shutdown -h now")

    def update_text_size(self, instance, size):
        instance.text_size = (instance.width, None)


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_layout()

    def create_layout(self):
        layout = GridLayout(rows=2, cols=3, spacing=5, padding=10)
        self.add_widget(layout)

        self.buttons = [
            Button(text=label, font_size=15, text_size=(None, None), halign='center', valign='middle') for label in DRINK_LABELS
        ]
        self.wash_button = Button(text="WASH", font_size=20)
        self.back_button = Button(text="Back", font_size=20)

        for i, button in enumerate(self.buttons):
            button.bind(on_press=lambda x, idx=i: self.make_drink(DRINK_LABELS[idx]))
            button.bind(size=self.update_text_size)  # Adjust size dynamically
            layout.add_widget(button)

        self.wash_button.bind(on_press=self.wash)
        self.back_button.bind(on_press=self.go_back)

        layout.add_widget(self.wash_button)
        layout.add_widget(self.back_button)

    def make_drink(self, drink_name):
        try:
            self.manager.get_screen("pour").set_message(f"Making {drink_name}")
            self.manager.current = "pour"
            recipe = MIXED_DRINKS[drink_name]

            # Schedule the pouring of each ingredient
            delay = 0
            for pump_index, portion in recipe:
                duration = PORTION_SIZES[portion]
                Clock.schedule_once(
                    lambda dt, idx=pump_index, dur=duration: self.activate_pump(idx, dur), delay
                )
                delay += duration

            # Schedule return to the menu after the last pour
            Clock.schedule_once(self.return_to_main, delay + 2)
        except Exception as e:
            print(f"Error while making drink: {e}")


    def activate_pump(self, pump_index, duration):
        try:
            GPIO.output(PUMP_PINS[pump_index], ON)
            Clock.schedule_once(lambda dt: GPIO.output(PUMP_PINS[pump_index], OFF), duration)
        except Exception as e:
            print(f"Error in activate_pump: {e}")


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
        try:
            self.manager.current = "menu"  # Ensure it goes back to the menu screen
        except Exception as e:
            print(f"Error returning to menu: {e}")


    def update_text_size(self, instance, size):
        instance.text_size = (instance.width, None)


class PourScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = GridLayout(rows=1, cols=1, padding=10)
        self.message_button = Button(text="", font_size=20)
        self.layout.add_widget(self.message_button)
        self.add_widget(self.layout)

    def set_message(self, message):
        self.message_button.text = message


class PumpApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(PourScreen(name="pour"))
        return sm


if __name__ == "__main__":
    try:
        PumpApp().run()
    except KeyboardInterrupt:
        GPIO.cleanup()
    except Exception as e:
        print(f"An error occurred: {e}")
        GPIO.cleanup()

GPIO.cleanup()
