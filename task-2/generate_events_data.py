import pandas as pd
import random
import os
from datetime import timedelta
from config import Config

class EventsDataGenerator(Config):

    def __init__(self):
        super().__init__()
        self.events_data = []
        self.drivers = []
        self.fleet = []
    
    def load_existing_data(self, snapshot='T1'):
        """Wczytuje istniejace dane z plikow CSV"""
        
        # Wczytujemy dane pracownikow - tylko kierowcow
        employees_file = f'pracownicy_{snapshot}.csv'

        try:
            employees_df = pd.read_csv(employees_file)
            drivers_df = employees_df[employees_df['Stanowisko'] == 'Kierowca']
            self.drivers = [f"{row['Imię']} {row['Nazwisko']}" for _, row in drivers_df.iterrows()]
            print(f"Wczytano {len(self.drivers)} kierowcow z {employees_file}")
        except FileNotFoundError:
            print(f"Nie znaleziono pliku {employees_file}")
            exit(1)

        # Wczytujemy dane floty tramwajowej
        fleet_file = f'flota_tramwajowa_{snapshot}.csv'

        try:
            fleet_df = pd.read_csv(fleet_file)
            self.tram_models = {row['Numer_Boczny']: f"{row['Marka']} {row['Model']}" for _, row in fleet_df.iterrows()}
            print(f"Wczytano {len(self.tram_models)} tramwajow z {fleet_file}")
        except FileNotFoundError:
            print(f"Nie znaleziono pliku {fleet_file}")
            exit(1)

    def generate_events(self, snapshot='T1'):
        """Generuje dane zdarzen dla arkusza Excel z podzialem na miesiace"""

        # Dla snapszotu T2 sprawdzamy czy istnieje plik T1
        if snapshot == 'T2':
            t1_filename = 'zdarzenia_T1.xlsx'
            if os.path.exists(t1_filename):
                print(f"Znaleziono plik {t1_filename}, tworzenie T2 na podstawie T1...")
                self.generate_t2_from_t1(t1_filename)
                return
        
        # Wczytujemy istniejace dane
        self.load_existing_data(snapshot)
        
        # Rozszerzony zakres dat - caly rok
        start_date = self.EVENT_TRACKING_START
        end_date = self.EVENT_TRACKING_START + timedelta(days=365)
        
        # Slownik do przechowywania zdarzen pogrupowanych wedlug miesiecy
        events_by_month = {}
        
        for i in range(1, self.EVENTS_COUNT + 1):
            
            # Losowy tramwaj
            tram_id = random.randint(1, len(self.tram_models))
            
            # Pobieramy model tramwaju na podstawie ID z pliku CSV
            tram_model = self.tram_models.get(tram_id, "Nieznany model")
            
            # Losowa data
            event_date = self.random_date(start_date, end_date)
            
            # Klucz dla miesiaca (YYYY-MM)
            month_key = event_date.strftime('%Y-%m')
            
            # Inicjalizujemy liste dla danego miesiaca jesli nie istnieje
            if month_key not in events_by_month:
                events_by_month[month_key] = []
            
            # Dodajemy zdarzenie do odpowiedniego miesiaca
            events_by_month[month_key].append({
                'ID_Wpisu': i,
                'Typ_Zdarzenia': random.choice(self.EVENT_TYPES),
                'Data': event_date,
                'ID_Zajezdni': random.randint(1, 3),
                'ID_Tramwaju': tram_id,
                'Model_Tramwaju': tram_model,
                'Linia': random.randint(1, self.LINES_COUNT),
                'Kurs': f"K{random.randint(1000, 9999)}",
                'Opis': "Lorem ipsum dolor sit amet.",
                'Osoba_Zgłaszająca': random.choice(self.drivers) if self.drivers else "Nieznany kierowca",
                'Wykonawca': f"Serwis o NIPie {random.randint(1000000000, 9999999999)}",
                'Koszt': round(random.uniform(0, 10000), 2)
            })
        
        # Konwertacja slownika na liste wszystkich zdarzen
        self.events_data = []
        for month_events in events_by_month.values():
            self.events_data.extend(month_events)
        
        # Zapisujemy pogrupowane dane
        self.events_by_month = events_by_month
    
    def generate_t2_from_t1(self, t1_filename):
        """Generuje dane T2 na podstawie istniejacego pliku T1 z podzialem na miesiace"""

        try:

            # Wczytujemy dane z T1 (wszystkie arkusze)
            xls = pd.ExcelFile(t1_filename)
            all_t1_events = []
            
            # Przechodzimy przez wszystkie arkusze i zbieramy dane
            for sheet_name in xls.sheet_names:
                if sheet_name.startswith('Zdarzenia_'):
                    df = pd.read_excel(t1_filename, sheet_name=sheet_name)
                    all_t1_events.extend(df.to_dict('records'))
            
            # Ostatni na liscie ID wpisu
            max_t1_id = max(event['ID_Wpisu'] for event in all_t1_events)
            
            # Slownik do przechowywania zdarzen pogrupowanych wedlug miesiecy
            events_by_month = {}
            
            # Modyfikujemy istniejace zdarzenia z T1
            modified_count = 0
            for event_data in all_t1_events:

                # 15 pierwszych zdarzen zmienia koszt na 0
                if modified_count < 15:  
                    event_data['Koszt'] = 0.0
                    modified_count += 1
                
                # Grupujemy wedlug miesiaca
                event_date = pd.to_datetime(event_data['Data'])
                month_key = event_date.strftime('%Y-%m')
                
                if month_key not in events_by_month:
                    events_by_month[month_key] = []
                
                events_by_month[month_key].append(event_data)
            
            print(f"Zmodyfikowano {modified_count} istniejacych zdarzen z T1")

            # Wczytujemy dane dla T2 (nowi kierowcy i tramwaje)
            self.load_existing_data('T2')
            
            # Rozszerzony zakres dat - caly rok
            start_date_t2 = self.EVENT_TRACKING_START
            end_date_t2 = self.EVENT_TRACKING_START + timedelta(days=365)
            
            # Dodajemy NOWE zdarzenia
            new_event_id = max_t1_id + 1
            for i in range(self.T2_EVENTS_COUNT):
                event_date = self.random_date(start_date_t2, end_date_t2)
                month_key = event_date.strftime('%Y-%m')
                
                # Losowy tramwaj
                tram_id = random.randint(1, len(self.tram_models))
                tram_model = self.tram_models.get(tram_id, "Nieznany model")
                
                new_event = {
                    'ID_Wpisu': new_event_id,
                    'Typ_Zdarzenia': random.choice(self.EVENT_TYPES),
                    'Data': event_date,
                    'ID_Zajezdni': random.randint(1, 3),
                    'ID_Tramwaju': tram_id,
                    'Model_Tramwaju': tram_model,
                    'Linia': random.randint(1, self.LINES_COUNT),
                    'Kurs': f"K{random.randint(1000, 9999)}",
                    'Opis': "Lorem ipsum dolor sit amet.",
                    'Osoba_Zgłaszająca': random.choice(self.drivers) if self.drivers else "Nieznany kierowca",
                    'Wykonawca': f"Serwis o NIPie {random.randint(1000000000, 9999999999)}",
                    'Koszt': round(random.uniform(0, 10000), 2)
                }
                
                if month_key not in events_by_month:
                    events_by_month[month_key] = []
                
                events_by_month[month_key].append(new_event)
                new_event_id += 1
            
            # Konwertacja na plaska liste dla kompatybilnosci
            self.events_data = []
            for month_events in events_by_month.values():
                self.events_data.extend(month_events)
            
            self.events_by_month = events_by_month
            
            print(f"Dodano {self.T2_EVENTS_COUNT} nowych zdarzen")
            print(f"Razem w T2: {len(self.events_data)} zdarzen")

        except Exception as e:
            print(f"Blad podczas wczytywania pliku {t1_filename}: {e}")
            exit(1)
    
    def save_to_excel(self, snapshot='T1'):
        """Zapisuje dane do pliku Excel z osobnymi arkuszami dla kazdego miesiaca"""

        filename = f'zdarzenia_{snapshot}.xlsx'
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:

            # Jesli mamy dane pogrupowane wedlug miesiecy, zapisujemy je w osobnych arkuszach
            if hasattr(self, 'events_by_month') and self.events_by_month:
                for month_key, month_events in self.events_by_month.items():
                    
                    # Nowy arkusz
                    sheet_name = f"Zdarzenia_{month_key}"

                    # Krotsza nazwa jesli jest za dluga (Excel ma limit 31 znakww)
                    if len(sheet_name) > 31:
                        sheet_name = sheet_name[:31]
                    
                    df = pd.DataFrame(month_events)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"Zapisano {len(month_events)} zdarzen do arkusza '{sheet_name}'")
            else:
                # Dla kompatybilnosci - zapisujemy wszystkie dane w jednym arkuszu
                df = pd.DataFrame(self.events_data)
                df.to_excel(writer, sheet_name=f'Zdarzenia_{snapshot}', index=False)
                print(f"Zapisano {len(self.events_data)} zdarzen do arkusza 'Zdarzenia_{snapshot}'")
        
        print(f"Utworzono plik {filename}")
    
    def generate_all(self, snapshot="T1"):
        """Generuje dane zdarzen"""

        print(">>> GENEROWANIE DANYCH ZDARZEN <<<")
        
        print(f"Generowanie snapszotu {snapshot}...")

        self.events_data = []
        
        self.generate_events(snapshot)
        self.save_to_excel(snapshot)
        
        print("Generowanie danych zdarzen zakonczone.")
