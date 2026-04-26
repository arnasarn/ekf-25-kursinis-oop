import tkinter as tk
from abc import ABC, abstractmethod

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
    def __init__(self):
        # Konfigūracija
        self._max_rpm = 7000
        self._idle_rpm = 800
        self._max_temp = 120
        self._rpm_increase_rate = 0.08

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


class TemperatureSensor(Sensor):
    def read(self, engine):
        return 70 + engine.get_rpm() * 0.01


# Įrenginių tėvinė klasė ir klasės, kurios ją paveldi
class Device:
    def activate(self, value):
        raise NotImplementedError


class CoolingFan(Device):
    def __init__(self):
        self._speed = "OFF"

    def activate(self, value):
        self._speed = value

    def get_speed(self):
        return self._speed


# Elektroninės valdymo sistemos klasė
class ECU:
    def __init__(self, engine):
        self._engine = engine
        self._temp_sensor = TemperatureSensor()
        self._fan = CoolingFan()
        self._overheat_time = 0
        self._overheat_limit = 5000
        self._is_overheating = False

    def update(self):
        rpm = self._engine.get_rpm()
        throttle = self._engine.get_throttle()

        temperature = self._temp_sensor.read(self._engine)
        self._engine.set_temperature(temperature)

        self.check_overheating(temperature)

        fuel_amount = self.calculate_fuel_injection(rpm, throttle)
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

    def calculate_fuel_injection(self, rpm, throttle):
        if throttle == 0:
            return 0.1

        return 0.1 + rpm * 0.00005

    def control_fan(self, temperature):
        if temperature > 95:
            self._fan.activate("HIGH")
        elif temperature > 75:
            self._fan.activate("LOW")
        else:
            self._fan.activate("OFF")

    def set_throttle(self, value):
        self._engine.set_throttle(value)

    def get_engine(self):
        return self._engine

    def get_fan_speed(self):
        return self._fan.get_speed()


# Programos inicializavimas
root = tk.Tk()
root.title("ECU Simulator")
root.geometry("400x350")

engine = Engine()
ecu = ECU(engine)
app = App(root, ecu)

root.mainloop()