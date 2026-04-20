import tkinter as tk

class Sensor:
    def read(self):
        raise NotImplementedError


class TemperatureSensor(Sensor):
    def read(self):
        return 90  # example value


class Actuator:
    def activate(self, value):
        raise NotImplementedError


class CoolingFan(Actuator):
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

class Engine:
    def __init__(self):
        self.rpm = 800

    def increase_rpm(self):
        self.rpm += 100

    def decrease_rpm(self):
        self.rpm = max(0, self.rpm - 100)


class App:
    def __init__(self, root):
        self.engine = Engine()

        self.label = tk.Label(root, text=f"RPM: {self.engine.rpm}")
        self.label.pack()

        tk.Button(root, text="Increase RPM", command=self.increase).pack()
        tk.Button(root, text="Decrease RPM", command=self.decrease).pack()

    def update_display(self):
        self.label.config(text=f"RPM: {self.engine.rpm}")

    def increase(self):
        self.engine.increase_rpm()
        self.update_display()

    def decrease(self):
        self.engine.decrease_rpm()
        self.update_display()


root = tk.Tk()
root.title("ECU Simulator")
app = App(root)
root.mainloop()

ecu = ECU()

for _ in range(5):
    ecu.update()