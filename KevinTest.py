# ----- Import libraries -----
import salabim as sim
import numpy as np
import math
import csv

# ----- Import function -----
from PortFunctions import find_port_distance, get_port_delay

# ----- Create constants -----
container_time = 0.05  # [hr]
battery_capacity = 3000  # [kWh]
charging_time = 1  # [hr]
ship_battery_limit = 25  # [-]
additional_battery_number = 20  # [-]
battery_warning = ship_battery_limit  # [-]

# ----- Create simulation constants -----
sim_ship_number = 30  # [-] (Thirty should be enough for a whole fleet)
sim_length = 10000  # [hr]
zero_holdings = 0  # Amount of times a ship has to wait for batteries

# ----- Create record keeping -----
trace = [["Time", "Object", "Event"]]


class ShipGenerator(sim.Component):
    """
    Creates a certain amount of ships, with accompanying start and ending ports.
    """
    def setup(self, amount_of_ships):
        self.amount_of_ships = amount_of_ships

    def process(self):
        # Create a certain amount of ships
        for _ in range(self.amount_of_ships):
            # Generate starting port
            start_port_string = port_choice()
            start_port = port_dict[start_port_string]

            # Generate ending port
            end_port_string = port_choice(current_port=start_port_string)
            end_port = port_dict[end_port_string]

            # Create instance of ship with starting and end ports
            Ship(current_port=start_port, destination_port=end_port,
                 current_port_string=start_port_string,
                 destination_port_string=end_port_string)
            # Hold generator to avoid congestion
            self.hold(sim.Uniform(5, 15).sample())

        # Finalize creating ships
        print("All ships generated!")
        trace.append([env.now(), "ShipGenerator",
                      "Finished generating all ships"])


class Ship(sim.Component):
    """
    Instance of a ship, with starting and ending ports.
    """
    def setup(self, current_port, destination_port,
              current_port_string, destination_port_string):
        self.length = 100  # [m]
        self.speed = 15  # [km/h]
        self.current_port = current_port
        self.current_port_string = current_port_string
        self.destination_port = destination_port
        self.destination_port_string = destination_port_string
        self.container_target = 0
        self.battery_limit = ship_battery_limit  # Also assume 3 kWh / battery
        self.power = 1000  # [kW]
        self.full_batteries = 0
        self.empty_batteries = 0
        self.half_battery_charge = 0

    def process(self):
        while True:
            # Sample amount of containers to be loaded onboard
            self.container_target = int(sim.Uniform(50, 100).sample())
            loading_time = self.container_target * container_time

            # Load containers
            self.hold(loading_time)
            print(f"{env.now()}: {self.name()} has loaded "
                  f"{self.container_target} containers as cargo.")

            trace.append([env.now(), f"{self.name()}",
                          f"loaded {self.container_target} containers as cargo "
                          f"in {self.current_port_string}"])

            self.current_port.cargo_output += self.container_target

            # Check if arrival port has a warning on it
            if self.destination_port.warning_status:
                # Then load even more battery containers to compensate
                self.battery_limit = (ship_battery_limit
                                      + additional_battery_number)
            # If no warning exists
            else:
                # Then reset to nominal value
                self.battery_limit = ship_battery_limit

            # Check if port has enough batteries or not, otherwise hold
            while self.current_port.batteries - self.battery_limit < 0:
                self.hold(1)
                global zero_holdings
                zero_holdings += 1
                print("Holding!")

            # Load battery containers
            self.hold(self.battery_limit * container_time)
            print(f"{env.now()}: {self.name()} has loaded {self.battery_limit} "
                  f"batteries from {self.current_port_string}.")
            trace.append([env.now(), f"{self.name()}",
                          f"Ship has loaded {self.battery_limit} batteries "
                          f"from {self.current_port_string}"])

            self.current_port.batteries -= self.battery_limit

            print(f"{env.now()}: {self.current_port_string} has "
                  f"{self.current_port.batteries} batteries left.")

            trace.append([env.now(), f"{self.current_port_string}",
                          f"{self.current_port_string} has "
                          f"{self.current_port.batteries} batteries left."])

            self.current_port.activate(process='check_warning')

            # Update battery / charge
            self.full_batteries = self.battery_limit
            self.charge = self.full_batteries * battery_capacity

            # Leave the current port's queue if it's in one
            if self in self.current_port.queue:
                self.leave(self.current_port.queue)

            # Find port distance
            distance = find_port_distance(self.current_port_string,
                                          self.destination_port_string)

            # Calculate voyage duration
            duration = distance / self.speed

            # Start holding for the duration of voyage in hours
            self.hold(duration)

            # Arrive at port, but with possible waiting time
            waiting_time = get_port_delay()
            self.hold(waiting_time)

            # Update battery / charge
            depleted_charge = duration * self.power
            charge_ratio = (self.charge - depleted_charge) / self.charge

            self.full_batteries = math.floor(self.battery_limit * charge_ratio)
            self.empty_batteries = math.floor(self.battery_limit
                                              * (1 - charge_ratio))
            self.half_battery_charge = ((self.battery_limit * charge_ratio)
                                        - self.full_batteries)

            self.charge -= depleted_charge

            # Enter the destination port's queue
            self.enter(self.destination_port.queue)

            # Update current port
            self.current_port = self.destination_port
            self.current_port_string = self.destination_port_string

            # Generate a new destination port
            end_port_string = port_choice(current_port=self.current_port_string)
            end_port = port_dict[end_port_string]

            # Update the destination ports
            self.destination_port = end_port
            self.destination_port_string = end_port_string

            # Start unloading cargo
            unloading_time = self.container_target * container_time
            self.hold(unloading_time)

            self.current_port.cargo_input += self.container_target

            # Start unloading batteries
            battery_unloading_time = self.battery_limit * container_time
            self.hold(battery_unloading_time)

            # Update port's batteries
            self.current_port.batteries += self.full_batteries
            self.current_port.empty_batteries += self.empty_batteries
            self.current_port.half_empty_batteries += 1
            self.current_port.half_empty_charges.append(self.half_battery_charge)

            # Activate the charging station since new batteries have arrived
            self.current_port.activate(process='charging_station')


