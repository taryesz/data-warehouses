import pandas as pd
import random
import os
from datetime import datetime, timedelta, time
from config import Config # Importuje Twój oryginalny config

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
        
        self.tram_availability = {}
        self.driver_availability = {}
        
        # --- ZMIANA: ---
        # Używamy EVENT_TRACKING_START z configu jako bazę dla T1
        self.DATE_T1 = self.EVENT_TRACKING_START 
        
        # Obliczamy datę T2 jako początek następnego miesiąca po T1
        next_month = self.DATE_T1.month + 1
        next_year = self.DATE_T1.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        # Ustawiamy T2 na pierwszy dzień następnego miesiąca
        self.DATE_T2 = datetime(next_year, next_month, 1) 
        
        print(f"Generator skonfigurowany: T1 start = {self.DATE_T1.date()}, T2 start = {self.DATE_T2.date()}")


    def load_existing_data(self, snapshot='T1'):
        """Wczytuje istniejące dane z plików CSV (flota i pracownicy)"""
        
        fleet_file = f'flota_tramwajowa_{snapshot}.csv'
        try:
            fleet_df = pd.read_csv(fleet_file)
            self.trams_data = [row.to_dict() for _, row in fleet_df.iterrows()]
            self.tram_availability = {tram['Numer_Boczny']: datetime.min for tram in self.trams_data}
            print(f"Wczytano {len(self.trams_data)} tramwajów z {fleet_file}")
        except FileNotFoundError:
            print(f"Nie znaleziono pliku {fleet_file}")
            exit(1)

        employees_file = f'pracownicy_{snapshot}.csv'
        try:
            employees_df = pd.read_csv(employees_file)
            drivers_df = employees_df[employees_df['Stanowisko'] == 'Kierowca']
            self.drivers_data = [row.to_dict() for _, row in drivers_df.iterrows()]
            self.driver_availability = {driver['ID_Pracownika']: datetime.min for driver in self.drivers_data}
            print(f"Wczytano {len(self.drivers_data)} kierowców z {employees_file}")
        except FileNotFoundError:
            print(f"Nie znaleziono pliku {employees_file}")
            exit(1)

    def generate_stops(self):
        """Generuje dane przystanków"""
        self.stops_data = [] # Czyścimy listę
        for i in range(1, len(self.STOPS) + 1):
            self.stops_data.append({
                'id_przystanku': i,
                'nazwa': self.STOPS[i-1]
            })
    
    def generate_lines(self):
        """Generuje dane linii"""
        self.lines_data = [] # Czyścimy listę
        for i in range(1, len(self.LINES) + 1):
            self.lines_data.append({
                'id_linii': i,
                'nazwa_linii': self.LINES[i-1]
            })
    
    def generate_stop_segment(self):
        """Generuje połączenia między przystankami"""
        self.stop_segment_data = [] # Czyścimy listę
        segment_id = 1
        for i in range(1, len(self.STOPS)):
            for j in range(i + 1, min(i + 4, len(self.STOPS) + 1)):
                self.stop_segment_data.append({
                    'id_przystanek_odcinek': segment_id,
                    'przystanek_pocz': i,
                    'przystanek_kon': j
                })
                segment_id += 1
    
    def _generate_course_batch(self, start_id, count, start_date, end_date):
        """
        Generuje 'count' kursów, zaczynając od 'start_id', 
        w zakresie dat, sprawdzając dostępność tramwajów i kierowców.
        Zwraca listę nowo wygenerowanych kursów.
        """
        
        new_courses = []
        generated_count = 0
        current_id = start_id
        current_date = start_date
        attempts = 0
        # Zabezpieczenie przed nieskończoną pętlą (zwiększone dla większej liczby kursów)
        max_attempts = max(count * 100, 5000000) 
        
        days_in_period = (end_date - start_date).days
        if days_in_period <= 0:
            days_in_period = 1
            
        courses_per_day_approx = count / days_in_period
        
        # Jeśli prób jest więcej niż ~połowa kursów na dzień, przejdź do następnego dnia
        attempts_per_day_limit = max(10, int(courses_per_day_approx / 2)) 
        if attempts_per_day_limit == 0: attempts_per_day_limit = 1 # Unikaj dzielenia przez zero

        while generated_count < count and attempts < max_attempts:
            attempts += 1
            
            hour = random.randint(5, 22) # Godziny kursowania
            minute = random.randint(0, 59)
            oczek_start = datetime.combine(current_date, time(hour, minute))
            
            # Przesuń datę do przodu
            if attempts % attempts_per_day_limit == 0:
                 current_date += timedelta(days=1)
                 if current_date > end_date:
                     current_date = start_date # Wróć na początek

            duration = timedelta(minutes=random.randint(30, 120))
            oczek_end = oczek_start + duration
            
            real_start = oczek_start
            real_end = oczek_end
            
            # 10% szans na opóźniony start
            if random.random() < 0.10:
                start_delay = timedelta(minutes=random.randint(1, 10))
                real_start = oczek_start + start_delay
            
            # 15% szans na opóźnienie na końcu (niezależne od startu)
            if random.random() < 0.15:
                end_delay = timedelta(minutes=random.randint(1, 20))
                real_end = oczek_end + end_delay
            
            # Upewnij się, że realny koniec jest po realnym starcie
            if real_end < real_start:
                real_end = real_start + duration 
            
            # --- Sprawdzanie dostępności ---
            available_trams = [tid for tid, end_time in self.tram_availability.items() if end_time <= oczek_start]
            if not available_trams:
                continue # Nie ma tramwaju, spróbuj o innej godzinie

            tram_id = random.choice(available_trams)
            
            available_drivers = [did for did, end_time in self.driver_availability.items() if end_time <= oczek_start]
            if not available_drivers:
                continue # Nie ma kierowcy
                
            driver_id = random.choice(available_drivers)
            
            # --- Rezerwacja zasobów ---
            self.tram_availability[tram_id] = real_end + timedelta(minutes=10) # Bufor na sprzątanie
            self.driver_availability[driver_id] = real_end + timedelta(minutes=30) # Bufor na przerwę
            
            new_course_data = {
                'id_kursu': current_id,
                'id_linii': random.randint(1, len(self.LINES)),
                'id_tramwaju': tram_id,
                'id_kierowcy': driver_id,
                'oczek_czas_rozp': oczek_start,
                'oczek_czas_zak': oczek_end,
                'real_czas_rozp': real_start,
                'real_czas_zak': real_end
            }
            
            new_courses.append(new_course_data)
            self.courses_data.append(new_course_data) # Dodajemy do głównej listy
            
            generated_count += 1
            current_id += 1

        if generated_count < count:
            print(f"OSTRZEŻENIE: Wygenerowano tylko {generated_count} z {count} kursów (na {max_attempts} prób). Może brakować zasobów (tramwajów/kierowców).")
        
        return new_courses # Zwracamy tylko nowe kursy

    def generate_t1_courses(self):
        """Generuje dane kursów dla T1"""
        
        self.load_existing_data('T1') 
        
        start_date = self.DATE_T1
        end_date = self.DATE_T2 - timedelta(days=1) # T1 trwa do dnia przed T2
        
        # Używamy COURSES_COUNT z Twojego pliku config.py
        courses_count = self.COURSES_COUNT 
        
        print(f"Generowanie {courses_count} kursów dla T1 (Zakres: {start_date.date()} do {end_date.date()})...")
        self._generate_course_batch(
            start_id=1, 
            count=courses_count, 
            start_date=start_date, 
            end_date=end_date
        )

    def _generate_segments_for_course(self, course):
        """Generuje odcinki dla pojedynczego kursu, dopasowując czasy."""
        
        segments_count = random.randint(5, 15)
        new_segments = [] # Lista na nowe segmenty
        
        try:
            # Upewnij się, że dane są obiektami datetime
            oczek_start = course['oczek_czas_rozp'] if isinstance(course['oczek_czas_rozp'], datetime) else datetime.fromisoformat(str(course['oczek_czas_rozp']))
            oczek_end = course['oczek_czas_zak'] if isinstance(course['oczek_czas_zak'], datetime) else datetime.fromisoformat(str(course['oczek_czas_zak']))
            real_start = course['real_czas_rozp'] if isinstance(course['real_czas_rozp'], datetime) else datetime.fromisoformat(str(course['real_czas_rozp']))
            real_end = course['real_czas_zak'] if isinstance(course['real_czas_zak'], datetime) else datetime.fromisoformat(str(course['real_czas_zak']))
        except Exception as e:
            print(f"Błąd konwersji czasu dla kursu {course['id_kursu']}: {e}")
            return []

        total_oczek_duration = oczek_end - oczek_start
        total_real_duration = real_end - real_start

        if total_oczek_duration <= timedelta(0) or segments_count == 0:
             print(f"Pominięto generowanie odcinków dla kursu {course['id_kursu']} (nieprawidłowy czas oczekiwany).")
             return []
        
        # Jeśli realny czas jest zły, użyj oczekiwanego
        if total_real_duration <= timedelta(0):
            real_start = oczek_start
            real_end = oczek_end
            total_real_duration = total_oczek_duration

        avg_oczek_duration = total_oczek_duration / segments_count
        avg_real_duration = total_real_duration / segments_count
        
        current_oczek_time = oczek_start
        current_real_time = real_start

        for segment_num in range(segments_count):
            oczek_seg_start = current_oczek_time
            real_seg_start = current_real_time
            
            oczek_seg_end = oczek_end # Domyślnie dla ostatniego
            real_seg_end = real_end # Domyślnie dla ostatniego

            if segment_num < segments_count - 1:
                # Losowość czasu trwania odcinka
                rand_factor = random.uniform(0.8, 1.2)
                oczek_seg_duration = max(timedelta(minutes=1), avg_oczek_duration * rand_factor)
                real_seg_duration = max(timedelta(minutes=1), avg_real_duration * rand_factor)
                
                oczek_seg_end = current_oczek_time + oczek_seg_duration
                real_seg_end = current_real_time + real_seg_duration
                
                # Zabezpieczenie przed przekroczeniem czasu całkowitego
                oczek_seg_end = min(oczek_seg_end, oczek_end - timedelta(minutes=(segments_count - 1 - segment_num)))
                real_seg_end = min(real_seg_end, real_end - timedelta(minutes=(segments_count - 1 - segment_num)))

            segment_data = {
                'id_kursu': course['id_kursu'],
                'id_przystanek_odcinek': random.randint(1, len(self.stop_segment_data)),
                'numer_odcinka': segment_num + 1,
                'oczek_czas_odj': oczek_seg_start,
                'oczek_czas_przyj': oczek_seg_end,
                'real_czas_odj': real_seg_start,
                'real_czas_przyj': real_seg_end,
                'liczba_pas': random.randint(0, 150)
            }
            
            new_segments.append(segment_data)
            self.segments_data.append(segment_data) # Dodajemy do głównej listy
            
            # Czas startu następnego odcinka = czas końca bieżącego
            current_oczek_time = oczek_seg_end
            current_real_time = real_seg_end
        
        return new_segments # Zwracamy wygenerowane segmenty

    def generate_t1_segments(self):
        """Generuje dane odcinków dla T1"""
        
        print(f"Generowanie odcinków dla {len(self.courses_data)} kursów T1...")
        for course in self.courses_data:
            self._generate_segments_for_course(course)
        print(f"Wygenerowano łącznie {len(self.segments_data)} odcinków dla T1.")

    def save_to_bulk(self, snapshot='T1'):
        """Zapisuje dane w formacie BULK do ładowania do SQL"""
        
        # Zapisuj dane wymiarów (przystanki, linie) tylko dla T1
        # Zakładamy, że T2 używa tych samych wymiarów co T1
        if snapshot == 'T1':
            with open(f'przystanki_{snapshot}.bulk', 'w', encoding='utf-8') as f:
                for stop in self.stops_data:
                    f.write(f"{stop['id_przystanku']}|{stop['nazwa']}\n")
            print(f"Zapisano {len(self.stops_data)} przystanków do przystanki_{snapshot}.bulk")

            with open(f'linie_{snapshot}.bulk', 'w', encoding='utf-8') as f:
                for line in self.lines_data:
                    f.write(f"{line['id_linii']}|{line['nazwa_linii']}\n")
            print(f"Zapisano {len(self.lines_data)} linii do linie_{snapshot}.bulk")

            with open(f'przystanek_odcinek_{snapshot}.bulk', 'w', encoding='utf-8') as f:
                for segment in self.stop_segment_data:
                    f.write(f"{segment['id_przystanek_odcinek']}|{segment['przystanek_pocz']}|{segment['przystanek_kon']}\n")
            print(f"Zapisano {len(self.stop_segment_data)} połączeń do przystanek_odcinek_{snapshot}.bulk")
        
        # Dane transakcyjne (kursy, odcinki) zapisuj zawsze dla danego snapshotu
        with open(f'kursy_{snapshot}.bulk', 'w', encoding='utf-8') as f:
            for course in self.courses_data:
                f.write(f"{course['id_kursu']}|{course['id_linii']}|{course['id_tramwaju']}|{course['id_kierowcy']}|"
                        f"{course['oczek_czas_rozp']}|{course['oczek_czas_zak']}|{course['real_czas_rozp']}|{course['real_czas_zak']}\n")
        print(f"Zapisano {len(self.courses_data)} kursów do kursy_{snapshot}.bulk")

        with open(f'odcinki_{snapshot}.bulk', 'w', encoding='utf-8') as f:
            for segment in self.segments_data:
                f.write(f"{segment['id_kursu']}|{segment['id_przystanek_odcinek']}|{segment['numer_odcinka']}|"
                        f"{segment['oczek_czas_odj']}|{segment['oczek_czas_przyj']}|{segment['real_czas_odj']}|"
                        f"{segment['real_czas_przyj']}|{segment['liczba_pas']}\n")
        print(f"Zapisano {len(self.segments_data)} odcinków do odcinki_{snapshot}.bulk")
    
    # --- LOGIKA T1 vs T2 ---
    
    def _generate_t1_data(self):
        """Wykonuje pełne generowanie danych dla T1"""
        
        # 1. Resetowanie danych transakcyjnych
        self.courses_data = []
        self.segments_data = []
        
        # 2. Generowanie wymiarów
        self.generate_stops()
        self.generate_lines()
        self.generate_stop_segment()
        print(f"Wygenerowano {len(self.stops_data)} przystanków, {len(self.lines_data)} linii, {len(self.stop_segment_data)} połączeń")
        
        # 3. Generowanie faktów (transakcji)
        self.generate_t1_courses()
        self.generate_t1_segments()

    def _load_t1_data(self):
        """Wczytuje pliki .bulk T1 do pamięci"""
        print("Wczytywanie danych T1 z plików .bulk...")
        
        try:
            # Wczytywanie wymiarów (potrzebne do generowania nowych odcinków w T2)
            print("Wczytywanie wymiarów T1...")
            stops_df = pd.read_csv(
                'przystanki_T1.bulk', sep='|', names=['id_przystanku', 'nazwa'], header=None
            )
            self.stops_data = stops_df.to_dict('records')
            
            lines_df = pd.read_csv(
                'linie_T1.bulk', sep='|', names=['id_linii', 'nazwa_linii'], header=None
            )
            self.lines_data = lines_df.to_dict('records')
            
            stop_segment_df = pd.read_csv(
                'przystanek_odcinek_T1.bulk', sep='|', 
                names=['id_przystanek_odcinek', 'przystanek_pocz', 'przystanek_kon'], header=None
            )
            self.stop_segment_data = stop_segment_df.to_dict('records')
            
            print(f"Wczytano {len(self.stops_data)} przystanków, {len(self.lines_data)} linii, {len(self.stop_segment_data)} połączeń.")

            # Wczytywanie faktów (do modyfikacji)
            print("Wczytywanie faktów T1 (kursy i odcinki)...")
            course_cols = ['id_kursu', 'id_linii', 'id_tramwaju', 'id_kierowcy', 'oczek_czas_rozp', 'oczek_czas_zak', 'real_czas_rozp', 'real_czas_zak']
            date_cols = ['oczek_czas_rozp', 'oczek_czas_zak', 'real_czas_rozp', 'real_czas_zak']
            
            courses_df = pd.read_csv(
                'kursy_T1.bulk', sep='|', names=course_cols, parse_dates=date_cols, header=None
            )
            
            segment_cols = ['id_kursu', 'id_przystanek_odcinek', 'numer_odcinka', 'oczek_czas_odj', 'oczek_czas_przyj', 'real_czas_odj', 'real_czas_przyj', 'liczba_pas']
            seg_date_cols = ['oczek_czas_odj', 'oczek_czas_przyj', 'real_czas_odj', 'real_czas_przyj']
            
            segments_df = pd.read_csv(
                'odcinki_T1.bulk', sep='|', names=segment_cols, parse_dates=seg_date_cols, header=None
            )
            
            print(f"Wczytano {len(courses_df)} kursów i {len(segments_df)} odcinków z T1.")
            return courses_df, segments_df

        except FileNotFoundError as e:
            print(f"BŁĄD: Nie znaleziono pliku .bulk T1: {e.filename}")
            print("Nie można wygenerować T2 bez danych T1. Uruchom najpierw generowanie T1.")
            exit(1)
        except Exception as e:
            print(f"BŁĄD podczas wczytywania plików T1: {e}")
            exit(1)

    def _modify_t1_data_for_t2(self, courses_df, segments_df):
        """Modyfikuje wczytane dane T1 zgodnie z logiką T2"""
        print("Modyfikowanie danych T1 na potrzeby T2...")
        
        # Modyfikacja 1: Zwiększamy opóźnienia kursów (większe/częstsze)
        # 20% kursów T1 dostanie dodatkowe opóźnienie
        indices_to_modify = courses_df.sample(frac=0.2).index
        
        for idx in indices_to_modify:
            # Dodajmy od 10 do 30 minut opóźnienia
            extra_delay = timedelta(minutes=random.randint(10, 30))
            courses_df.at[idx, 'real_czas_zak'] = courses_df.at[idx, 'real_czas_zak'] + extra_delay

        print(f"Zmodyfikowano opóźnienia dla {len(indices_to_modify)} kursów z T1.")
        
        # Modyfikacja 2: Zwiększamy liczbę pasażerów na odcinkach
        # 30% odcinków T1 będzie miało większe obłożenie
        seg_indices_to_modify = segments_df.sample(frac=0.3).index
        
        for idx in seg_indices_to_modify:
            # Zwiększ liczbę pasażerów o 20% do 50%
            factor = random.uniform(1.2, 1.5)
            new_pass_count = int(segments_df.at[idx, 'liczba_pas'] * factor)
            segments_df.at[idx, 'liczba_pas'] = min(new_pass_count, 200) # Ograniczenie do max 200

        print(f"Zmodyfikowano liczbę pasażerów dla {len(seg_indices_to_modify)} odcinków z T1.")
        
        return courses_df, segments_df

    def _generate_t2_data(self):
        """Wykonuje pełne generowanie danych dla T2"""
        
        # 1. Wczytaj dane T1 z plików .bulk
        courses_t1_df, segments_t1_df = self._load_t1_data()
        
        # 2. Zmodyfikuj wczytane dane T1
        courses_mod_df, segments_mod_df = self._modify_t1_data_for_t2(courses_t1_df, segments_t1_df)
        
        # 3. Załaduj zmodyfikowane dane do list w klasie
        # .to_dict('records') jest najszybszym sposobem
        self.courses_data = courses_mod_df.to_dict('records')
        self.segments_data = segments_mod_df.to_dict('records')
        
        max_t1_id = courses_mod_df['id_kursu'].max()
        print(f"Maksymalne ID kursu z T1: {max_t1_id}")
        
        # 4. Wczytaj zasoby T2 (nowi kierowcy, nowe tramwaje)
        print("Wczytywanie zasobów (flota, pracownicy) dla T2...")
        self.load_existing_data('T2') # To resetuje i ładuje tram_availability i driver_availability
        
        # 5. Uzupełnij dostępność zasobów na podstawie ZMODYFIKOWANYCH danych T1
        # Musimy to zrobić, aby nowe kursy T2 nie nałożyły się na kursy T1
        print("Aktualizowanie dostępności zasobów na podstawie danych T1...")
        for course in self.courses_data:
            tram_id = course['id_tramwaju']
            driver_id = course['id_kierowcy']
            
            # Pobierz realny czas zakończenia (już jako datetime z pandas)
            real_end_time = course['real_czas_zak']
            
            if tram_id in self.tram_availability:
                self.tram_availability[tram_id] = max(self.tram_availability[tram_id], real_end_time + timedelta(minutes=10))
                
            if driver_id in self.driver_availability:
                self.driver_availability[driver_id] = max(self.driver_availability[driver_id], real_end_time + timedelta(minutes=30))
        
        # 6. Generuj NOWE 50 tys. kursów dla T2
        new_courses_count = 50000 
        start_date_t2 = self.DATE_T2
        end_date_t2 = self.DATE_T2 + timedelta(days=29) # Zakres T2 (np. luty)
        
        print(f"Generowanie {new_courses_count} nowych kursów dla T2 (Zakres: {start_date_t2.date()} do {end_date_t2.date()})...")
        
        # _generate_course_batch dodaje nowe kursy do self.courses_data
        # i zwraca listę TYLKO tych NOWYCH
        newly_generated_courses = self._generate_course_batch(
            start_id=max_t1_id + 1,
            count=new_courses_count,
            start_date=start_date_t2,
            end_date=end_date_t2
        )
        
        print(f"Wygenerowano {len(newly_generated_courses)} nowych kursów.")
        
        # 7. Generuj odcinki TYLKO dla nowo wygenerowanych kursów
        print(f"Generowanie odcinków dla {len(newly_generated_courses)} nowych kursów...")
        new_segments_count = 0
        for course in newly_generated_courses:
            # _generate_segments_for_course dodaje segmenty do self.segments_data
            new_segments = self._generate_segments_for_course(course)
            new_segments_count += len(new_segments)
            
        print(f"Wygenerowano {new_segments_count} nowych odcinków.")
        
        # 8. Zakończono
        print(f"Łącznie w T2: {len(self.courses_data)} kursów i {len(self.segments_data)} odcinków.")

    def generate_all(self, snapshot="T1"):
        """Główna metoda generująca dane"""

        print(f"--- GENEROWANIE DANYCH TramConnect: {snapshot} ---")
        
        if snapshot == 'T1':
            print(f"Rozpoczynanie generowania snapszotu {snapshot}...")
            self._generate_t1_data()
            
        elif snapshot == 'T2':
            print(f"Rozpoczynanie generowania snapszotu {snapshot} (na podstawie T1)...")
            self._generate_t2_data()
            
        else:
            print(f"Nieznany snapshot: {snapshot}")
            return

        # 9. Zapisz wszystkie dane do plików .bulk
        print(f"Zapisywanie danych do plików .bulk dla {snapshot}...")
        self.save_to_bulk(snapshot)
        
        print(f"--- Generowanie danych TramConnect ({snapshot}) ZAKOŃCZONE ---")
        