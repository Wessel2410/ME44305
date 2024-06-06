# ----- Import libraries -----
import salabim as sim
import numpy as np

# ----- Import function -----
from PortDistances import find_port_distance

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
        self.length = 100
        self.speed = 15
        self.current_port = current_port
        self.current_port_string = current_port_string
        self.destination_port = destination_port
        self.destination_port_string = destination_port_string

    def process(self):
        while True:
            # Leave the current port's queue if it's in one
            if self in self.current_port.queue:
                self.leave(self.current_port.queue)

            # Find port distance
            distance = find_port_distance(self.current_port_string,
                                          self.destination_port_string)

            # Calculate voyage duration
            duration = distance / self.speed * 60

            # Start holding for the duration
            self.hold(duration)

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


class Port(sim.Component):
    """
    Instance of a port, with a name and accompanying queue.
    """
    def setup(self):
        self.name = self.name()
        self.queue = sim.Queue(self.name)


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
env = sim.Environment(trace=True)

# Create a certain number of ships using the Ship Generator
ShipGenerator(amount_of_ships=10)

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
env.run(till=1000)

