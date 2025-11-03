from generate_tram_connect_data import TramConnectDataGenerator
from generate_events_data import EventsDataGenerator
from generate_fleet_data import FleetDataGenerator
from generate_employees_data import EmployeesDataGenerator

def main():
    
    employees_data_generator = EmployeesDataGenerator()
    employees_data_generator.generate_all()

    fleet_data_generator = FleetDataGenerator()
    fleet_data_generator.generate_all()

    events_data_generator = EventsDataGenerator()
    events_data_generator.generate_all()

    tram_connect_data_generator = TramConnectDataGenerator()
    tram_connect_data_generator.generate_all()

    # ====================== T2 ======================

    print('\n\n\nT2 ==================================================== \n\n\n')

    employees_data_generator.generate_all("T2")

    fleet_data_generator.generate_all("T2")

    events_data_generator.generate_all("T2")

    tram_connect_data_generator.generate_all("T2")
    
if __name__ == "__main__":
    main()
