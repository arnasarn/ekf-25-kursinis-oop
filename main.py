import tkinter as tk

#Pagrindinė aplikacijos klasė
class App:
    def __init__(self, root, ecu):
        self._root = root
        self._ecu = ecu
        self._rpm_label = tk.Label(root, font=("Arial", 16))
        self._rpm_label.pack(pady=20)

        self._throttle_label = tk.Label(root, font=("Arial", 16))
        self._throttle_label.pack(pady=20)

        self._temp_label = tk.Label(root, font=("Arial", 16))
        self._temp_label.pack(pady=20)


        root.bind("<KeyPress-Up>", self.throttle_on)
        root.bind("<KeyRelease-Up>", self.throttle_off)

        self.update_loop()

    def update_display(self):
        engine = self._ecu.get_engine()

        self._rpm_label.config(text=f"RPM: {engine.get_rpm()}")
        self._throttle_label.config(text=f"Throttle: {engine.get_throttle()}")
        self._temp_label.config(text=f"Temperature: {engine.get_temperature():.1f}")

    def increase(self, event):
        self.engine.increase_rpm()

    def throttle_on(self, event):
        self._ecu.set_throttle(1)

    def throttle_off(self, event):
        self._ecu.set_throttle(0)

    def update_loop(self):
        self._ecu.update()
        self.update_display()
        self._root.after(50, self.update_loop)


#Variklio klasė
class Engine:
    def __init__(self):
        # Konfigūracija
        self._max_rpm = 7000
        self._idle_rpm = 800
        self._max_temp = 120
        
        # Būsena
        self._rpm = self._idle_rpm
        self._temperature = 70
        self._throttle = 0
        self._fuel_used = 0.0

    def set_throttle(self, value):
        if (value != 0 and value != 1):
            raise ValueError("Throttle can only be numbers 0 or 1")

        self._throttle = value

    def set_temperature(self, value):
        self._temperature = min(value, self._max_temp)

    def update(self):
        if self._throttle == 1:
            self._rpm += 100
            if self._rpm > self._max_rpm:
                self._rpm = self._max_rpm
        else:
            if self._rpm > self._idle_rpm:
                self._rpm -= 100

    def get_rpm(self):
        return self._rpm

    def get_throttle(self):
        return self._throttle

    def get_temperature(self):
        return self._temperature


#Tėvinė jutiklio klasė ir klasės, kurios ją paveldi
class Sensor:
    def read(self):
        raise NotImplementedError


class TemperatureSensor(Sensor):
    def read(self, engine):
        return 50 + engine.get_rpm() * 0.01


#Įrenginių tėvinė klasė ir klasės, kurios ją paveldi
class Device:
    def activate(self, value):
        raise NotImplementedError

class CoolingFan(Device):
    def activate(self, value):
        print(f"Fan speed set to {value}")


class ECU:
    def __init__(self, engine):
        self._engine = engine
        self._temp_sensor = TemperatureSensor()
        self._fan = CoolingFan()

    def update(self):
        rpm = self._engine.get_rpm()
        throttle = self._engine.get_throttle()

        temperature = self._temp_sensor.read(self._engine)
        self._engine.set_temperature(temperature)

        self._engine.update()

    def set_throttle(self, value):
        self._engine.set_throttle(value)

    def get_engine(self):
        return self._engine



#Programos inicializavimas
root = tk.Tk()
root.title("ECU Simulator")
root.geometry("400x300")
engine = Engine()
ecu = ECU(engine)
app = App(root, ecu)
root.mainloop()