import pandas as pd
import random
import os
from datetime import datetime, timedelta
from config import Config

class TramConnectDataGenerator(Config):

    def __init__(self):
        super().__init__()
        self.trams_data = []
        self.drivers_data = []
        self.stops_data = []
        self.lines_data = []
        self.courses_data = []
        self.stop_segment_data = []
        self.segments_data = []
    
    def load_existing_data(self, snapshot='T1'):
        """Wczytuje istniejące dane z plików CSV"""
        
        # Wczytujemy dane tramwajów
        fleet_file = f'flota_tramwajowa_{snapshot}.csv'
        try:
            fleet_df = pd.read_csv(fleet_file)
            self.trams_data = [row.to_dict() for _, row in fleet_df.iterrows()]
            print(f"Wczytano {len(self.trams_data)} tramwajów z {fleet_file}")
        except FileNotFoundError:
            print(f"Nie znaleziono pliku {fleet_file}")
            exit(1)

        # Wczytujemy dane kierowców
        employees_file = f'pracownicy_{snapshot}.csv'
        try:
            employees_df = pd.read_csv(employees_file)
            drivers_df = employees_df[employees_df['Stanowisko'] == 'Kierowca']
            self.drivers_data = [row.to_dict() for _, row in drivers_df.iterrows()]
            print(f"Wczytano {len(self.drivers_data)} kierowców z {employees_file}")
        except FileNotFoundError:
            print(f"Nie znaleziono pliku {employees_file}")
            exit(1)

    def generate_stops(self):
        """Generuje dane przystanków"""
        for i in range(1, len(self.STOPS) + 1):
            self.stops_data.append({
                'id_przystanku': i,
                'nazwa': self.STOPS[i-1]
            })
    
    def generate_lines(self):
        """Generuje dane linii"""
        for i in range(1, len(self.LINES) + 1):
            self.lines_data.append({
                'id_linii': i,
                'nazwa_linii': self.LINES[i-1]
            })
    
    def generate_stop_segment(self):
        """Generuje połączenia między przystankami"""
        segment_id = 1
        for i in range(1, len(self.STOPS)):
            for j in range(i + 1, min(i + 4, len(self.STOPS) + 1)):
                self.stop_segment_data.append({
                    'id_przystanek_odcinek': segment_id,
                    'przystanek_pocz': i,
                    'przystanek_kon': j
                })
                segment_id += 1
    
    def generate_courses(self, snapshot='T1'):
        """Generuje dane kursów"""
        
        # Dla snapszotu T2 sprawdzamy czy istnieje plik T1
        if snapshot == 'T2':
            t1_filename = 'kursy_T1.csv'
            if os.path.exists(t1_filename):
                print(f"Znaleziono plik {t1_filename}, tworzenie T2 na podstawie T1...")
                self.generate_t2_courses_from_t1(t1_filename)
                return
        
        # Wczytujemy dane dla T1
        self.load_existing_data(snapshot)
        
        if snapshot == 'T1':
            courses_count = self.COURSE_COUNT_T1
            start_date = self.DATE_T1
        else:
            courses_count = self.COURSE_COUNT_T1
            start_date = self.DATE_T2
        
        end_date = start_date + timedelta(days=30)
        
        for i in range(1, courses_count + 1):
            start_time = self.random_date(start_date, end_date)
            duration = timedelta(minutes=random.randint(30, 120))
            expected_end = start_time + duration
            
            if random.random() < 0.15:
                delay = timedelta(minutes=random.randint(1, 20))
                actual_end = expected_end + delay
            else:
                actual_end = expected_end
            
            tram = random.choice(self.trams_data)
            driver = random.choice(self.drivers_data)
            
            self.courses_data.append({
                'id_kursu': i,
                'id_linii': random.randint(1, len(self.LINES)),
                'id_tramwaju': tram['Numer_Boczny'],
                'id_kierowcy': driver['ID_Pracownika'],
                'oczek_czas_rozp': start_time,
                'oczek_czas_zak': expected_end,
                'real_czas_rozp': start_time,
                'real_czas_zak': actual_end
            })
    
    def generate_t2_courses_from_t1(self, t1_filename):
        """Generuje dane T2 na podstawie istniejącego pliku T1"""
        try:
            t1_df = pd.read_csv(t1_filename)
            max_t1_id = t1_df['id_kursu'].max()

            for index, row in t1_df.iterrows():
                course_data = row.to_dict()
                
                if index < 20:  
                    original_start = datetime.fromisoformat(course_data['real_czas_rozp'])
                    new_start = original_start + timedelta(minutes=random.randint(5, 30))
                    course_data['real_czas_rozp'] = new_start.isoformat()
                
                self.courses_data.append(course_data)
            
            print(f"Zmodyfikowano {len(t1_df)} istniejących kursów z T1")

            self.load_existing_data('T2')
            
            new_courses_count = self.COURSE_COUNT_T1
            start_date_t2 = self.DATE_T2
            end_date_t2 = self.DATE_T2 + timedelta(days=30)
            
            for i in range(max_t1_id + 1, max_t1_id + new_courses_count + 1):
                start_time = self.random_date(start_date_t2, end_date_t2)
                duration = timedelta(minutes=random.randint(30, 120))
                expected_end = start_time + duration
                
                if random.random() < 0.15:
                    delay = timedelta(minutes=random.randint(1, 20))
                    actual_end = expected_end + delay
                else:
                    actual_end = expected_end
                
                tram = random.choice(self.trams_data)
                driver = random.choice(self.drivers_data)
                
                self.courses_data.append({
                    'id_kursu': i,
                    'id_linii': random.randint(1, len(self.LINES)),
                    'id_tramwaju': tram['Numer_Boczny'],
                    'id_kierowcy': driver['ID_Pracownika'],
                    'oczek_czas_rozp': start_time,
                    'oczek_czas_zak': expected_end,
                    'real_czas_rozp': start_time,
                    'real_czas_zak': actual_end
                })
            
            print(f"Dodano {new_courses_count} nowych kursów")
            print(f"Razem w T2: {len(self.courses_data)} kursów")

        except Exception as e:
            print(f"Błąd podczas wczytywania pliku {t1_filename}: {e}")
            exit(1)
    
    def generate_segments(self, snapshot='T1'):
        """Generuje dane odcinków"""
        
        if snapshot == 'T2':
            t1_filename = 'odcinki_T1.csv'
            if os.path.exists(t1_filename):
                print(f"Znaleziono plik {t1_filename}, tworzenie T2 na podstawie T1...")
                self.generate_t2_segments_from_t1(t1_filename)
                return
        
        for course in self.courses_data:
            segments_count = random.randint(5, 15)      
            current_time = course['real_czas_rozp'] if isinstance(course['real_czas_rozp'], datetime) else datetime.fromisoformat(course['real_czas_rozp'])
            
            for segment_num in range(segments_count):
                segment_duration = timedelta(minutes=random.randint(2, 10))
                expected_arrival = current_time + segment_duration
                
                if random.random() < 0.2:
                    delay = timedelta(minutes=random.randint(1, 8))
                    actual_arrival = expected_arrival + delay
                else:
                    actual_arrival = expected_arrival
                
                self.segments_data.append({
                    'id_kursu': course['id_kursu'],
                    'id_przystanek_odcinek': random.randint(1, len(self.stop_segment_data)),
                    'numer_odcinka': segment_num + 1,
                    'oczek_czas_odj': current_time,
                    'oczek_czas_przyj': expected_arrival,
                    'real_czas_odj': current_time,
                    'real_czas_przyj': actual_arrival,
                    'liczba_pas': random.randint(0, 150)
                })
                
                current_time = actual_arrival
    
    def generate_t2_segments_from_t1(self, t1_filename):
        """Generuje dane T2 na podstawie istniejącego pliku T1"""
        try:
            t1_df = pd.read_csv(t1_filename)
            
            for index, row in t1_df.iterrows():
                segment_data = row.to_dict()
                
                if index < 30:  
                    segment_data['liczba_pas'] = random.randint(100, 180)
                
                self.segments_data.append(segment_data)
            
            print(f"Zmodyfikowano {len(t1_df)} istniejących odcinków z T1")

            new_courses = [course for course in self.courses_data if course['id_kursu'] > len(t1_df)]
            
            for course in new_courses:
                segments_count = random.randint(5, 15)      
                current_time = course['real_czas_rozp'] if isinstance(course['real_czas_rozp'], datetime) else datetime.fromisoformat(course['real_czas_rozp'])
                
                for segment_num in range(segments_count):
                    segment_duration = timedelta(minutes=random.randint(2, 10))
                    expected_arrival = current_time + segment_duration
                    
                    if random.random() < 0.2:
                        delay = timedelta(minutes=random.randint(1, 8))
                        actual_arrival = expected_arrival + delay
                    else:
                        actual_arrival = expected_arrival
                    
                    self.segments_data.append({
                        'id_kursu': course['id_kursu'],
                        'id_przystanek_odcinek': random.randint(1, len(self.stop_segment_data)),
                        'numer_odcinka': segment_num + 1,
                        'oczek_czas_odj': current_time,
                        'oczek_czas_przyj': expected_arrival,
                        'real_czas_odj': current_time,
                        'real_czas_przyj': actual_arrival,
                        'liczba_pas': random.randint(0, 150)
                    })
                    
                    current_time = actual_arrival
            
            print(f"Dodano odcinki dla {len(new_courses)} nowych kursów")
            print(f"Razem w T2: {len(self.segments_data)} odcinków")

        except Exception as e:
            print(f"Błąd podczas wczytywania pliku {t1_filename}: {e}")
            exit(1)

    def save_to_bulk(self, snapshot='T1'):
        """Zapisuje dane w formacie BULK do ładowania do SQL"""
        
        # Format BULK dla kursów
        with open(f'kursy_{snapshot}.bulk', 'w', encoding='utf-8') as f:
            for course in self.courses_data:
                f.write(f"{course['id_kursu']}|{course['id_linii']}|{course['id_tramwaju']}|{course['id_kierowcy']}|"
                       f"{course['oczek_czas_rozp']}|{course['oczek_czas_zak']}|{course['real_czas_rozp']}|{course['real_czas_zak']}\n")
        print(f"Zapisano {len(self.courses_data)} kursów do kursy_{snapshot}.bulk")

        # Format BULK dla odcinków
        with open(f'odcinki_{snapshot}.bulk', 'w', encoding='utf-8') as f:
            for segment in self.segments_data:
                f.write(f"{segment['id_kursu']}|{segment['id_przystanek_odcinek']}|{segment['numer_odcinka']}|"
                       f"{segment['oczek_czas_odj']}|{segment['oczek_czas_przyj']}|{segment['real_czas_odj']}|"
                       f"{segment['real_czas_przyj']}|{segment['liczba_pas']}\n")
        print(f"Zapisano {len(self.segments_data)} odcinków do odcinki_{snapshot}.bulk")

        # Format BULK dla przystanków
        with open(f'przystanki_{snapshot}.bulk', 'w', encoding='utf-8') as f:
            for stop in self.stops_data:
                f.write(f"{stop['id_przystanku']}|{stop['nazwa']}\n")
        print(f"Zapisano {len(self.stops_data)} przystanków do przzystanki_{snapshot}.bulk")

        # Format BULK dla linii
        with open(f'linie_{snapshot}.bulk', 'w', encoding='utf-8') as f:
            for line in self.lines_data:
                f.write(f"{line['id_linii']}|{line['nazwa_linii']}\n")
        print(f"Zapisano {len(self.lines_data)} linii do linie_{snapshot}.bulk")

        # Format BULK dla połączeń przystanków
        with open(f'przystanek_odcinek_{snapshot}.bulk', 'w', encoding='utf-8') as f:
            for segment in self.stop_segment_data:
                f.write(f"{segment['id_przystanek_odcinek']}|{segment['przystanek_pocz']}|{segment['przystanek_kon']}\n")
        print(f"Zapisano {len(self.stop_segment_data)} połączeń do przystanek_odcinek_{snapshot}.bulk")
    
    def generate_all(self, snapshot="T1"):
        """Generuje wszystkie dane"""

        print(">>> GENEROWANIE DANYCH TramConnect <<<")
        
        print(f"Generowanie snapszotu {snapshot}...")

        if snapshot == 'T1':
            self.courses_data = []
            self.segments_data = []
        
        if snapshot == 'T1':
            self.stops_data = []
            self.lines_data = []
            self.stop_segment_data = []
            
            self.generate_stops()
            self.generate_lines()
            self.generate_stop_segment()
            print(f"Wygenerowano {len(self.stops_data)} przystanków, {len(self.lines_data)} linii, {len(self.stop_segment_data)} połączeń")
        
        self.generate_courses(snapshot)
        self.generate_segments(snapshot)
        
        self.save_to_bulk(snapshot)
        
        print("Generowanie danych TramConnect zakończone.")
