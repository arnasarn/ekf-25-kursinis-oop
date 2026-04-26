# Automobilio variklio elektroninės valdymo sistemos simuliatorius

## Įvadas

Ši programa abstrakčiai įgyvendina automobilio variklio elektroninę valdymo sistemą ir simuliuoja šios sistemos veikimą, saugant duomenis kaip RPM, temperatūra, purškiamas degalų kiekis, degalų sanaudos ir t.t. Vartotojas paleidęs programą gali nustatyti variklio parametrus, pasirinkti ar nori juos saugoti .csv faile ar nuskaityti parametrus iš failo, tada mato grafinę sąsają, kurioje gali kelti ir mažinti variklio apsukas ir matyti kaip keičiasi variklio darbo parametrai.

### Naudojimas

Programa iš pradžių paklaus vartotojo įvesti variklio duomenis, tada matys grafinę sąsają, kur gali kelti variklio apsukas su klavišu 'Arrow Up'.
Programa paleidžiama terminale įvedus komandą

```bash
python main.py
```

Unit testai paleidžiami komanda

```bash
python -m unittest test_ecu.py
```

## Analizė

### OOP principai

### 1 enkapsuliacija

Visos klasės apsaugo savo vidinius atributus. Visi kintamieji pažymėti `_`, tai reiškia kad už klasės ribų draudžiama pasiekti šiuos kintamuosius. Visos klasės turi metodus, skirtus suteikti priegą prie kintamųjų, pavyzdžiui, klasėje `Engine`:

```
def set_throttle(self, value):
   if value != 0 and value != 1:
      raise ValueError("Throttle can only be 0 or 1")

   self._throttle = value
```

Taip pat tikrinama, ar kvietėjas metodui paduoda teisinga reikšmę, t.y gazas gali būti arba įjungtas, arba neįjungtas (supaprastinas gazo pedalo veikimas, kadangi programa skirta valdyti klaviatūra).

### 2 abstrakcija

Tėvinės `Sensor` ir `Device` klasės yra abstračios klasės, kontraktas, kurį turi įgyvendinti šias klases paveldinčios klasės, šiuo atveju konkretūs prietaisai kaip `RPMSensor` ir `TemperatureSensor`

```
class Sensor:
    @abstractmethod
    def read(self, engine):
        pass

    def health_check(self):
        print("Generic sensor health check")
```

```
class Device:
    @abstractmethod
    def activate(self, value):
        pass

    def health_check(self):
        print("Generic device health check")
```

### 3 paveldėjimas

Kelios klasės paveldi bazines klases. Tai leidžia išplėsti funkcionalumą nekeičiant esamo kodo.

```
class CoolingFan(Device):
    def __init__(self):
        self._speed = "OFF"

    def activate(self, value):
        self._speed = value

    def get_speed(self):
        return self._speed

    def health_check(self):
        print("CoolingFan OK")
```

### 4 polimorfizmas

Skirtingi jutikliai ir prietasai turi tokį patį metodą `health_check`, kuris veikia skirtingai, priklausomai nuo to kokiam objektui metodas priklauso. Šioje programoje tai panaudojama diagnostikos metode `ECU` klasėje, kuris išveda visų prietaisų būklę:

```
def run_diagnostics(self):
   self._temp_sensor.health_check()
   self._rpm_sensor.health_check()
   self._throttle_sensor.health_check()
   self._fan.health_check()
```

1. Introduction
   a. What is your application?
   b. How to run the program?
   c. How to use the program?
2. Body/Analysis
   a. Explain how the program covers
   (implements) functional requirements (4 oop pillars, composition and aggregation, loading from file, design pattern)
3. Results and Summary
   a. 3-5 sentences (separate bullet points) about the
   results, which can include challenges faced during
   the implementation.

   b. Short summary of the key findings and outcomes of
   the coursework. What has this work achieved?
   What is the result of your work (program)?
   What are the future prospects of your program?
   c. How it would be possible to extend
   your application?
