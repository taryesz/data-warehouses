import pandas as pd
import random
import os

from datetime import datetime
from config import Config

class FleetDataGenerator(Config):

    def __init__(self):
        super().__init__()
        self.fleet_data = []
    
    def generate_fleet_data(self, trams_count, snapshot='T1'):
        """Generuje dane floty tramwajowej"""

        # Dla snapszotu T2 sprawdzamy czy istnieje plik T1
        if snapshot == 'T2':

            t1_filename = 'flota_tramwajowa_T1.csv'
            
            if os.path.exists(t1_filename):
                print(f"Znaleziono plik {t1_filename}, tworzenie T2 na podstawie T1...")
                self.generate_t2_from_t1(t1_filename)
                return
        
        start_id = 1

        if self.fleet_data:
            start_id = max(tram['Numer_Boczny'] for tram in self.fleet_data) + 1
        
        for i in range(start_id, start_id + trams_count):
            self.fleet_data.append({
                'Numer_Boczny': i,  # Używamy poprawnego, kolejnego 'i'
                'Marka': random.choice(self.TRAM_BRANDS),
                'Model': random.choice(self.TRAM_MODELS),
                'Rok_Produkcji': random.randint(1990, 2023),
                'Czy_Niskopodlogowy': random.choice([True, False]),
                'Wymiary': f"{random.randint(15, 30)}x{random.randint(2, 3)}x{random.randint(3, 4)}",
                'Czy_Dwukierunkowy': random.choice([True, False]),
                'Liczba_Wagonow': random.randint(1, 5),
                'Prędkość_Maksymalna': round(random.uniform(60, 80), 1),
                'Pasażerowie_Stojący': random.randint(80, 150),
                'Pasażerowie_Siedzący': random.randint(30, 60),
                'Czy_Sprawny': random.random() > 0.1  # 90% sprawnych
            })
    
        print(f"Wygenerowano {trams_count} nowych tramwajow")

    def generate_t2_from_t1(self, t1_filename):
        """Generuje dane T2 na podstawie istniejacego pliku T1"""

        try:

            t1_df = pd.read_csv(t1_filename)

            # Modyfikujemy istniejace tramwaje z T1
            for index, row in t1_df.iterrows():

                tram_data = row.to_dict()
                
                # 5 pierwszych tramwajow zmienia status na "niesprawny"
                if index < 5:  
                    tram_data['Czy_Sprawny'] = False
                
                self.fleet_data.append(tram_data)
            
            print(f"Zmodyfikowano pierwszych 5 istniejacych tramwajow z T1")

            # Dodajemy NOWE tramwaje
            self.generate_fleet_data(trams_count=self.T2_TRAMS_COUNT)

        except Exception as e:
            print(f"Blad podczas wczytywania pliku {t1_filename}: {e}")
            exit(1)

    def save_to_csv(self, snapshot='T1'):
        """Zapisuje dane floty do CSV"""

        filename = f'flota_tramwajowa_{snapshot}.csv'

        pd.DataFrame(self.fleet_data).to_csv(filename, index=False)
        print(f"Zapisano {len(self.fleet_data)} tramwajow do {filename}")
    
    def save_to_bulk(self, snapshot='T1'):
        """Zapisuje dane floty tramwajowej do BULK"""
    
        filename = f'tramwaje_{snapshot}.bulk'
        
        with open(filename, 'w', encoding='utf-8') as f:
       
            for tram in self.fleet_data:
                line = (
                    f"{tram['Numer_Boczny']}|"
                    f"{tram['Marka']}|"
                    f"{tram['Model']}|\n"
                )
                f.write(line)
        
        print(f"Zapisano {len(self.fleet_data)} tramwajow do {filename}")

    def generate_all(self, snapshot="T1"):
        """Generuje dane floty"""

        print("\n\n>>> GENEROWANIE DANYCH FLOTY <<<")
        
        print(f"Generowanie snapszotu {snapshot}...")

        self.fleet_data = [] 

        trams_count = self.TRAMS_COUNT if snapshot == "T1" else self.T2_TRAMS_COUNT

        self.generate_fleet_data(trams_count, snapshot)
        self.save_to_csv(snapshot)
        self.save_to_bulk(snapshot)
        
        print("Generowanie danych floty zakonczone.")
