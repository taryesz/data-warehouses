import random
from datetime import datetime, timedelta

class Config:
    
    def random_date(self, start_date, end_date):
        """Generuje losowa date w podanym zakresie"""

        delta = end_date - start_date
        random_days = random.randint(0, delta.days)
        random_seconds = random.randint(0, 86400)
        return start_date + timedelta(days=random_days, seconds=random_seconds)
    
    # Podstawowe dane
    TRAM_BRANDS = ['Pesa', 'Modertrans', 'Solaris', 'Newag']
    TRAM_MODELS = ['SwING', '2016N', '128N', '123N']
    
    STOPS = [
        'Dworzec Główny', 
        'Plac Wolności', 
        'Ratusz', 
        'Stare Miasto', 
        'Dworzec PKS',
        'Szpital Miejski', 
        'Uniwersytet', 
        'Galeria Handlowa', 
        'Zajezdnia', 
        'Lotnisko',
        'Stadion Miejski', 
        'Teatr Wielki', 
        'Muzeum Narodowe',
        'Park Miejski', 
        'Biblioteka',
        'Nowe Ogrody',
        'Plac Konstytucji',
        'Cmentarz Komunalny',
        'Osiedle Leśne',
        'Most Północny',
        'Targowisko',
        'Fabryka',
        'Dworzec Zachodni',
        'Kamienice',
        'Plac Słowiański',
        'Osiedle Południe',
        'Szkoła Techniczna',
        'Rondo Solidarności',
        'Rektorat',
        'Port Miejski',
        'Nowy Rynek',
        'Plac Grunwaldzki',
        'Osiedle Kolejowe',
        'Aleja Lipowa',
        'Dworzec Wschodni',
        'Szpital Wojewódzki',
        'Park Technologiczny',
        'Kampus Zachodni',
        'Osiedle Kwiatowe',
        'Plac Targowy',
        'Hala Widowiskowa',
        'Most Południowy',
        'Zamek',
        'Osiedle Energetyków',
        'Plac Niepodległości'
    ]
    
    LINES = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    
    EVENT_TYPES = [
        'Awaria techniczna', 
        'Przegląd okresowy', 
        'Czyszczenie', 
        'Naprawa awaryjna',
        'Wycofanie z ruchu', 
        'Incydent z pasażerem', 
        'Wypadek', 
        'Utrudnienie w ruchu'
    ]
    
    JOB_TITLES = [
        'Kierowca', 
        'Mechanik', 
        'Kierownik'
    ]
    
    EDUCATION = [
        "Podstawowe",
        "Zasadnicze zawodowe",
        "Średnie ogólne",
        "Średnie techniczne",
        "Policealne / pomaturalne",
        "Wyższe (licencjat / inżynier)",
        "Wyższe (magister)",
        "Podyplomowe",
    ]
    
    # Ustawienia generatora
    EMPLOYEES_COUNT = 200
    T2_EMPLOYEES_COUNT = 50

    TRAMS_COUNT = 120
    T2_TRAMS_COUNT = 25

    EVENTS_COUNT = 1000
    T2_EVENTS_COUNT = 250

    EVENT_TRACKING_START = datetime(2020, 1, 1)

    STOPS_COUNT = len(STOPS)
    LINES_COUNT = len(LINES)

    COURSES_COUNT = 10000   # 1mln 
    T2_COURSES_COUNT = 1000
    