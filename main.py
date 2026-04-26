import tkinter as tk
from abc import ABC, abstractmethod
import csv
import os

CONFIG_FILE = "engine_config.csv"

SIMULATION_SPEED_MS = 50

# Pagrindinė aplikacijos klasė
class App:
    def __init__(self, root, ecu):
        self._root = root
        self._ecu = ecu

        self._rpm_label = tk.Label(root, font=("Arial", 16))
        self._rpm_label.pack(pady=10)

        self._throttle_label = tk.Label(root, font=("Arial", 16))
        self._throttle_label.pack(pady=10)

        self._temp_label = tk.Label(root, font=("Arial", 16))
        self._temp_label.pack(pady=10)

        self._fan_label = tk.Label(root, font=("Arial", 16))
        self._fan_label.pack(pady=10)

        self._fuel_used_label = tk.Label(root, font=("Arial", 16))
        self._fuel_used_label.pack(pady=10)

        root.bind("<KeyPress-Up>", self.throttle_on)
        root.bind("<KeyRelease-Up>", self.throttle_off)

        self.update_loop()

    def update_display(self):
        engine = self._ecu.get_engine()

        self._rpm_label.config(text=f"RPM: {engine.get_rpm():.0f}")
        self._throttle_label.config(text=f"Throttle: {engine.get_throttle()}")
        self._temp_label.config(text=f"Temperature: {engine.get_temperature():.1f} C°")
        self._fan_label.config(text=f"Fan: {self._ecu.get_fan_speed()}")
        self._fuel_used_label.config(text=f"Fuel used: {engine.get_fuel_used():.4f} L")

    def throttle_on(self, event):
        self._ecu.set_throttle(1)

    def throttle_off(self, event):
        self._ecu.set_throttle(0)

    def update_loop(self):
        self._ecu.update()
        self.update_display()
        self._root.after(SIMULATION_SPEED_MS, self.update_loop)


# Variklio klasė
class Engine:
    def __init__(self, max_rpm=7000, idle_rpm=800, max_temp=120, rpm_increase_rate=0.08):
        # Konfigūracija
        self._max_rpm = max_rpm
        self._idle_rpm = idle_rpm
        self._max_temp = max_temp
        self._rpm_increase_rate = rpm_increase_rate

        # Būsena
        self._rpm = self._idle_rpm
        self._temperature = 0
        self._throttle = 0
        self._fuel_used = 0.0
        self._fuel_injection = 0.0

    def set_throttle(self, value):
        if value != 0 and value != 1:
            raise ValueError("Throttle can only be 0 or 1")

        self._throttle = value

    def set_fuel_injection(self, value):
        if value < 0:
            raise ValueError("Fuel injection cannot be negative")

        self._fuel_injection = value

    def set_temperature(self, value):
        self._temperature = value

    def update(self):
        target_rpm = self._idle_rpm + self._throttle * (self._max_rpm - self._idle_rpm)

        self._rpm += (target_rpm - self._rpm) * self._rpm_increase_rate

        if self._rpm < self._idle_rpm:
            self._rpm = self._idle_rpm

        if self._rpm > self._max_rpm:
            self._rpm = self._max_rpm

        self._fuel_used += self._fuel_injection * 0.05

    def get_rpm(self):
        return self._rpm

    def get_throttle(self):
        return self._throttle

    def get_temperature(self):
        return self._temperature

    def get_fuel_used(self):
        return self._fuel_used


# Tėvinė jutiklio klasė ir klasės, kurios ją paveldi
class Sensor:
    @abstractmethod
    def read(self, engine):
        pass

    def health_check(self):
        print("Generic sensor health check")


class TemperatureSensor(Sensor):
    def read(self, engine):
        return 70 + engine.get_rpm() * 0.01
    
    def health_check(self):
        print("TemperatureSensor OK")


class RPMSensor(Sensor):
    def read(self, engine):
        return engine.get_rpm()
    
    def health_check(self):
        print("RPMSensor OK")


class ThrottleSensor(Sensor):
    def read(self, engine):
        return engine.get_throttle()
    
    def health_check(self):
        print("ThrottleSensor OK")


# Įrenginių tėvinė klasė ir klasės, kurios ją paveldi
class Device:
    def activate(self, value):
        pass
    
    def health_check(self):
        print("Generic device health check")


class CoolingFan(Device):
    def __init__(self):
        self._speed = "OFF"

    def activate(self, value):
        self._speed = value

    def get_speed(self):
        return self._speed
    
    def health_check(self):
        print("CoolingFan OK")


# Strategy pattern strategijos apskaičiuoti kuro vartojimui
class FuelStrategy(ABC):
    @abstractmethod
    def calculate(self, rpm, throttle):
        pass


class EcoFuelStrategy(FuelStrategy):
    def calculate(self, rpm, throttle):
        if throttle == 0:
            return 0.05

        return 0.05 + rpm * 0.00003


class SportFuelStrategy(FuelStrategy):
    def calculate(self, rpm, throttle):
        if throttle == 0:
            return 0.15

        return 0.15 + rpm * 0.00008


