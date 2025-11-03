import pandas as pd
import random
from datetime import datetime, timedelta
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
    
    def generate_personal_data(self, count):
        """Generuje dane pracownikow używajac Nemesis API"""

        employees = []
        
        for i in range(1, count + 1):

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
    
    def generate_employees_data(self, snapshot='T1'):
        """Generuje kompletne dane pracownikow"""

        employees_count = 200
        
        base_employees = self.generate_personal_data(employees_count)
        
        for i, base_emp in enumerate(base_employees, 1):

            hired_date = self.random_date(datetime(2010, 1, 1), datetime(2023, 12, 31))
            
            # W T2 niektore dane sie zmieniaja (awanse)
            if snapshot == 'T2' and i <= 10:
                job_title = 'Kierownik' if random.random() > 0.5 else f"Starszy {random.choice(self.JOB_TITLES)}"
            else:
                job_title = random.choice(self.JOB_TITLES)

            education = random.choice(self.EDUCATION)
            
            self.employees_data.append({
                'ID_Pracownika': i,
                'Imię': base_emp['first_name'],
                'Drugie_Imię': base_emp['middle_name'],
                'Nazwisko': base_emp['last_name'],
                'Data_Urodzenia': base_emp['birth_date'].strftime('%Y-%m-%d'),
                'Płeć': base_emp['gender'],
                'PESEL': base_emp['pesel'],
                'Data_Zatrudnienia': hired_date.strftime('%Y-%m-%d'),
                'Stanowisko': job_title,
                'Wykształcenie_Zawód': education,
            })
    
    def save_to_csv(self, snapshot='T1'):
        """Zapisuje dane pracownikow do CSV"""

        filename = f'pracownicy_{snapshot}.csv'

        pd.DataFrame(self.employees_data).to_csv(filename, index=False, encoding='utf-8')
        print(f"Zapisano {len(self.employees_data)} pracownikow do {filename}")
       
    def generate_all(self):
        """Generuje dane pracownikow dla obu snapszotow"""

        print(">>> GENEROWANIE DANYCH PRACOWNIKOW <<<")
        
        print("Generowanie snapszotu T1...")

        self.generate_employees_data('T1')
        self.save_to_csv('T1')
        
        self.employees_data = []    # Czyscimy dane przed generowaniem T2
        
        print("Generowanie snapszotu T2...")

        self.generate_employees_data('T2')
        self.save_to_csv('T2')
        
        print("Generowanie danych pracownikow zakonczone.")

if __name__ == "__main__":
    employees = EmployeesDataGenerator()
    employees.generate()
