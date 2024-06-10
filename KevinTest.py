# ----- Import libraries -----
import salabim as sim
import numpy as np
import math

# ----- Import function -----
from PortFunctions import find_port_distance, get_port_delay

# ----- Create constants -----
container_time = 0.05  # [hr]
battery_capacity = 2000  # [kWh]
charging_time = 2  # [hr]
ship_battery_limit = 38  # [-]
additional_battery_number = 20  # [-]
battery_warning = ship_battery_limit  # [-]

# ----- Create simulation constants -----
sim_ship_number = 10  # [-]
sim_length = 2000  # [hr]


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
        self.battery_limit = ship_battery_limit  # Also assume 2 kWh per battery unit
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

            # Check if arrival port has a warning on it
            if self.current_port.warning_status:
                # Then load even more battery containers to compensate
                self.battery_limit = (ship_battery_limit
                                      + additional_battery_number)
            # If no warning exists
            else:
                # Then reset to nominal value
                self.battery_limit = ship_battery_limit

            # Load battery containers
            self.hold(self.battery_limit * container_time)
            self.current_port.batteries -= self.battery_limit
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
            self.hold(get_port_delay())

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
    def setup(self):
        self.name = self.name()
        self.queue = sim.Queue(self.name)
        self.batteries = 100  # Assume 100 batteries in port to start
        self.empty_batteries = 0  # No empty batteries to start
        self.half_empty_batteries = 0  # No half empty batteries to start
        self.half_empty_charges = []  # No half empty batteries to start
        self.warning_status = False

    # Charging station, which is activated by the arrival of new batteries
    def charging_station(self):
        # Check for any half empty battery containers
        while len(self.half_empty_charges) > 0:
            # Charge said half empty battery container until it's full
            self.hold(self.half_empty_charges[0] * charging_time)

            # Remove battery from half empty list since it's charged
            del self.half_empty_charges[0]

            # Add now fully charged battery
            self.batteries += 1

        # Check for any empty batteries
        while self.empty_batteries > 0:
            # Charge a single battery at a time (for now)
            self.hold(charging_time)

            # Update the amount of empty batteries left
            self.empty_batteries -= 1

            # Add fully charged battery
            self.batteries += 1

        # Finally check if the battery warning threshold has been cleared
        if self.batteries > battery_warning and self.warning_status:
            # If so, then remove warning status
            self.warning_status = False

            # Add print for fun (and to check)
            print(f"Warning deactivated in the port of {self.name}.")

        # Passivate self to save resources - until more batteries arrive
        self.passivate()

    # Warning check after new batteries are loaded from port to ship
    def check_warning(self):
        # If battery warning threshold has been breached
        if self.batteries <= battery_warning:
            # Then add the warning status to the port
            self.warning_status = True

            # Add print for fun (and to check)
            print(f"Warning activated in the port of {self.name}!")

        # Passivate self to save resources - until more batteries are loaded
        self.passivate()



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
port_rotterdam = Port('Rotterdam')
port_antwerp = Port('Antwerp')
port_amsterdam = Port('Amsterdam')
port_duisburg = Port('Duisburg')
port_vlissingen = Port('Vlissingen')
port_paris = Port('Paris')
port_Liege = Port('Liege')
port_terneuzen = Port('Terneuzen')
port_moerdijk = Port('Moerdijk')
port_cologne = Port('Cologne')
port_mannheim = Port('Mannheim')
port_karlsruhe = Port('Karlsruhe')
port_louviere = Port('Louviere')
port_sittard = Port('Sittard')
port_velsen = Port('Velsen')
port_strasbourg = Port('Strasbourg')
port_dordrecht = Port('Dordrecht')
port_neuss = Port('Neuss')
port_ludwigshafen = Port('Ludwigshafen')
port_brussels = Port('Brussels')
port_delfzijl = Port('Delfzijl')

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