class Port(sim.Component):
    """
    Instance of a port, with a name and accompanying queue.
    """
    def setup(self, charging_spots):
        self.name = self.name()
        self.queue = sim.Queue(self.name)
        self.batteries = 100  # Assume 100 batteries in port to start
        self.empty_batteries = 0  # No empty batteries to start
        self.half_empty_batteries = 0  # No half empty batteries to start
        self.half_empty_charges = []  # No half empty batteries to start
        self.warning_status = False
        self.total_charged = 0
        self.cargo_input = 0  # Amount of containers entering port
        self.cargo_output = 0  # Amount of containers leaving port
        self.warning_times = 0  # Amount of warning turn-ons
        self.zero_crossings = 0  # Amount of hours #batteries are below zero
        self.charging_spots = charging_spots

    # Charging station, which is activated by the arrival of new batteries
    def charging_station(self):
        # Check for any half empty battery containers
        while self.half_empty_batteries > 0:
            # Charge said half empty battery container until it's full
            self.hold(self.half_empty_charges[0] * charging_time)

            # Remove battery from half empty list since it's charged
            del self.half_empty_charges[0]

            # Remove half empty battery
            self.half_empty_batteries -= 1

            # Add now fully charged battery
            self.batteries += 1

        # Check for any empty batteries
        while self.empty_batteries > 0:
            # Charge for a battery's charging time
            self.hold(charging_time)

            # Update the amount of empty batteries left
            if self.empty_batteries <= self.charging_spots:
                # Add fully charged batteries
                self.batteries += self.empty_batteries
                self.total_charged += self.empty_batteries

                # Set current empty batteries to zero
                self.empty_batteries = 0
            else:
                # Remove charged batteries
                self.empty_batteries -= self.charging_spots

                # Add fully charged batteries
                self.batteries += self.charging_spots
                self.total_charged += self.charging_spots
            
            #self.activate(process='check_warning')
            self.check_warning()

        # Passivate self to save resources - until more batteries arrive
        # self.passivate()

    # Warning check after new batteries are loaded from port to ship
    def check_warning(self):
        # If batteries are below zero
        if self.batteries < 0:
            self.zero_crossings += 1

        # If battery warning threshold has been breached
        if self.batteries <= battery_warning and not self.warning_status:
            # Then add the warning status to the port
            self.warning_status = True

            # Add print for fun (and to check)
            print(f"Warning activated in the port of {self.name}!")
            print(f"Only {self.batteries} left!")
            
            trace.append([env.now(), self.name,
                          f"Warning activated in {self.name}, "
                          f"only {self.batteries} batteries left"])

            self.warning_times += 1

        # If the battery warning threshold has not been breached
        if (self.batteries > battery_warning) and self.warning_status:
            # If so, then remove warning status
            self.warning_status = False

            # Add print for fun (and to check)
            print(f"Warning deactivated in the port of {self.name}.")
            trace.append([env.now(), self.name,
                          f"Warning deactivated in {self.name}, "
                          f"{self.batteries} batteries available"])


