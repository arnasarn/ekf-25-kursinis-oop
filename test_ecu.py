import unittest

from main import (
    Engine,
    ECU,
    EcoFuelStrategy,
    SportFuelStrategy,
    DieselFuelStrategy,
)


class TestEngine(unittest.TestCase):

    def test_engine_starts_at_idle_rpm(self):
        engine = Engine(idle_rpm=900)

        self.assertEqual(engine.get_rpm(), 900)

    def test_throttle_can_only_be_0_or_1(self):
        engine = Engine()

        engine.set_throttle(1)
        self.assertEqual(engine.get_throttle(), 1)

        with self.assertRaises(ValueError):
            engine.set_throttle(2)

    def test_rpm_increases_when_throttle_on(self):
        engine = Engine(max_rpm=7000, idle_rpm=800, rpm_increase_rate=0.1)

        engine.set_throttle(1)
        engine.update()

        self.assertGreater(engine.get_rpm(), 800)

    def test_fuel_used_increases(self):
        engine = Engine()

        engine.set_fuel_injection(0.2)
        engine.update()

        self.assertGreater(engine.get_fuel_used(), 0)


class TestFuelStrategies(unittest.TestCase):

    def test_eco_strategy_uses_less_fuel_than_sport(self):
        rpm = 3000
        throttle = 1

        eco = EcoFuelStrategy()
        sport = SportFuelStrategy()

        self.assertLess(
            eco.calculate(rpm, throttle),
            sport.calculate(rpm, throttle)
        )

    def test_diesel_strategy_calculates_fuel(self):
        diesel = DieselFuelStrategy()

        fuel = diesel.calculate(3000, 1)

        self.assertGreater(fuel, 0)

    def test_idle_fuel_is_lower_in_eco_than_sport(self):
        eco = EcoFuelStrategy()
        sport = SportFuelStrategy()

        self.assertLess(
            eco.calculate(1000, 0),
            sport.calculate(1000, 0)
        )


class TestECU(unittest.TestCase):

    def test_ecu_sets_engine_temperature(self):
        engine = Engine()
        ecu = ECU(engine, EcoFuelStrategy())

        ecu.update()

        self.assertGreater(engine.get_temperature(), 0)

    def test_fan_turns_off_when_cold(self):
        engine = Engine()
        ecu = ECU(engine, EcoFuelStrategy())

        ecu.control_fan(50)

        self.assertEqual(ecu.get_fan_speed(), "OFF")

    def test_fan_turns_low_when_warm(self):
        engine = Engine()
        ecu = ECU(engine, EcoFuelStrategy())

        ecu.control_fan(80)

        self.assertEqual(ecu.get_fan_speed(), "LOW")

    def test_fan_turns_high_when_hot(self):
        engine = Engine()
        ecu = ECU(engine, EcoFuelStrategy())

        ecu.control_fan(100)

        self.assertEqual(ecu.get_fan_speed(), "HIGH")


if __name__ == "__main__":
    unittest.main()