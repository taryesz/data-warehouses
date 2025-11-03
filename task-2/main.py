from generate_tram_connect_data import TramConnectDataGenerator
from generate_events_data import EventsDataGenerator
from generate_fleet_data import FleetDataGenerator
from generate_employees_data import EmployeesDataGenerator

def main():
    
    # tram_connect_data_generator = TramConnectDataGenerator()
    # tram_connect_data_generator.generate_all()
    
    # events_data_generator = EventsDataGenerator()
    # events_data_generator.generate_all()
    
    # fleet_data_generator = FleetDataGenerator()
    # fleet_data_generator.generate_all()
    
    employees_data_generator = EmployeesDataGenerator()
    employees_data_generator.generate_all()

if __name__ == "__main__":
    main()