def port_choice(current_port=None):
    """
    Chooses a port from a list, with a given chance to generate said port.
    :param current_port: str, in case the ship is already in a port
    :return: str, the chosen port
    """

    # Data (from CCNR Annual report 2023)
    port_list = ['Rotterdam', 'Antwerp', 'Amsterdam', 'Duisburg', 'Vlissingen',
                 'Paris', 'Liege', 'Terneuzen', 'Moerdijk', 'Cologne',
                 'Mannheim',
                 'Karlsruhe', 'Louviere', 'Sittard', 'Velsen', 'Strasbourg',
                 'Dordrecht', 'Neuss', 'Ludwigshafen', 'Brussels', 'Delfzijl']

    port_odds = [0.297, 0.199, 0.111, 0.083, 0.048, 0.041, 0.029, 0.023, 0.019,
                 0.016, 0.015, 0.013, 0.013, 0.013, 0.013, 0.013, 0.012, 0.011,
                 0.011, 0.010, 0.010]

    # Check if ship is already in a port
    if current_port is not None:
        # Find index of current port
        current_port_index = port_list.index(current_port)

        # Remove current port from list of possiblities
        del port_list[current_port_index]
        del port_odds[current_port_index]

        # Rescale port odds to sum to 1
        new_port_odds = [odd / sum(port_odds) for odd in port_odds]

        # Choose port
        chosen_port = str(np.random.choice(port_list, 1, p=new_port_odds)[0])

        return chosen_port
    else:
        # Choose port
        chosen_port = str(np.random.choice(port_list, 1, p=port_odds)[0])

        return chosen_port


# Create environment
env = sim.Environment(trace=False)

# Create a certain number of ships using the Ship Generator
ShipGenerator(amount_of_ships=sim_ship_number)

# Create all ports included in the simulation
port_rotterdam = Port('Rotterdam', charging_spots=20)
port_antwerp = Port('Antwerp', charging_spots=20)
port_amsterdam = Port('Amsterdam', charging_spots=15)
port_duisburg = Port('Duisburg', charging_spots=15)
port_vlissingen = Port('Vlissingen', charging_spots=10)
port_paris = Port('Paris', charging_spots=8)
port_Liege = Port('Liege', charging_spots=5)
port_terneuzen = Port('Terneuzen', charging_spots=3)
port_moerdijk = Port('Moerdijk', charging_spots=3)
port_cologne = Port('Cologne', charging_spots=3)
port_mannheim = Port('Mannheim', charging_spots=3)
port_karlsruhe = Port('Karlsruhe', charging_spots=3)
port_louviere = Port('Louviere', charging_spots=3)
port_sittard = Port('Sittard', charging_spots=3)
port_velsen = Port('Velsen', charging_spots=3)
port_strasbourg = Port('Strasbourg', charging_spots=3)
port_dordrecht = Port('Dordrecht', charging_spots=3)
port_neuss = Port('Neuss', charging_spots=3)
port_ludwigshafen = Port('Ludwigshafen', charging_spots=3)
port_brussels = Port('Brussels', charging_spots=3)
port_delfzijl = Port('Delfzijl', charging_spots=3)

