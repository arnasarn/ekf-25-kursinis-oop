import tkinter as tk

#Pagrindinė aplikacijos klasė
class App:
    def __init__(self, root):
        self._engine = Engine(ECU())
        self._rpm_label = tk.Label(root, text=f"RPM: {self._engine._rpm}", font=("Arial", 16))
        self._rpm_label.pack(pady=20)

        self._throttle_label = tk.Label(root, text=f"Throttle: {self._engine._throttle}", font=("Arial", 16))
        self._throttle_label.pack(pady=20)


        root.bind("<KeyPress-Up>", self.throttle_on)
        root.bind("<KeyRelease-Up>", self.throttle_off)

    def update_display(self):
        self._rpm_label.config(text=f"RPM: {self._engine._rpm}")
        self._throttle_label.config(text=f"Throttle: {self._engine._throttle}")

    def increase(self, event):
        self.engine.increase_rpm()
        self.update_display()

    def throttle_on(self, event):
        self._engine.set_throttle(1)
        self.update_display()

    def throttle_off(self, event):
        self._engine.set_throttle(0)
        self.update_display()


#Variklio klasė
class Engine:
    def __init__(self, ecu):
        # Konfigūracija
        self._max_rpm = 7000
        self._idle_rpm = 800
        self._max_temp = 120
        self._ecu = ecu
        
        # Būsena
        self._rpm = self._idle_rpm
        self._temperature = 70
        self._throttle = 0
        self._fuel_used = 0.0

    def set_throttle(self, value):
        if (value != 0 and value != 1):
            raise ValueError("Throttle can only be numbers 0 or 1")

        self._throttle = value


#Tėvinė jutiklio klasė ir klasės, kurios ją paveldi
class Sensor:
    def read(self):
        raise NotImplementedError


class TemperatureSensor(Sensor):
    def read(self):
        return 90  # example value


#Įrenginių tėvinė klasė ir klasės, kurios ją paveldi
class Device:
    def activate(self, value):
        raise NotImplementedError

class CoolingFan(Device):
    def activate(self, value):
        print(f"Fan speed set to {value}")


class ECU:
    def __init__(self):
        self.temp_sensor = TemperatureSensor()
        self.fan = CoolingFan()

    def update(self):
        temp = self.temp_sensor.read()

        if temp > 95:
            self.fan.activate("HIGH")
        else:
            self.fan.activate("LOW")


#Programos inicializavimas
root = tk.Tk()
root.title("ECU Simulator")
root.geometry("400x300")
ecu = ECU()
engine = Engine(ecu)
app = App(root)
root.mainloop()