class DieselFuelStrategy(FuelStrategy):
    def calculate(self, rpm, throttle):
        if throttle == 0:
            return 0.08

        return 0.08 + rpm * 0.00004


# Elektroninės valdymo sistemos klasė
class ECU:
    def __init__(self, engine, fuel_strategy):
        self._engine = engine
        self._fuel_strategy = fuel_strategy
        self._temp_sensor = TemperatureSensor()
        self._fan = CoolingFan()
        self._rpm_sensor = RPMSensor()
        self._throttle_sensor = ThrottleSensor()
        self._overheat_time = 0
        self._overheat_limit = 5000
        self._is_overheating = False
        self.run_diagnostics()

    def update(self):
        rpm = self._rpm_sensor.read(self._engine)
        throttle = self._throttle_sensor.read(self._engine)

        temperature = self._temp_sensor.read(self._engine)
        self._engine.set_temperature(temperature)

        self.check_overheating(temperature)

        fuel_amount = self._fuel_strategy.calculate(rpm, throttle)
        self._engine.set_fuel_injection(fuel_amount)

        self.control_fan(temperature)

        self._engine.update()

    def check_overheating(self, temperature):
        dt = SIMULATION_SPEED_MS
        if temperature >= self._engine._max_temp:
            self._overheat_time += dt

            if self._overheat_time >= self._overheat_limit and not self._is_overheating:
                print("ENGINE OVERHEATING!")
                self._is_overheating = True
        else:
            self._overheat_time = 0.0
            self._is_overheating = False

    def control_fan(self, temperature):
        if temperature > 95:
            self._fan.activate("HIGH")
        elif temperature > 75:
            self._fan.activate("LOW")
        else:
            self._fan.activate("OFF")

    def run_diagnostics(self):
        self._temp_sensor.health_check()
        self._rpm_sensor.health_check()
        self._throttle_sensor.health_check()
        self._fan.health_check()

    def set_throttle(self, value):
        self._engine.set_throttle(value)

    def get_engine(self):
        return self._engine

    def get_fan_speed(self):
        return self._fan.get_speed()


# Variklio parametrų saugojimo ir skaitymo funkcijos
def save_engine_parameters(max_rpm, idle_rpm, max_temp, rpm_increase_rate):
    with open(CONFIG_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["max_rpm", "idle_rpm", "max_temp", "rpm_increase_rate"])
        writer.writerow([max_rpm, idle_rpm, max_temp, rpm_increase_rate])

    print("Engine parameters saved to CSV.")


def load_engine_parameters():
    if not os.path.exists(CONFIG_FILE):
        print("No saved CSV file found.")
        return None

    with open(CONFIG_FILE, "r") as file:
        reader = csv.DictReader(file)
        row = next(reader)

        return (
            int(row["max_rpm"]),
            int(row["idle_rpm"]),
            float(row["max_temp"]),
            float(row["rpm_increase_rate"])
        )


# Funkcijos variklio duomenų ivedimui terminale
def ask_fuel_strategy():
    print("\nChoose fuel calculation strategy:")
    print("1 - Eco")
    print("2 - Sport")
    print("3 - Diesel")

    choice = input("Choose option [1]: ").strip()

    if choice == "2":
        return SportFuelStrategy()
    elif choice == "3":
        return DieselFuelStrategy()
    else:
        return EcoFuelStrategy()


def ask_engine_parameters():
    print("1 - Enter new engine parameters")
    print("2 - Load engine parameters from CSV")

    choice = input("Choose option [1]: ").strip()

    if choice == "2":
        loaded = load_engine_parameters()

        if loaded is not None:
            print("Engine parameters loaded from CSV.")
            return loaded

        print("Using manual input instead.\n")

    print("Enter engine parameters. Press Enter to use default value.\n")

    def ask_number(name, default, number_type=float):
        value = input(f"{name} [{default}]: ")

        if value.strip() == "":
            return default

        return number_type(value)

    max_rpm = ask_number("Max RPM", 7000, int)
    idle_rpm = ask_number("Idle RPM", 800, int)
    max_temp = ask_number("Max temperature", 120, float)
    rpm_increase_rate = ask_number("RPM increase rate", 0.08, float)

    save_choice = input("Save these parameters to CSV? [y/N]: ").strip().lower()

    if save_choice == "y":
        save_engine_parameters(max_rpm, idle_rpm, max_temp, rpm_increase_rate)

    return max_rpm, idle_rpm, max_temp, rpm_increase_rate


# Programos inicializavimas
if __name__ == "__main__":
    root = tk.Tk()
    root.title("ECU Simulator")
    root.geometry("400x350")

    max_rpm, idle_rpm, max_temp, rpm_increase_rate = ask_engine_parameters()
    fuel_strategy = ask_fuel_strategy()

    engine = Engine(
        max_rpm=max_rpm,
        idle_rpm=idle_rpm,
        max_temp=max_temp,
        rpm_increase_rate=rpm_increase_rate
    )

    ecu = ECU(engine, fuel_strategy)
    app = App(root, ecu)

    root.mainloop()