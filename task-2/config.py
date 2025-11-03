import random
from datetime import datetime, timedelta

class Config:
    
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
        'Zajezdnia', 'Lotnisko',
        'Stadion Miejski', 
        'Teatr Wielki', 
        'Muzeum Narodowe',
        'Park Miejski', 
        'Biblioteka'
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
        'Serwisant', 
        'Dyspozytor', 
        'Konserwator', 
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
    TRAM_COUNT = 50
    EVENTS_COUNT = 1000

    STOPS_COUNT = 15
    LINES_COUNT = 12
    # COURSE_COUNT_T1 = 50000   # 50k dla T1
    # COURSE_COUNT_T2 = 100000  # 100k dla T2 (T1 + 50k nowych)
    
    # Daty snapszotow
    DATE_T1 = datetime(2024, 1, 1)
    DATE_T2 = datetime(2024, 2, 1)
    
    def random_date(self, start_date, end_date):
        """Generuje losowa date w podanym zakresie"""
        delta = end_date - start_date
        random_days = random.randint(0, delta.days)
        random_seconds = random.randint(0, 86400)
        return start_date + timedelta(days=random_days, seconds=random_seconds)
    