# Create dictionary that maps strings to objects
port_dict = {'Rotterdam': port_rotterdam,
             'Antwerp': port_antwerp,
             'Amsterdam': port_amsterdam,
             'Duisburg': port_duisburg,
             'Vlissingen': port_vlissingen,
             'Paris': port_paris,
             'Liege': port_Liege,
             'Terneuzen': port_terneuzen,
             'Moerdijk': port_moerdijk,
             'Cologne': port_cologne,
             'Mannheim': port_mannheim,
             'Karlsruhe': port_karlsruhe,
             'Louviere': port_louviere,
             'Sittard': port_sittard,
             'Velsen': port_velsen,
             'Strasbourg': port_strasbourg,
             'Dordrecht': port_dordrecht,
             'Neuss': port_neuss,
             'Ludwigshafen': port_ludwigshafen,
             'Brussels': port_brussels,
             'Delfzijl': port_delfzijl}

# Start simulation
env.run(till=sim_length)

with open('Trace.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(trace)


# Results
def results_printer():
    """
    Prints results after running the entire simulation.
    Put into a function, so it can be hidden away.
    """

    print("\n_______________RESULTS_________________")

    print("\n")
    print("Batteries per port:")
    tot_bat = 0
    for value, port in port_dict.items():
        print(f"{port.name}: {port.batteries}")
        tot_bat += port.batteries
    print("Total number of batteries in ports: ", tot_bat)

    print("\n")
    print("Warning status per port:")
    for value, port in port_dict.items():
        print(f"{port.name}: {port.warning_status}")

    print("\n")
    total_warnings = 0
    print("Amount of warnings per port:")
    for value, port in port_dict.items():
        print(f"{port.name}: {port.warning_times}")
        total_warnings += port.warning_times
    print("Total numbers of warnings during the simulation: ", total_warnings)

    print("\n")
    total_zeros = 0
    print("Amount of hours below zero batteries per port:")
    for value, port in port_dict.items():
        print(f"{port.name}: {port.zero_crossings}")
        total_zeros += port.zero_crossings
    print("Total amount of hours below zero batteries: ", total_zeros)

    print("\n")
    print("Total number of empty batteries per port:")
    total_empty_bat = 0
    for value, port in port_dict.items():
        print(f"{port.name}: {port.empty_batteries}")
        total_empty_bat += port.empty_batteries
    print("Total number of empty batteries in ports: ", total_empty_bat)

    print("\n")
    print("Total number of half empty batteries remaining per port:")
    total_half_bat = 0
    for value, port in port_dict.items():
        print(f"{port.name}: {port.half_empty_batteries}")
        total_half_bat += port.half_empty_batteries
    print("Total number of half empty batteries remaining in ports: ",
          total_half_bat)

    print("\n")
    print("Total number of batteries charged per port:")
    total_charged_bat = 0
    for value, port in port_dict.items():
        print(f"{port.name}: {port.total_charged}")
        total_charged_bat += port.total_charged
    print("Total number of batteries charged in ports: ", total_charged_bat)

    print("\n")
    print("Total number of containers entering each port:")
    total_input_con = 0
    for value, port in port_dict.items():
        print(f"{port.name}: {port.cargo_input}")
        total_input_con += port.cargo_input
    print("Total number of containers entered in ports: ", total_input_con)

    print("\n")
    print("Total number of containers leaving each port:")
    total_output_con = 0
    for value, port in port_dict.items():
        print(f"{port.name}: {port.cargo_output}")
        total_output_con += port.cargo_output
    print("Total number of containers left in ports: ", total_output_con)

    print("\n")
    print("Total number of containers handled per port:")
    total_containers = 0
    for value, port in port_dict.items():
        print(f"{port.name}: {port.cargo_input + port.cargo_output}")
        total_containers += port.cargo_input + port.cargo_output
    print("Total number of containers handled in ports: ", total_containers)

    print("\n")
    print(f"Total amount of hours held in port due to absence of batteries: "
          f"{zero_holdings}")


# Print results
results_printer()

