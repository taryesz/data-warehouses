import pandas as pd
import random
from datetime import datetime
from config import Config

class FleetDataGenerator(Config):

    def __init__(self):
        super().__init__()
        self.fleet_data = []
    
    def generate_fleet_data(self, snapshot='T1'):
        """Generuje dane floty tramwajowej"""

        for i in range(1, self.TRAM_COUNT + 1):

            production_year = random.randint(1990, 2023)
            
            # W T2 niektore tramwaje zmieniaja status sprawnosci
            if snapshot == 'T2' and i <= 5:  # 5 tramwajow zmienia status
                is_operational = False
            else:
                is_operational = random.random() > 0.1  # 90% sprawnych
            
            self.fleet_data.append({
                'Numer_Boczny': i,
                'Marka': random.choice(self.TRAM_BRANDS),
                'Model': random.choice(self.TRAM_MODELS),
                'Rok_Produkcji': production_year,
                'Czy_Niskopodlogowy': random.choice([True, False]),
                'Wymiary': f"{random.randint(15, 30)}x{random.randint(2, 3)}x{random.randint(3, 4)}",
                'Czy_Dwukierunkowy': random.choice([True, False]),
                'Liczba_Wagonow': random.randint(1, 5),
                'Prędkość_Maksymalna': round(random.uniform(60, 80), 1),
                'Pasażerowie_Stojący': random.randint(80, 150),
                'Pasażerowie_Siedzący': random.randint(30, 60),
                'Czy_Sprawny': is_operational
            })
    
    def save_to_csv(self, snapshot='T1'):
        """Zapisuje dane floty do CSV"""

        filename = f'flota_tramwajowa_{snapshot}.csv'

        pd.DataFrame(self.fleet_data).to_csv(filename, index=False)
        print(f"Zapisano {len(self.fleet_data)} tramwajow do {filename}")
    
    def generate_all(self):
        """Generuje dane floty dla obu snapszotow"""

        print(">>> GENEROWANIE DANYCH FLOTY <<<")
        
        print("Generowanie snapszotu T1...")

        self.generate_fleet_data('T1')
        self.save_to_csv('T1')
        
        self.fleet_data = []    # Czyscimy dane przed generowaniem T2
        
        print("Generowanie snapszotu T2...")

        self.generate_fleet_data('T2')
        self.save_to_csv('T2')
        
        print("Generowanie danych floty zakonczone.")
