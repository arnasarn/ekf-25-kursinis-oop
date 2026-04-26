# Automobilio variklio elektroninės valdymo sistemos simuliatorius

## Įvadas

Ši programa abstrakčiai įgyvendina automobilio variklio elektroninę valdymo sistemą ir simuliuoja šios sistemos veikimą, saugant duomenis kaip RPM, temperatūra, purškiamas degalų kiekis, degalų sanaudos ir t.t. Vartotojas paleidęs programą gali nustatyti variklio parametrus, pasirinkti ar nori juos saugoti .csv faile ar nuskaityti parametrus iš failo, tada mato grafinę sąsają, kurioje gali kelti ir mažinti variklio apsukas ir matyti kaip keičiasi variklio darbo parametrai.

### Naudojimas

Paleidus programą, vartotojas pirmiausia gali pasirinkti, ar nori įvesti naujus variklio parametrus, ar užkrauti juos iš anksčiau išsaugoto CSV failo. Taip pat vartotojas pasirenka degalų skaičiavimo strategiją, kuri gali būti „eco“, „sport“ arba „diesel“.

Toliau vartotojas įveda pagrindinius variklio parametrus, tokius kaip maksimalios apsukos (RPM), laisvos eigos apsukos, maksimali temperatūra ir apsukų didėjimo greitis. Jeigu vartotojas neįveda reikšmės ir paspaudžia Enter, naudojamos numatytosios reikšmės.

Atsidarius grafinei sąsajai, vartotojas gali valdyti variklį klaviatūros pagalba. Paspaudus „Arrow Up“ klavišą, įjungiamas gazas, todėl didėja variklio apsukos. Atleidus klavišą, gazas atjungiamas, o variklis grįžta link laisvos eigos režimo.

Programos lange realiu laiku pateikiama informacija apie variklio būseną. Rodomos dabartinės apsukos, temperatūra, droselio padėtis, ventiliatoriaus veikimo režimas bei bendras sunaudotų degalų kiekis. Tai leidžia vartotojui stebėti, kaip keičiasi variklio parametrai priklausomai nuo jo veiksmų ir pasirinktos strategijos.
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

### 1. Enkapsuliacija

Visos klasės apsaugo savo vidinius atributus. Visi kintamieji pažymėti `_`, tai reiškia kad už klasės ribų draudžiama pasiekti šiuos kintamuosius. Visos klasės turi metodus, skirtus suteikti priegą prie kintamųjų, pavyzdžiui, klasėje `Engine`:

```
def set_throttle(self, value):
   if value != 0 and value != 1:
      raise ValueError("Throttle can only be 0 or 1")

   self._throttle = value
```

Taip pat tikrinama, ar kvietėjas metodui paduoda teisinga reikšmę, t.y gazas gali būti arba įjungtas, arba neįjungtas (supaprastinas gazo pedalo veikimas, kadangi programa skirta valdyti klaviatūra).

### 2. Abstrakcija

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

### 3. Paveldėjimas

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

### 4. Polimorfizmas

Skirtingi jutikliai ir prietasai turi tokį patį metodą `health_check`, kuris veikia skirtingai, priklausomai nuo to kokiam objektui metodas priklauso. Šioje programoje tai panaudojama diagnostikos metode `ECU` klasėje, kuris išveda visų prietaisų būklę:

```
def run_diagnostics(self):
   self._temp_sensor.health_check()
   self._rpm_sensor.health_check()
   self._throttle_sensor.health_check()
   self._fan.health_check()
```

### Kompozicija ir agregacija

Klasėje `ECU` yra kompozicijos pavyzdys.

```
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
```

Kadangi jutiklių objektai sukuriami `ECU` klasės konstruktoriuje, šie egzistuoja tik tada, kai egzistuoja ECU objektas, o savaime neegzistuoja. Tai yra "is-a" ryšys.
Šioje klasėje taip pat yra agregacijos pavyzdys, nes `engine` objektas yra paduodamas per argumentus konstruktoriuje, o nesukuriamas jame. Tai yra "has-a"
Pagrindinėje programos klasėje `App` taip pat yra agregacijos pavyzdys, nes joje per argumentus paduodami ecu ir grafinės sąsajos root objektai.

