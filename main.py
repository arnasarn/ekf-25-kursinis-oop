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