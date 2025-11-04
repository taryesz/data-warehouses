import pandas as pd
import random
import os
from datetime import datetime
from config import Config
from mimesis import Person, Generic
from mimesis.locales import Locale
from mimesis.enums import Gender


class EmployeesDataGenerator(Config):

    def __init__(self):
        super().__init__()
        self.employees_data = []
        self.person = Person(locale=Locale.PL)
        self.generic = Generic(locale=Locale.PL)
    
    def generate_personal_data(self, employees_count):
        """Generuje dane pracownikow używajac Mimesis"""

        employees = []
        
        for i in range(1, employees_count + 1):

            # Plec
            gender = random.choice([Gender.MALE, Gender.FEMALE])
            
            # Imie
            first_name = self.person.first_name(gender=gender)

            # Drugie imie
            middle_name = self.person.first_name(gender=gender)

            # Nazwisko
            last_name = self.person.last_name(gender=gender)

            # Data urodzenia
            age = random.randint(24, 65)        # Generujemy wiek w latach
            current_year = datetime.now().year  # Obliczamy rok urodzenia
            birth_year = current_year - age
            birth_month = random.randint(1, 12) # Losowy dzien i miesiac
            birth_day = random.randint(1, 28)   # Bezpiecznie, zeby nie bylo problemow z lutym
            birth_date = datetime(birth_year, birth_month, birth_day)
            
            # PESEL
            pesel = self.person.identifier(mask='###########')
                    
            employees.append({
                'id': i,
                'first_name': first_name,
                'middle_name': middle_name,
                'last_name': last_name,
                'birth_date': birth_date,
                'gender': gender,
                'pesel': pesel,
            })
                
        return employees
    
    def generate_employees_data(self, employees_count, snapshot="T1"):
        """Generuje kompletne dane pracownikow"""

        # Dla snapszotu T2 sprawdzamy czy istnieje plik T1
        if snapshot == "T2":
        
            t1_filename = 'pracownicy_T1.csv'

            if os.path.exists(t1_filename):
                print(f"Znaleziono plik {t1_filename}, tworzenie T2 na podstawie T1...")
                self.generate_t2_from_t1(t1_filename)
                return
        
        employees = self.generate_personal_data(employees_count)
        
        start_id = 1
        if self.employees_data:
            start_id = max(emp['ID_Pracownika'] for emp in self.employees_data) + 1

        for i, employee in enumerate(employees, start=start_id):

            self.employees_data.append({
                'ID_Pracownika': i,
                'Imię': employee['first_name'],
                'Drugie_Imię': employee['middle_name'],
                'Nazwisko': employee['last_name'],
                'Data_Urodzenia': employee['birth_date'].strftime('%Y-%m-%d'),
                'Płeć': "M" if employee['gender'] == Gender.MALE else "K",
                'PESEL': employee['pesel'],
                'Data_Zatrudnienia': self.random_date(datetime(2010, 1, 1), datetime(2023, 12, 31)).strftime('%Y-%m-%d'),
                'Stanowisko': random.choice(self.JOB_TITLES),
                'Wykształcenie_Zawód': random.choice(self.EDUCATION),
            })
    
        print(f"Wygenerowano {employees_count} nowych pracownikow")

    def generate_t2_from_t1(self, t1_filename):
        """Generuje dane T2 na podstawie istniejacego pliku T1"""

        try:

            t1_df = pd.read_csv(t1_filename, dtype={'PESEL': str})

            # Modyfikujemy istniejacych pracownikow z T1
            for index, row in t1_df.iterrows():

                employee_data = row.to_dict()
                
                # 10 pierwszych pracownikow otrzymuje awans
                if index < 10:  
                    current_position = employee_data['Stanowisko']
                    if current_position != 'Kierownik':

                        # Awans na Kierownika lub Starszego [stanowisko]
                        if random.random() > 0.5:
                            employee_data['Stanowisko'] = 'Kierownik'
                        else:
                            employee_data['Stanowisko'] = f"Starszy {current_position}"
                
                self.employees_data.append(employee_data)
            
            print(f"Zmodyfikowano pierwszych 10 istniejacych pracownikow z T1")

            # Dodajemy NOWYCH pracownikow
            self.generate_employees_data(employees_count=self.T2_EMPLOYEES_COUNT)
            
        except Exception as e:
            print(f"Blad podczas wczytywania pliku {t1_filename}: {e}")
            exit(1)
    
    def save_to_csv(self, snapshot='T1'):
        """Zapisuje dane pracownikow do CSV"""

        filename = f'pracownicy_{snapshot}.csv'

        pd.DataFrame(self.employees_data).to_csv(filename, index=False, encoding='utf-8')
        print(f"Zapisano {len(self.employees_data)} pracownikow do {filename}")
       
    def save_to_bulk(self, snapshot='T1'):
        """Zapisuje dane pracownikow do BULK - TYLKO KIEROWCY"""
        
        filename = f'kierowcy_{snapshot}.bulk'
        
        # Tylko kierowcy
        drivers = [employee for employee in self.employees_data if employee['Stanowisko'] == 'Kierowca']
        
        with open(filename, 'w', encoding='utf-8') as f:
            
            for employee in drivers:
                line = (
                    f"{employee['ID_Pracownika']}|"
                    f"{employee['Imię']}|"
                    f"{employee['Nazwisko']}|\n"
                )
                f.write(line)
        
        print(f"Z czego {len(drivers)} pracownikow-kierowcow zapisano do {filename}")
    
    def generate_all(self, snapshot="T1"):
        """Generuje dane pracownikow"""

        print("\n\n>>> GENEROWANIE DANYCH PRACOWNIKOW <<<")
        
        print(f"Generowanie snapszotu {snapshot}...")

        self.employees_data = []
        
        employees_count = self.EMPLOYEES_COUNT if snapshot == "T1" else self.T2_EMPLOYEES_COUNT

        self.generate_employees_data(employees_count, snapshot)
        self.save_to_csv(snapshot)
        self.save_to_bulk(snapshot)
        
        print("Generowanie danych pracownikow zakonczone.")