```
class App:
    def __init__(self, root, ecu):
        self._root = root
        self._ecu = ecu
```

### Strategy dizaino šablonas

Programoje įgyvendintas Strategy dizaino šablonas. ECU klasė naudoja abstrakčią „FuelStrategy“ sąsają, o konkreti strategija parenkama programos paleidimo metu. Tai leidžia lengvai keisti degalų skaičiavimo logiką nekeičiant pačios ECU klasės.

```
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
```

### Duomenų saugojimas ir skaitymas

Duomenų išsaugojimui ir įkėlimui naudojamas CSV failas. Vartotojas gali išsaugoti įvestus parametrus ir vėliau juos užkrauti, taip išvengiant pakartotinio duomenų įvedimo. Tai padidina programos patogumą ir praktiškumą.

### Unit testai

Programoje taip pat buvo įgyvendinti vienetiniai testai, siekiant patikrinti pagrindinį sistemos funkcionalumą ir užtikrinti kodo teisingumą. Testavimui buvo naudojamas standartinis Python modulis `unittest`, kuris leidžia kurti automatinius testus atskiroms programos dalims.

Testai buvo skirti patikrinti svarbiausias sistemos komponentų savybes. Buvo tikrinama, ar variklis teisingai inicijuojamas su nustatytomis reikšmėmis, ar droselio reikšmės yra ribojamos tik leidžiamais intervalais, bei ar variklio apsukos didėja, kai paspaudžiamas gazas. Taip pat buvo tikrinama, ar degalų sunaudojimas didėja, kai vyksta variklio darbas.

Papildomai buvo testuojamos skirtingos degalų skaičiavimo strategijos. Buvo įsitikinta, kad „eco“ strategija sunaudoja mažiau degalų nei „sport“, o „diesel“ strategija grąžina logiškas reikšmes įvairiais darbo režimais. Tai padeda užtikrinti, kad Strategy dizaino šablonas veikia teisingai.

Taip pat buvo testuojamas ECU veikimas. Buvo tikrinama, ar ECU atnaujina variklio temperatūrą, ar teisingai valdo aušinimo ventiliatorių priklausomai nuo temperatūros, ir ar sistema reaguoja į skirtingas darbo sąlygas.

## Rezultatai ir apibendrinimas

Programos kūrimo metu kilo keletas iššūkių.

- Vienas iš pagrindinių sunkumų buvo teisingai paskirstyti atsakomybes tarp ECU ir variklio klasės, kad sistema būtų logiška ir lengvai prižiūrima.
- Kilo sunkumų sugalvoti, kaip reikšmingai panaudoti paveldėjimą ir abstrakciją.
- Nepavyko išsiaiškinti, kodėl kartais ECU nesiunčia pranešimo, kad variklis perkaista, nors pasiekta maksimali temperatūra ir perkaitimo laikas

Šio darbo metu buvo sukurtas veikiantis automobilio variklio ECU simuliatorius su grafine sąsaja. Programa leidžia vartotojui keisti variklio parametrus, stebėti jų pokyčius realiu laiku ir naudoti skirtingas degalų skaičiavimo strategijas. Darbo metu sėkmingai pritaikyti pagrindiniai objektinio programavimo principai ir dizaino šablonai, kurie pagerino kodo struktūrą ir lankstumą. Galutinis rezultatas yra aiškiai organizuota, funkcionali ir lengvai plečiama sistema.

Ateityje programą būtų galima išplėsti įgyvendinant sudėtingesnį temperatūros modelį, kuris apimtų šilumos kaupimą ir aušinimą. Taip pat būtų galima pridėti daugiau jutiklių, pavyzdžiui, oro srauto ar slėgio matavimą. Kitas galimas patobulinimas yra gedimų simuliacija, leidžianti modeliuoti jutiklių ar įrenginių gedimus. Be to, būtų naudinga pridėti grafikus, kurie realiu laiku atvaizduotų duomenų pokyčius. Grafinę sąsają taip pat būtų galima patobulinti pridedant daugiau valdymo elementų, tokių kaip mygtukai ar slankikliai. Galiausiai, galima įgyvendinti duomenų logavimą į failą, kad būtų galima analizuoti variklio darbą ilgesnį laiką.
