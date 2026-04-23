import tkinter as tk

#Pagrindinė aplikacijos klasė
class App:
    def __init__(self, root):
        self.engine = Engine()

        self.label = tk.Label(root, text=f"RPM: {self.engine.rpm}", font=("Arial", 16))
        self.label.pack(pady=20)

        root.bind("<Up>", self.increase)
        root.bind("<Down>", self.decrease)

    def update_display(self):
        self.label.config(text=f"RPM: {self.engine.rpm}")

    def increase(self, event):
        self.engine.increase_rpm()
        self.update_display()

    def decrease(self, event):
        self.engine.decrease_rpm()
        self.update_display()

#Variklio klasė
class Engine:
    def __init__(self):
        self.rpm = 800

    def increase_rpm(self):
        self.rpm += 100

    def decrease_rpm(self):
        self.rpm = max(0, self.rpm - 100)

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
app = App(root)
root.mainloop()